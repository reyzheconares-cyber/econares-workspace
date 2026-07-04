#!/usr/bin/env python3
"""
ECONARES — Stale Deal Detector (v2)

What it does:
  Scans open deals in the ECONARES Sales Pipeline. Produces two reports:

  1. STALE DEALS — open deals with engagement activity logged but no touch
     in N+ days (default 14). Drafts a 2-line re-engagement note per deal.

  2. UNTOUCHED QUEUE — open deals with NO engagement ever logged
     (no notes_last_contacted, no email reply, no meeting). These are
     staged-but-unworked. The highest-value next-action: research the
     contact and draft first-touch outreach.

Critical rules:
  - READ-ONLY. Never mutates the CRM. RZH reviews drafts and sends manually.
  - Owner ID 164168266 (RZH) — 90091659 is DEAD, never reference it.
  - Staleness signal = MAX of notes_last_contacted, notes_last_updated,
    hs_notes_last_activity, engagements_last_meeting_booked,
    hs_latest_sales_email_*_date, hs_latest_meeting_activity.
  - Untouched = NONE of those activity fields populated (even if
    hs_lastmodifieddate is recent from a batch import).

CLI:
  python3 hubspot_stale_deals.py                          # JSON only, default 14d
  python3 hubspot_stale_deals.py --days 30                # raise stale threshold
  python3 hubspot_stale_deals.py --min-amount 1000000     # PHP1M+ only
  python3 hubspot_stale_deals.py --report                 # print Telegram report
  python3 hubspot_stale_deals.py --owner-only             # RZH-owned deals only
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# === Constants ===
RZH_OWNER_ID = "164168266"  # ACTIVE RZH account. 90091659 is DEAD.

STAGE_LABELS = {
    "3410654912": "Lead Generated",
    "3410654913": "Initial Contact",
    "3410654914": "Needs Analysis",
    "3410654915": "Proposal Sent",
    "3410654916": "Negotiation",
    "closedwon": "Closed Won",
    "closedlost": "Closed Lost",
}

# Parent-group exclusion map (verified 2026-07-04, per
# econares-crm-and-outreach-operations skill).
# If a PARENT GROUP has an OPEN deal in the portal, its subsidiaries are
# excluded from new outreach — they go through the existing deal channel only.
PARENT_GROUPS = {
    "MGEN / Meralco PowerGen": {
        "subsidiaries": ["CEDC", "Global Business Power", "GBP", "Meralco PowerGen",
                         "Toledo Power", "Redondo", "SPPC"],
        "parent_keywords": ["MGEN", "Meralco"],
    },
    "AboitizPower": {
        "subsidiaries": ["Therma Visayas", "Therma South", "TSI", "Therma Marine",
                         "Therma Subic", "Hedcor", "AP Renewables", "Aboitiz Power",
                         "SN Aboitiz", "Aboitiz", "PTC", "Philippine Hydro"],
        "parent_keywords": ["Aboitiz"],
    },
    "SMC Global Power": {
        "subsidiaries": ["Limay", "Mariveles", "Malita", "Sarangani", "SMC",
                         "San Miguel Power", "SMCGP", "SMC Power"],
        "parent_keywords": ["SMC", "San Miguel"],
    },
    "GNPower": {
        "subsidiaries": ["GNPower", "Dinginin", "Kauswagan", "GN Power"],
        "parent_keywords": ["GNPower", "GN Power"],
    },
    "SPC Power Group": {
        "subsidiaries": ["Panay Energy", "PEDC", "SPC Power", "Naga", "SPC"],
        "parent_keywords": ["SPC", "Panay Energy"],
    },
    "Holcim Philippines": {
        "subsidiaries": ["Holcim", "La Union", "Bulacan", "Lugait", "Davao",
                         "Holcim Philippines"],
        "parent_keywords": ["Holcim"],
    },
    "Republic Cement": {
        "subsidiaries": ["Republic Cement", "RCMI", "Danao", "Teresa",
                         "Republic", "Republic Cement Norzagaray"],
        "parent_keywords": ["Republic Cement", "Republic"],
    },
    "PCPC / Jin Navitas": {
        "subsidiaries": ["Palm Concepcion", "PCPC", "Iloilo CFBC",
                         "Jin Navitas"],
        "parent_keywords": ["PCPC", "Palm Concepcion", "Jin Navitas"],
    },
}


def detect_parent_group(deal_name, company_name=""):
    """Return parent group name if deal/company matches a known subsidiary.
    Returns None if no match. Case-insensitive substring on deal+company."""
    text = f"{deal_name or ''} {company_name or ''}".lower()
    for parent, info in PARENT_GROUPS.items():
        for kw in info["subsidiaries"]:
            if kw.lower() in text:
                return parent
    return None


ACTIVITY_PROPS = [
    "notes_last_contacted",
    "notes_last_updated",
    "hs_notes_last_activity",
    "engagements_last_meeting_booked",
    "hs_latest_sales_email_reply_date",
    "hs_latest_sales_email_click_date",
    "hs_latest_sales_email_open_date",
    "hs_latest_meeting_activity",
]

# Re-engagement note templates per stage. DETERMINISTIC, no LLM cost.
# REVIEW-FIRST. NEVER AUTO-SEND. DRAFTS for RZH to edit + send manually.
TEMPLATES = {
    "3410654912": "Hi {first}, quick check-in on whether {company}'s procurement timeline for {commodity} has firmed up. Open to a 10-min call this week. — RZH",
    "3410654913": "Hi {first}, circling back on the {commodity} conversation from a few weeks back. Any update on your end, or should I send a refreshed rate sheet? — RZH",
    "3410654914": "Hi {first}, checking in on the {commodity} requirements we walked through. Have scope and timing firmed up? I can have a draft proposal over by Friday. — RZH",
    "3410654915": "Hi {first}, did the {commodity} proposal land OK on your side? Happy to walk through pricing on a quick call, or adjust the spec if anything shifted. — RZH",
    "3410654916": "Hi {first}, still keen to land the {commodity} supply with {company}. Any sticking points I can help clear to get this over the line? — RZH",
}

DEAL_PROPERTIES = [
    "dealname", "dealstage", "amount", "deal_currency_code", "closedate",
    "createdate", "hs_createdate", "hubspot_owner_id",
    "hs_lastmodifieddate",
    "notes_last_contacted", "notes_last_updated", "hs_notes_last_activity",
    "engagements_last_meeting_booked",
    "hs_latest_sales_email_reply_date",
    "hs_latest_sales_email_open_date", "hs_latest_sales_email_click_date",
    "hs_latest_meeting_activity",
]


# === Token loading ===
def _token():
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if re.match(r"\s*(export\s+)?HUBSPOT_ACCESS_TOKEN\s*=", line):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env")


# === HTTP helper ===
def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


# === Date parsing ===
def parse_iso(s):
    if not s:
        return None
    s = s.strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def has_any_activity(props):
    """True if ANY of the activity timestamp fields are populated."""
    return any((props.get(p) or "").strip() for p in ACTIVITY_PROPS)


def last_activity_ts(props):
    """MAX of all activity timestamp fields (UTC aware)."""
    cands = []
    for prop in ACTIVITY_PROPS:
        v = parse_iso(props.get(prop))
        if v is not None:
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            cands.append(v)
    return max(cands) if cands else None


# === Deal fetching (paginated GET — search POST has IN-operator bugs) ===
def fetch_open_deals():
    deals, after = [], None
    while True:
        url = ("https://api.hubapi.com/crm/v3/objects/deals"
               f"?limit=100&properties={','.join(DEAL_PROPERTIES)}")
        if after:
            url += f"&after={after}"
        c, body = http("GET", url)
        if c != 200:
            raise SystemExit(f"Deals fetch failed: HTTP {c} {str(body)[:200]}")
        for d in body.get("results", []):
            if d["properties"].get("dealstage") not in ("closedlost", "closedwon"):
                deals.append(d)
        paging = body.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return deals


def fetch_deal_contacts(deal_id):
    c, body = http(
        "GET",
        f"https://api.hubapi.com/crm/v4/objects/deals/{deal_id}/associations/contacts",
    )
    if c != 200:
        return []
    out = []
    for r in body.get("results", []):
        cid = r.get("toObjectId") or r.get("id")
        if cid:
            out.append(str(cid))
    return out


def fetch_contact(cid):
    c, body = http(
        "GET",
        f"https://api.hubapi.com/crm/v3/objects/contacts/{cid}"
        "?properties=firstname,lastname,email,jobtitle,phone",
    )
    if c != 200:
        return None
    return body.get("properties", {}) if isinstance(body, dict) else None


def parse_deal_name(name):
    """Extract (company, commodity) from 'Bulk Ore Limited - Nickel Ore Supply'."""
    if not name:
        return ("?", "commodity")
    parts = [p.strip() for p in name.split(" - ")]
    if len(parts) >= 2:
        company = parts[0]
        last = parts[-1]
        commodity = re.sub(r"\s+(Supply|Inquiry|Pilot|Quote|Proposal)$", "", last, flags=re.IGNORECASE)
        return (company, commodity or last)
    return (name, "commodity")


# === Report formatter ===
def format_deal_line(r):
    amt = r.get("amount_php")
    cur = r.get("currency") or "PHP"
    if amt and amt > 0:
        amt_str = f"${amt:,.0f}" if cur == "USD" else f"₱{amt:,.0f}"
    else:
        amt_str = "amt n/a"
    contact = r.get("contact_name") or "no contact"
    return (f"  • {r['deal_name']} | {amt_str} | {r['stage_label']} | "
            f"{r['days_stale']}d | {contact}")


def format_untouched_line(u):
    amt = u.get("amount_php")
    cur = u.get("currency") or "PHP"
    if amt and amt > 0:
        amt_str = f"${amt:,.0f}" if cur == "USD" else f"₱{amt:,.0f}"
    else:
        amt_str = "amt n/a"
    return (f"  • {u['deal_name']} | {amt_str} | {u['stage_label']} | "
            f"created {u.get('days_since_create','?')}d ago | {u['commodity']}")


def format_report(stale, untouched, threshold_days, now):
    buckets = {"14-30d": [], "30-60d": [], "60-90d": [], "90+d": []}
    for r in stale:
        d = r["days_stale"]
        if d <= 30:
            buckets["14-30d"].append(r)
        elif d <= 60:
            buckets["30-60d"].append(r)
        elif d <= 90:
            buckets["60-90d"].append(r)
        else:
            buckets["90+d"].append(r)

    L = []
    L.append(f"STALE + UNTOUCHED DEAL REPORT — {now.strftime('%a %b %d, %Y')}")
    L.append(f"Stale threshold: {threshold_days}+ days since last engagement")
    L.append("")

    L.append("=== SUMMARY ===")
    L.append(f"  Stale (engagement-logged, >{threshold_days}d):    {len(stale)}")
    L.append(f"  Untouched (NO engagement ever logged): {len(untouched)}")
    L.append("")

    # === STALE SECTION ===
    if stale:
        L.append("=== STALE DEALS (re-engage candidates) ===")
        L.append("Buckets by days since last activity:")
        L.append(f"  14-30d:  {len(buckets['14-30d'])}")
        L.append(f"  30-60d:  {len(buckets['30-60d'])}")
        L.append(f"  60-90d:  {len(buckets['60-90d'])}")
        L.append(f"  90+d:    {len(buckets['90+d'])}")
        L.append("")
        for bucket_name in ("90+d", "60-90d", "30-60d", "14-30d"):
            bucket = buckets[bucket_name]
            if not bucket:
                continue
            L.append(f"  --- {bucket_name.upper()} ({len(bucket)}) ---")
            bucket.sort(key=lambda r: r.get("amount_php") or 0, reverse=True)
            for r in bucket[:8]:
                L.append(format_deal_line(r))
            if len(bucket) > 8:
                L.append(f"  ... +{len(bucket) - 8} more in JSON")
            L.append("")

        L.append("=== DRAFTED RE-ENGAGEMENT NOTES (REVIEW-FIRST — never auto-send) ===")
        top5 = sorted(stale, key=lambda x: -(x.get("amount_php") or 0))[:5]
        for r in top5:
            L.append("")
            L.append(f"  → {r['deal_name']} ({r['days_stale']}d stale, {r['stage_label']})")
            L.append(f"    TO: {r.get('contact_name') or '?'} <{r.get('contact_email') or '?'}>")
            L.append(f"    BODY: {r['draft_note']}")
        L.append("")
    else:
        L.append("=== STALE DEALS ===")
        L.append("  None. All engagement-active deals are fresh.")
        L.append("")

    # === UNTOUCHED SECTION ===
    if untouched:
        actionable = [u for u in untouched if not u.get("parent_excluded")]
        excluded = [u for u in untouched if u.get("parent_excluded")]
        L.append(f"=== UNTOUCHED QUEUE ({len(untouched)} total) ===")
        L.append(f"  Actionable (no parent-group exclusion): {len(actionable)}")
        L.append(f"  Excluded (parent group has live deal):   {len(excluded)}")
        L.append("")
        L.append("These deals have NO engagement activity logged (no notes,")
        L.append("emails, or meetings). They were likely batch-imported or")
        L.append("created manually but no outreach has happened yet.")
        L.append("Highest-value next-action: research contact + draft first touch.")
        L.append("")

        if actionable:
            L.append(f"--- ACTIONABLE ({len(actionable)}) ---")
            actionable_sorted = sorted(actionable, key=lambda u: -(u.get("amount_php") or 0))
            for u in actionable_sorted[:10]:
                L.append(format_untouched_line(u))
            if len(actionable) > 10:
                L.append(f"  ... +{len(actionable) - 10} more in JSON")
            L.append("")

        if excluded:
            L.append(f"--- EXCLUDED — parent group has live deal ({len(excluded)}) ---")
            excluded_sorted = sorted(excluded, key=lambda u: u.get("parent_group", ""))
            for u in excluded_sorted[:10]:
                L.append(format_untouched_line(u))
                if u.get("parent_group"):
                    L.append(f"      parent: {u['parent_group']} (active deal exists)")
            if len(excluded) > 10:
                L.append(f"  ... +{len(excluded) - 10} more in JSON")
            L.append("")

    L.append("=== NEXT ACTIONS ===")
    L.append(f"  Stale ({len(stale)}): review drafted re-engagement notes; confirm 'let's go' to send")
    L.append(f"  Untouched ({len(untouched)}): request first-touch research + draft for batch")
    L.append("")
    L.append("Full JSON snapshot saved (audit trail).")

    return "\n".join(L)


# === Main ===
def main():
    ap = argparse.ArgumentParser(description="ECONARES stale + untouched deal detector")
    ap.add_argument("--days", type=int, default=14,
                    help="Stale threshold in days (default 14)")
    ap.add_argument("--min-amount", type=float, default=0,
                    help="Min deal amount in PHP (default 0 = no filter)")
    ap.add_argument("--owner-only", action="store_true",
                    help="Only flag deals owned by RZH (164168266)")
    ap.add_argument("--out", type=str, default=None,
                    help="JSON output path")
    ap.add_argument("--report", action="store_true",
                    help="Print Telegram-format report to stdout")
    args = ap.parse_args()

    print(f"[FETCH] Loading open deals from ECONARES pipeline ...", file=sys.stderr)
    deals = fetch_open_deals()
    print(f"[FETCH] {len(deals)} open deals", file=sys.stderr)

    # === Build live parent-group exclusion set ===
    # If a parent group name appears in any open deal name, treat that group as
    # having a live deal → all its subsidiaries are EXCLUDED from outreach.
    parents_with_open_deals = set()
    for d in deals:
        parent = detect_parent_group(d["properties"].get("dealname", ""))
        if parent:
            parents_with_open_deals.add(parent)
    print(f"[EXCL] Parent groups with live open deals: {sorted(parents_with_open_deals)}", file=sys.stderr)

    now = datetime.now(timezone.utc)
    stale = []
    untouched = []
    skipped_owner = 0
    skipped_amount = 0

    for d in deals:
        props = d["properties"]
        owner = props.get("hubspot_owner_id")
        if args.owner_only and owner != RZH_OWNER_ID:
            skipped_owner += 1
            continue

        any_activity = has_any_activity(props)
        last_act = last_activity_ts(props) if any_activity else None
        last_mod = parse_iso(props.get("hs_lastmodifieddate"))
        if last_mod and last_mod.tzinfo is None:
            last_mod = last_mod.replace(tzinfo=timezone.utc)
        created_iso = props.get("createdate") or props.get("hs_createdate")
        created_dt = parse_iso(created_iso)
        if created_dt and created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=timezone.utc)

        company, commodity = parse_deal_name(props.get("dealname"))
        amount_str = props.get("amount")
        amount = float(amount_str) if amount_str else 0
        stage_id = props.get("dealstage", "")
        stage_label = STAGE_LABELS.get(stage_id, stage_id)
        days_since_create = (now - created_dt).days if created_dt else 0

        # === UNTOUCHED branch: no engagement ever logged ===
        if not any_activity:
            parent_group = detect_parent_group(props.get("dealname", ""), company)
            parent_excluded = parent_group in parents_with_open_deals
            untouched.append({
                "deal_id": d["id"],
                "deal_name": props.get("dealname"),
                "stage_id": stage_id,
                "stage_label": stage_label,
                "amount_php": amount if amount else None,
                "currency": props.get("deal_currency_code"),
                "closedate": props.get("closedate"),
                "createdate": created_iso,
                "days_since_create": days_since_create,
                "last_modified": props.get("hs_lastmodifieddate"),
                "owner_id": owner,
                "commodity": commodity,
                "company": company,
                "parent_group": parent_group,
                "parent_excluded": parent_excluded,
            })
            continue

        # === STALE branch: has engagement, but too old ===
        if last_act:
            days_stale = (now - last_act).days
        elif last_mod:
            days_stale = (now - last_mod).days
        elif created_dt:
            days_stale = (now - created_dt).days
        else:
            days_stale = 9999

        if days_stale < args.days:
            continue
        if amount < args.min_amount:
            skipped_amount += 1
            continue

        # Fetch primary contact for the re-engagement draft
        contact_ids = fetch_deal_contacts(d["id"])
        contact_name = None
        contact_email = None
        first_name = "there"
        if contact_ids:
            cp = fetch_contact(contact_ids[0])
            if cp:
                first = (cp.get("firstname") or "").strip()
                last = (cp.get("lastname") or "").strip()
                if first or last:
                    contact_name = f"{first} {last}".strip()
                contact_email = cp.get("email")
                if first:
                    first_name = first

        template = TEMPLATES.get(stage_id, TEMPLATES["3410654913"])
        draft = template.format(first=first_name, company=company, commodity=commodity)

        parent_group = detect_parent_group(props.get("dealname", ""), company)
        parent_excluded = parent_group in parents_with_open_deals

        stale.append({
            "deal_id": d["id"],
            "deal_name": props.get("dealname"),
            "stage_id": stage_id,
            "stage_label": stage_label,
            "amount_php": amount if amount else None,
            "currency": props.get("deal_currency_code"),
            "closedate": props.get("closedate"),
            "createdate": created_iso,
            "last_activity": last_act.isoformat() if last_act else None,
            "days_stale": days_stale,
            "owner_id": owner,
            "contact_id": contact_ids[0] if contact_ids else None,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "commodity": commodity,
            "company": company,
            "parent_group": parent_group,
            "parent_excluded": parent_excluded,
            "draft_note": draft,
        })

    out_path = args.out or os.path.expanduser(
        f"~/ECONARES_WORKSPACE/intelligence/stale_deals/"
        f"stale_deals_{now.strftime('%Y-%m-%d')}.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    actionable_untouched = [u for u in untouched if not u.get("parent_excluded")]
    excluded_untouched = [u for u in untouched if u.get("parent_excluded")]
    snapshot = {
        "generated_at": now.isoformat(),
        "threshold_days": args.days,
        "min_amount_php": args.min_amount,
        "owner_only": args.owner_only,
        "open_deals_scanned": len(deals),
        "skipped_owner_mismatch": skipped_owner,
        "skipped_below_amount": skipped_amount,
        "parents_with_open_deals": sorted(parents_with_open_deals),
        "stale_count": len(stale),
        "untouched_count": len(untouched),
        "actionable_untouched_count": len(actionable_untouched),
        "excluded_untouched_count": len(excluded_untouched),
        "stale": stale,
        "untouched": untouched,
    }
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"[SAVE] {out_path}", file=sys.stderr)
    print(f"[RESULT] {len(stale)} stale + {len(untouched)} untouched "
          f"(stale threshold >{args.days}d, "
          f"{'RZH-owned' if args.owner_only else 'all owners'}, "
          f"{len(actionable_untouched)} actionable / "
          f"{len(excluded_untouched)} parent-excluded)",
          file=sys.stderr)

    if args.report:
        print("\n" + "=" * 60)
        print(format_report(stale, untouched, args.days, now))

    return 0


if __name__ == "__main__":
    sys.exit(main())
