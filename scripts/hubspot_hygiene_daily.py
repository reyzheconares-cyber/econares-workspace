#!/usr/bin/env python3
"""
ECONARES — Daily CRM & Data Hygiene (v1)

Five-stage daily hygiene check on the ECONARES HubSpot portal (245683432).
Each stage is READ-ONLY and produces a review-first report. RZH reviews
output and decides what to mutate manually.

Stages:
  1. DEDUP          Find duplicate companies (by domain), contacts (by email)
  2. COMMODITY TAG  Surface which contacts NEED commodity tags based on
                    their associated deals (no auto-apply — requires schema)
  3. LEAD RE-SCORE  Categorize OPEN/IN_PROGRESS leads by recent activity
                    (hot/warm/cold) using Notes as the activity signal
  4. DEAD THREADS   Find outreach that has gone silent (>60d) via:
                    4a. HubSpot: contacts with OPEN/IN_PROGRESS + no notes in 60d
                    4b. Gmail IMAP: outbound threads with no reply in 60d
  5. BACKFILL       Surface contacts/companies/deals missing critical fields

CLI:
  python3 hubspot_hygiene_daily.py                     # all 5 stages, JSON only
  python3 hubspot_hygiene_daily.py --digest            # JSON + Telegram digest
  python3 hubspot_hygiene_daily.py --stages 1,3,5      # subset
  python3 hubspot_hygiene_daily.py --owner-only        # only RZH-owned (164168266)
"""
import argparse
import base64
import imaplib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.utils import parsedate_to_datetime

# === Constants ===
RZH_OWNER_ID = "164168266"  # ACTIVE. 90091659 is DEAD.

# ECONARES portal — known activity signal: NOTES (not task completions).
# Per skill: "ECONARES logs outreach as Notes associated with contacts."
ACTIVITY_LOOKBACK_DAYS = 30
STALE_THRESHOLD_DAYS = 60

# =====================================================================
# Token + HTTP
# =====================================================================
def _token():
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if re.match(r"\s*(export\s+)?HUBSPOT_ACCESS_TOKEN\s*=", line):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env")


def _gmail_password():
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if re.match(r"\s*(export\s+)?GMAIL_APP_PASSWORD\s*=", line):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


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


def paginated_get(object_type, properties, extra_qs=""):
    """Paginated GET /crm/v3/objects/{type}?limit=100&properties=..."""
    items, after = [], None
    while True:
        url = f"https://api.hubapi.com/crm/v3/objects/{object_type}?limit=100&properties={','.join(properties)}"
        if extra_qs:
            url += f"&{extra_qs}"
        if after:
            url += f"&after={after}"
        c, body = http("GET", url)
        if c != 200:
            raise SystemExit(f"{object_type} fetch failed: HTTP {c} {str(body)[:200]}")
        items.extend(body.get("results", []))
        paging = body.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return items


def paginated_search(object_type, filter_groups, properties, limit=100):
    items, after = [], None
    while True:
        body_q = {"filterGroups": filter_groups, "properties": properties, "limit": limit}
        if after:
            body_q["after"] = after
        c, body = http("POST", f"https://api.hubapi.com/crm/v3/objects/{object_type}/search", body_q)
        if c != 200:
            break
        items.extend(body.get("results", []))
        paging = body.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return items


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


def days_since(iso_str, now):
    dt = parse_iso(iso_str)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days


# =====================================================================
# STAGE 1: DEDUP
# =====================================================================
def stage1_dedup():
    """Find duplicate companies (domain) + duplicate contacts (email).
    READ-ONLY — RZH reviews and merges manually."""
    # Companies by domain
    companies = paginated_get("companies", ["name", "domain", "industry", "city", "country"])
    by_domain = defaultdict(list)
    for co in companies:
        d = (co["properties"].get("domain") or "").strip().lower()
        if d:
            by_domain[d].append({"id": co["id"], "name": co["properties"].get("name"),
                                 "city": co["properties"].get("city")})
    dup_companies = [{"domain": d, "companies": cs} for d, cs in by_domain.items() if len(cs) > 1]

    # Contacts by email
    contacts = paginated_get("contacts",
                             ["firstname", "lastname", "email", "company", "hs_lead_status"])
    by_email = defaultdict(list)
    for ct in contacts:
        e = (ct["properties"].get("email") or "").strip().lower()
        if e:
            by_email[e].append({"id": ct["id"], "name": f"{ct['properties'].get('firstname','')} {ct['properties'].get('lastname','')}".strip(),
                                "company": ct["properties"].get("company"),
                                "lead_status": ct["properties"].get("hs_lead_status")})
    dup_contacts = [{"email": e, "contacts": cs} for e, cs in by_email.items() if len(cs) > 1]

    # Companies with no domain (informational — easy fix opportunity)
    no_domain = [{"id": c["id"], "name": c["properties"].get("name")}
                 for c in companies if not (c["properties"].get("domain") or "").strip()]

    return {
        "stage": "dedup",
        "summary": {
            "duplicate_companies": len(dup_companies),
            "duplicate_contacts": len(dup_contacts),
            "companies_missing_domain": len(no_domain),
        },
        "duplicate_companies": dup_companies[:20],
        "duplicate_contacts": dup_contacts[:20],
        "companies_missing_domain": no_domain[:20],
    }


# =====================================================================
# STAGE 2: COMMODITY TAG (analysis only — no auto-apply)
# =====================================================================
COMMODITY_KEYWORDS = {
    "nickel": ["nickel", "ni ore", "laterite", "saprolite"],
    "copper": ["copper", "cu ore", "concentrate"],
    "coal": ["coal", "thermal coal", "coke breeze", "steam coal"],
    "diesel": ["diesel", "fuel oil", "bunker"],
    "pks": ["palm kernel shell", "pks"],
    "woodchips": ["woodchip", "wood chip", "acacia"],
    "cpo": ["crude palm oil", "cpo"],
}


def detect_commodity(text):
    if not text:
        return None
    t = text.lower()
    for commodity, kws in COMMODITY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return commodity
    return None


def stage2_commodity_tag():
    """For each contact: derive intended commodity tag from associated deals.
    Output: plan + counts. No auto-apply (requires custom property creation)."""
    # Fetch all open deals + their commodity signal
    deals = paginated_get("deals", ["dealname", "dealstage", "amount"])
    open_deals = [d for d in deals if d["properties"].get("dealstage") not in ("closedlost", "closedwon")]
    deal_commodity = {}
    deal_to_contacts = defaultdict(list)
    for d in open_deals:
        comm = detect_commodity(d["properties"].get("dealname"))
        if comm:
            deal_commodity[d["id"]] = comm
        # Get associated contacts
        c, body = http("GET", f"https://api.hubapi.com/crm/v4/objects/deals/{d['id']}/associations/contacts")
        if c == 200:
            for r in body.get("results", []):
                cid = str(r.get("toObjectId") or r.get("id"))
                if cid:
                    deal_to_contacts[d["id"]].append(cid)

    # Aggregate per-contact commodities
    contact_commodities = defaultdict(set)
    for did, contacts in deal_to_contacts.items():
        comm = deal_commodity.get(did)
        if not comm:
            continue
        for cid in contacts:
            contact_commodities[cid].add(comm)

    # All contacts
    contacts = paginated_get("contacts", ["firstname", "lastname", "email", "company"])
    contact_map = {c["id"]: c["properties"] for c in contacts}

    tagged = []
    untagged = []
    for cid, props in contact_map.items():
        if not (props.get("email") or "").strip():
            continue
        name = f"{props.get('firstname','')} {props.get('lastname','')}".strip() or "?"
        record = {"id": cid, "name": name, "email": props.get("email"),
                  "company": props.get("company")}
        if cid in contact_commodities:
            record["commodities"] = sorted(contact_commodities[cid])
            tagged.append(record)
        else:
            untagged.append(record)

    return {
        "stage": "commodity_tag",
        "summary": {
            "contacts_with_commodity_signal": len(tagged),
            "contacts_needing_research": len(untagged),
            "open_deals_analyzed": len(open_deals),
            "open_deals_with_commodity_signal": len(deal_commodity),
        },
        "schema_note": "No 'econares_commodity_interest' property exists yet. "
                       "Surface this plan to RZH before applying (requires admin).",
        "tagged_preview": tagged[:15],
        "untagged_preview": untagged[:15],
    }


# =====================================================================
# STAGE 3: LEAD RE-SCORE (RFM-lite, Notes as activity signal)
# =====================================================================
def stage3_lead_rescore():
    """Categorize OPEN/IN_PROGRESS leads by recent note activity.
    hot=3+ notes in 30d, warm=1-2, cold=0, stale=no notes in 60+d."""
    now = datetime.now(timezone.utc)
    lookback_start = now - timedelta(days=ACTIVITY_LOOKBACK_DAYS)

    # Fetch all OPEN + IN_PROGRESS leads
    leads = []
    for status in ("OPEN", "IN_PROGRESS"):
        leads.extend(paginated_search("contacts",
            [{"filters": [
                {"propertyName": "hs_lead_status", "operator": "EQ", "value": status},
                {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": RZH_OWNER_ID},
            ]}],
            ["firstname", "lastname", "email", "company", "hs_lead_status", "econares_last_outreach_date"]))

    # Per-lead note counts in lookback window
    # Use search endpoint with createdate filter
    notes_recent = paginated_search("notes",
        [{"filters": [
            {"propertyName": "createdate", "operator": "GTE",
             "value": lookback_start.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
        ]}],
        ["hs_note_body", "createdate"], limit=100)

    # Map contact_id -> count of recent notes
    notes_per_contact = Counter()
    last_note_per_contact = {}
    for n in notes_recent:
        # Get associations
        c, body = http("GET", f"https://api.hubapi.com/crm/v4/objects/notes/{n['id']}/associations/contacts")
        if c == 200:
            for r in body.get("results", []):
                cid = str(r.get("toObjectId") or r.get("id"))
                if cid:
                    notes_per_contact[cid] += 1
                    ts = parse_iso(n["properties"].get("createdate"))
                    if ts and (cid not in last_note_per_contact or ts > last_note_per_contact[cid]):
                        last_note_per_contact[cid] = ts

    hot, warm, cold = [], [], []
    for lead in leads:
        cid = lead["id"]
        n_recent = notes_per_contact.get(cid, 0)
        last_outreach = lead["properties"].get("econares_last_outreach_date")
        days_since_outreach = days_since(last_outreach, now)
        record = {
            "id": cid,
            "name": f"{lead['properties'].get('firstname','')} {lead['properties'].get('lastname','')}".strip(),
            "company": lead["properties"].get("company"),
            "email": lead["properties"].get("email"),
            "lead_status": lead["properties"].get("hs_lead_status"),
            "notes_last_30d": n_recent,
            "last_outreach_days_ago": days_since_outreach,
        }
        if n_recent >= 3:
            hot.append(record)
        elif n_recent >= 1:
            warm.append(record)
        else:
            cold.append(record)

    return {
        "stage": "lead_rescore",
        "summary": {
            "open_in_progress_leads": len(leads),
            "hot_3plus_notes_30d": len(hot),
            "warm_1to2_notes_30d": len(warm),
            "cold_0_notes_30d": len(cold),
        },
        "hot_preview": hot[:10],
        "warm_preview": warm[:10],
        "cold_preview": cold[:10],
    }


# =====================================================================
# STAGE 4: DEAD THREADS (HubSpot + optional Gmail IMAP)
# =====================================================================
def stage4_dead_threads():
    """Find outreach that has gone silent. Two sub-stages:
    4a. HubSpot: OPEN/IN_PROGRESS leads with no notes in 60+d
    4b. Gmail IMAP: outbound threads with no inbound reply in 60+d
    """
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=STALE_THRESHOLD_DAYS)

    # 4a. HubSpot stale leads
    stale_leads = paginated_search("contacts",
        [{"filters": [
            {"propertyName": "hs_lead_status", "operator": "IN", "value": "OPEN,IN_PROGRESS"},
            {"propertyName": "econares_last_outreach_date", "operator": "LT",
             "value": stale_cutoff.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": RZH_OWNER_ID},
        ]}],
        ["firstname", "lastname", "email", "company", "hs_lead_status", "econares_last_outreach_date"])

    hs_stale = []
    for sl in stale_leads:
        p = sl["properties"]
        hs_stale.append({
            "id": sl["id"],
            "name": f"{p.get('firstname','')} {p.get('lastname','')}".strip(),
            "company": p.get("company"),
            "email": p.get("email"),
            "lead_status": p.get("hs_lead_status"),
            "last_outreach": p.get("econares_last_outreach_date"),
            "days_silent": days_since(p.get("econares_last_outreach_date"), now),
        })

    # 4b. Gmail IMAP — try; graceful failure
    imap_stale = []
    imap_error = None
    pw = _gmail_password()
    if not pw:
        imap_error = "GMAIL_APP_PASSWORD not set in ~/.hermes/.env"
    else:
        try:
            imap_stale = _imap_fetch_stale_threads(pw, stale_cutoff, now)
        except Exception as e:
            imap_error = f"IMAP error: {type(e).__name__}: {str(e)[:200]}"

    return {
        "stage": "dead_threads",
        "summary": {
            "hubspot_stale_leads": len(hs_stale),
            "gmail_stale_threads": len(imap_stale),
            "gmail_imap_status": "ok" if not imap_error else f"error: {imap_error[:80]}",
        },
        "hubspot_stale": hs_stale[:20],
        "gmail_stale": imap_stale[:20],
    }


def _imap_fetch_stale_threads(password, cutoff, now):
    """Connect to Gmail IMAP and find outbound threads with no inbound in 60+d."""
    stale = []
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("reyzh.econares@gmail.com", password)
    imap.select("INBOX")
    cutoff_str = cutoff.strftime("%d-%b-%Y")

    # Search SENT folder for threads older than cutoff
    typ, data = imap.select('"[Gmail]/Sent Mail"')
    if typ != "OK":
        imap.logout()
        return stale
    typ, msg_ids = imap.search(None, f'(SINCE {cutoff_str})')
    if typ != "OK" or not msg_ids[0]:
        imap.logout()
        return stale

    # Sample most recent 100 to avoid huge scans
    ids = msg_ids[0].split()[-100:]
    for mid in ids:
        typ, msg_data = imap.fetch(mid, "(RFC822.HEADER X-GM-THRID)")
        if typ != "OK":
            continue
        raw = msg_data[0][1]
        msg = message_from_bytes(raw)
        thr_id_match = re.search(rb"X-GM-THRID (\d+)", msg_data[0][0])
        if not thr_id_match:
            continue
        thr_id = thr_id_match.group(1).decode()

        # Check INBOX for replies in this thread
        typ, _ = imap.search(None, f'(X-GM-THRID {thr_id})')
        if typ != "OK":
            continue
        # If we found the message in INBOX (not just SENT), it means there are
        # inbound replies. Skip — not stale.
        if msg_ids[0].count(mid) == 0:  # safety
            continue
        # A simpler proxy: if we got hits in INBOX for this thread ID,
        # we have inbound replies — skip
        # (this is approximate; IMAP X-GM-THRID in INBOX would tell us)
        # For now, only count threads we KNOW have NO inbound
        # Use a separate INBOX search
        typ2, inbox_hits = imap.select("INBOX")
        if typ2 == "OK":
            typ3, _ = imap.search(None, f'(X-GM-THRID {thr_id})')
            if typ3 == "OK" and _[0]:
                continue  # has inbound replies
        # Otherwise, flag as stale
        date_hdr = msg.get("Date")
        sent_at = None
        if date_hdr:
            try:
                sent_at = parsedate_to_datetime(date_hdr)
            except Exception:
                pass
        if sent_at and sent_at < cutoff:
            stale.append({
                "thread_id": thr_id,
                "subject": msg.get("Subject"),
                "to": msg.get("To"),
                "sent_at": sent_at.isoformat(),
                "days_silent": (now - sent_at).days if sent_at.tzinfo else None,
            })

    imap.logout()
    return stale


# =====================================================================
# STAGE 5: BACKFILL
# =====================================================================
def stage5_backfill():
    """Surface contacts/companies/deals missing critical fields."""
    now = datetime.now(timezone.utc)

    # Contacts missing key fields
    contact_missing = defaultdict(list)
    contact_fields = ["firstname", "lastname", "email", "phone", "company", "jobtitle", "country"]
    contacts = paginated_get("contacts",
        ["firstname", "lastname", "email", "phone", "company", "jobtitle", "country"])
    for c in contacts:
        p = c["properties"]
        name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or "?"
        for f in contact_fields:
            if not (p.get(f) or "").strip():
                contact_missing[f].append({"id": c["id"], "name": name,
                                           "email": p.get("email"),
                                           "company": p.get("company")})

    # Companies missing fields
    company_missing = defaultdict(list)
    company_fields = ["name", "domain", "industry", "country", "city", "numberofemployees"]
    companies = paginated_get("companies", company_fields)
    for c in companies:
        p = c["properties"]
        for f in company_fields:
            if not (p.get(f) or "").strip():
                company_missing[f].append({"id": c["id"], "name": p.get("name") or "?"})

    # Deals missing fields (open only)
    deal_missing = defaultdict(list)
    deals = paginated_get("deals", ["dealname", "dealstage", "amount", "closedate"])
    open_deals = [d for d in deals if d["properties"].get("dealstage") not in ("closedlost", "closedwon")]
    for d in open_deals:
        p = d["properties"]
        if not (p.get("amount") or "").strip():
            deal_missing["amount"].append({"id": d["id"], "name": p.get("dealname")})
        if not (p.get("closedate") or "").strip():
            deal_missing["closedate"].append({"id": d["id"], "name": p.get("dealname")})

    return {
        "stage": "backfill",
        "summary": {
            "contacts_scanned": len(contacts),
            "companies_scanned": len(companies),
            "open_deals_scanned": len(open_deals),
        },
        "contact_missing_counts": {k: len(v) for k, v in contact_missing.items()},
        "company_missing_counts": {k: len(v) for k, v in company_missing.items()},
        "deal_missing_counts": {k: len(v) for k, v in deal_missing.items()},
        "contact_missing_samples": {k: v[:5] for k, v in contact_missing.items()},
        "company_missing_samples": {k: v[:5] for k, v in company_missing.items()},
        "deal_missing_samples": {k: v[:5] for k, v in deal_missing.items()},
    }


# =====================================================================
# Telegram digest
# =====================================================================
def format_digest(results, threshold_days=60):
    L = []
    L.append(f"ECONARES DAILY HYGIENE — {datetime.now().strftime('%a %b %d, %Y')}")
    L.append(f"5-stage sweep across HubSpot portal 245683432")
    L.append("")

    if "dedup" in results:
        s = results["dedup"]["summary"]
        L.append(f"STAGE 1 — DEDUP")
        L.append(f"  Duplicate companies (shared domain): {s['duplicate_companies']}")
        L.append(f"  Duplicate contacts (shared email):   {s['duplicate_contacts']}")
        L.append(f"  Companies missing domain:            {s['companies_missing_domain']}")
        if s['duplicate_companies'] or s['duplicate_contacts']:
            L.append(f"  Action: review JSON, merge duplicates manually")
        L.append("")

    if "commodity_tag" in results:
        s = results["commodity_tag"]["summary"]
        L.append(f"STAGE 2 — COMMODITY TAGS")
        L.append(f"  Contacts with commodity signal: {s['contacts_with_commodity_signal']}")
        L.append(f"  Contacts needing research:      {s['contacts_needing_research']}")
        L.append(f"  Note: {results['commodity_tag']['schema_note']}")
        L.append("")

    if "lead_rescore" in results:
        s = results["lead_rescore"]["summary"]
        L.append(f"STAGE 3 — LEAD RE-SCORE (RZH-owned)")
        L.append(f"  HOT (3+ notes/30d): {s['hot_3plus_notes_30d']}")
        L.append(f"  WARM (1-2 notes/30d): {s['warm_1to2_notes_30d']}")
        L.append(f"  COLD (0 notes/30d): {s['cold_0_notes_30d']}")
        if s['hot_3plus_notes_30d']:
            L.append("  Top HOT leads (priority for follow-up):")
            for r in results["lead_rescore"].get("hot_preview", [])[:5]:
                L.append(f"    • {r['name']} @ {r.get('company') or '?'} ({r['notes_last_30d']} notes)")
        L.append("")

    if "dead_threads" in results:
        s = results["dead_threads"]["summary"]
        L.append(f"STAGE 4 — DEAD THREADS (>{threshold_days}d silent)")
        L.append(f"  HubSpot stale leads: {s['hubspot_stale_leads']}")
        L.append(f"  Gmail stale threads: {s['gmail_stale_threads']}")
        L.append(f"  Gmail IMAP: {s['gmail_imap_status']}")
        if s['hubspot_stale_leads']:
            L.append("  Top stale leads (re-engage or archive):")
            for r in results["dead_threads"].get("hubspot_stale", [])[:5]:
                L.append(f"    • {r['name']} @ {r.get('company') or '?'} "
                         f"({r['days_silent']}d silent, status={r['lead_status']})")
        L.append("")

    if "backfill" in results:
        s = results["backfill"]["summary"]
        L.append(f"STAGE 5 — BACKFILL (missing fields)")
        L.append(f"  Contacts scanned: {s['contacts_scanned']} | Companies: {s['companies_scanned']} | Open deals: {s['open_deals_scanned']}")
        c_miss = results["backfill"]["contact_missing_counts"]
        co_miss = results["backfill"]["company_missing_counts"]
        d_miss = results["backfill"]["deal_missing_counts"]
        if c_miss:
            L.append(f"  Contacts missing: {', '.join(f'{k}({v})' for k,v in c_miss.items() if v > 0)}")
        if co_miss:
            L.append(f"  Companies missing: {', '.join(f'{k}({v})' for k,v in co_miss.items() if v > 0)}")
        if d_miss:
            L.append(f"  Deals missing: {', '.join(f'{k}({v})' for k,v in d_miss.items() if v > 0)}")
        L.append("")

    L.append("NEXT ACTIONS")
    L.append("  • Review JSON snapshot for any stage with non-zero counts")
    L.append("  • Confirm 'let's go' on dedup merges or backfill updates")
    L.append("  • IMAP error? Check GMAIL_APP_PASSWORD in ~/.hermes/.env")
    return "\n".join(L)


# =====================================================================
# Main
# =====================================================================
def main():
    ap = argparse.ArgumentParser(description="ECONARES daily CRM hygiene")
    ap.add_argument("--digest", action="store_true", help="Print Telegram digest to stdout")
    ap.add_argument("--stages", type=str, default="1,2,3,4,5",
                    help="Comma-separated stage numbers (default 1,2,3,4,5)")
    ap.add_argument("--out", type=str, default=None, help="JSON output path")
    args = ap.parse_args()

    stages_to_run = set(int(s.strip()) for s in args.stages.split(",") if s.strip())
    print(f"[STAGES] Running: {sorted(stages_to_run)}", file=sys.stderr)

    results = {}
    stage_map = {
        1: ("dedup", stage1_dedup),
        2: ("commodity_tag", stage2_commodity_tag),
        3: ("lead_rescore", stage3_lead_rescore),
        4: ("dead_threads", stage4_dead_threads),
        5: ("backfill", stage5_backfill),
    }

    for n in sorted(stages_to_run):
        if n not in stage_map:
            continue
        name, fn = stage_map[n]
        try:
            print(f"[STAGE {n}] {name} ...", file=sys.stderr)
            results[name] = fn()
            print(f"[STAGE {n}] OK", file=sys.stderr)
        except Exception as e:
            results[name] = {"stage": name, "error": f"{type(e).__name__}: {str(e)[:300]}"}
            print(f"[STAGE {n}] ERROR: {e}", file=sys.stderr)

    out_path = args.out or os.path.expanduser(
        f"~/ECONARES_WORKSPACE/intelligence/hygiene/"
        f"hygiene_{datetime.now().strftime('%Y-%m-%d')}.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stages_run": sorted(stages_to_run),
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"[SAVE] {out_path}", file=sys.stderr)

    if args.digest:
        print("\n" + "=" * 60)
        print(format_digest(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
