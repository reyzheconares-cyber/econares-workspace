#!/usr/bin/env python
"""
apply_audit_fixes.py
====================
Apply the 3 concrete fixes from the HubSpot duplicate-tasks audit (2026-06-18):

  1. RENAME 4 SMCGP long-form subjects to canonical short form
     (fixes the subject-name inconsistency that splits the same contact
     into 2 visual clusters)

  2. RE-ASSOCIATE 6 orphan tasks to their deals/contacts
     (restores the audit trail for completed outreach activities that
     are currently disconnected from the underlying deals)

  3. RE-DUE 7 past-due open tasks (due 2026-05-29, now ~20 days past)
     to today + 7 days = 2026-06-25
     (stops the silent queue rot)

Task 368495619797 (Mary Grace Caballes, due 2026-12-16) is intentionally
NOT modified — flagged in the audit as a manual decision and the due
date is still in the future.

Modes:
  --dry-run    Print what would change, no API writes
  --execute    (default) Apply all changes

Outputs:
  - reports/audit_fixes_changelog_YYYYMMDD-HHMMSS.json  (per-operation log)
  - reports/audit_fixes_rollback_YYYYMMDD-HHMMSS.json   (revert instructions)
  - stdout summary

Idempotency:
  - Renames: only PATCH if current subject matches expected long form
  - Re-due: only PATCH if current hs_timestamp is in the past
  - Re-associate: skip if association already exists (idempotent)
"""

import os
import re
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ---------------- config ----------------
TOKEN_PATH = Path.home() / ".hermes" / ".env"
BASE = "https://api.hubapi.com"
SLEEP = 0.25  # polite delay between calls (HubSpot recommends this)
REPORTS_DIR = Path.home() / "Documents" / "ECONARES_WORKSPACE" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Canonical (short) subject for the SMCGP cluster
NEW_SMCGP_SUBJECT = "follow up with san miguel global power"

# Re-due target: today + 7 days at 16:00 PHT (08:00 UTC)
NEW_DUE = (datetime.now(timezone.utc) + timedelta(days=7))
NEW_DUE = NEW_DUE.replace(hour=8, minute=0, second=0, microsecond=0)
NEW_DUE_ISO = NEW_DUE.isoformat().replace("+00:00", "Z")
NEW_DUE_HUMAN = NEW_DUE.strftime("%Y-%m-%d")

# 4 SMCGP long-form tasks to rename (the "duplicate-feeling" cluster)
SMCGP_RENAMES = [
    "371707497154",
    "372367782643",
    "375100949184",
    "375599966969",
]
SMCGP_OLD_SUBJECT_FRAGMENT = "holdings corporation"  # signature to verify before rename

# 7 past-due tasks to re-due (all currently due 2026-05-29)
REDUE_TASKS = [
    ("365474280178", "[Gmail ★] Philippine Nickel Ore Supply | ECONARES"),
    ("365485966013", "China Nickel follow-up - Tsingshan and YNQSGT"),
    ("365619775164", "Research Emmanuel Castro — Acciona Daanbantayan site (diesel)"),
    ("366800672475", "[COPPER/ZINC/LEAD] Aurelio Ramones Jr. — Isabela buyer wants"),
    ("368593698533", "Outreach — Zhejiang Huayou Cobalt Co. Ltd. | Day 1 Email"),
    ("368545238723", "Outreach — Jinchuan Group International Resources | Day 1 Email"),
    ("370180074190", "Follow up on Nickel Ore — Bulk Ore Limited"),
]

# 6 orphan tasks to re-associate
# (task_id, company_query, contact_query, also_link_company_deals)
ORPHAN_TASKS = [
    {
        "id": "369842216663",
        "subject": "Fraser Outreach — Team Energy Corporation",
        "company_query": "Team Energy",
        "contact_query": None,  # no named contact in subject
        "link_deals_via_company": True,
    },
    {
        "id": "368565424856",
        "subject": "Follow up — L.M. Pantilo, Carmen Copper | lmpantilo@carmencopper.com",
        "company_query": "Carmen Copper",
        "contact_query": "Pantilo",
        "link_deals_via_company": True,
    },
    {
        "id": "367837349576",
        "subject": "FOLLOW UP Allan Saquilayan — Republic Cement (profile sent)",
        "company_query": "Republic Cement",
        "contact_query": "Saquilayan",
        "link_deals_via_company": True,
    },
    {
        "id": "367837175508",
        "subject": "MTG CONFIRMED: Sebastian/MGEN — May 4, 10:30 AM Virtual",
        "company_query": "MGEN",
        "contact_query": "Sebastian",
        "link_deals_via_company": True,
    },
    {
        "id": "366050338535",
        "subject": "[Apo Cement / Taiheiyo] Follow up on field visit results",
        "company_query": "Apo Cement",
        "contact_query": None,
        "link_deals_via_company": True,
    },
    {
        "id": "366091924199",
        "subject": "[DEFERRED — Identity Verification] [Durano Paper/Sugar] Research company",
        "company_query": "Durano",
        "contact_query": None,
        "link_deals_via_company": False,  # likely a research task with no underlying deal yet
    },
]

# ---------------- token ----------------
def load_token() -> str:
    text = TOKEN_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        if s.startswith("HUBSPOT_ACCESS_TOKEN="):
            val = s.split("=", 1)[1].strip().strip('"').strip("'")
            return val
    raise RuntimeError("HUBSPOT_ACCESS_TOKEN not found in .env")


def hdr(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------- API helpers ----------------
def api_get(tok, url, params=None):
    r = requests.get(url, headers=hdr(tok), params=params, timeout=30)
    if r.status_code != 200:
        return {"_err": f"GET {r.status_code}: {r.text[:200]}"}
    return r.json() if r.text else {}


def api_patch(tok, url, body):
    r = requests.patch(url, headers=hdr(tok), json=body, timeout=30)
    if r.status_code not in (200, 201):
        return {"_err": f"PATCH {r.status_code}: {r.text[:200]}"}
    return r.json() if r.text else {}


def api_put(tok, url, body=None):
    if body is None:
        body = []
    r = requests.put(url, headers=hdr(tok), json=body, timeout=30)
    if r.status_code not in (200, 201, 204):
        return {"_err": f"PUT {r.status_code}: {r.text[:200]}"}
    if r.status_code == 204 or not r.text:
        return {"_ok": True}
    return r.json()


def api_post(tok, url, body):
    r = requests.post(url, headers=hdr(tok), json=body, timeout=30)
    if r.status_code not in (200, 201):
        return {"_err": f"POST {r.status_code}: {r.text[:200]}"}
    return r.json() if r.text else {}


# ---------------- domain ops ----------------
def fetch_task(tok, task_id):
    """GET single task with full properties."""
    url = f"{BASE}/crm/v3/objects/tasks/{task_id}"
    props = ",".join([
        "hs_task_subject", "hs_task_body", "hs_task_status", "hs_task_priority",
        "hs_task_type", "hs_timestamp", "hs_createdate", "hs_lastmodifieddate",
    ])
    return api_get(tok, url, params={"properties": props})


def fetch_task_associations(tok, task_id):
    """GET current associations for a task."""
    out = {"contacts": [], "companies": [], "deals": []}
    for kind in ("contacts", "companies", "deals"):
        url = f"{BASE}/crm/v3/objects/tasks/{task_id}/associations/{kind}"
        d = api_get(tok, url)
        if "_err" not in d:
            out[kind] = [r["id"] for r in d.get("results", [])]
    return out



def get_company_from_contact(tok, contact_id):
    """Fallback: read the contact's associatedcompanyid and return the company
    record. Used when the company name search returns no results but a contact
    match was found (e.g. Carmen Copper — name-search missed, but the contact
    record has associatedcompanyid 324008042227)."""
    url = f"{BASE}/crm/v3/objects/contacts/{contact_id}"
    d = api_get(tok, url, params={"properties": "associatedcompanyid,company"})
    if "_err" in d:
        return None, None
    props = d.get("properties", {})
    cid = props.get("associatedcompanyid")
    if not cid:
        return None, None
    # fetch the company
    curl = f"{BASE}/crm/v3/objects/companies/{cid}"
    cd = api_get(tok, curl, params={"properties": "name,domain"})
    if "_err" in cd:
        return cid, None
    return cid, cd.get("properties", {}).get("name", "")



def patch_subject(tok, task_id, new_subject):
    url = f"{BASE}/crm/v3/objects/tasks/{task_id}"
    return api_patch(tok, url, {"properties": {"hs_task_subject": new_subject}})


def patch_due(tok, task_id, new_iso):
    url = f"{BASE}/crm/v3/objects/tasks/{task_id}"
    return api_patch(tok, url, {"properties": {"hs_timestamp": new_iso}})


def put_association(tok, task_id, target_type, target_id):
    """v4 default association PUT for a task to {contacts|companies|deals}."""
    url = f"{BASE}/crm/v4/objects/tasks/{task_id}/associations/default/{target_type}/{target_id}"
    return api_put(tok, url, body=[])


def search_companies(tok, query, limit=5):
    url = f"{BASE}/crm/v3/objects/companies/search"
    return api_post(tok, url, {"query": query, "limit": limit, "properties": ["name", "domain"]})


def search_contacts(tok, query, limit=5):
    url = f"{BASE}/crm/v3/objects/contacts/search"
    return api_post(tok, url, {"query": query, "limit": limit, "properties": ["firstname", "lastname", "email", "company"]})


def get_company_deals(tok, company_id):
    """GET deals associated with a company."""
    url = f"{BASE}/crm/v3/objects/companies/{company_id}/associations/deals"
    d = api_get(tok, url)
    if "_err" in d:
        return []
    return [r["id"] for r in d.get("results", [])]


# ---------------- operations ----------------
def op_rename_smcgp(tok, changelog, dry_run):
    print(f"\n[{ts()}] === 1. RENAME 4 SMCGP long-form tasks → '{NEW_SMCGP_SUBJECT}' ===")
    for tid in SMCGP_RENAMES:
        before = fetch_task(tok, tid)
        if "_err" in before:
            print(f"  [{tid}] FETCH FAILED: {before['_err']}")
            changelog.append({"op": "rename", "id": tid, "status": "fetch_failed", "error": before["_err"]})
            continue
        old_subject = before.get("properties", {}).get("hs_task_subject", "")
        if NEW_SMCGP_SUBJECT.lower() == old_subject.lower():
            print(f"  [{tid}] already canonical: '{old_subject[:60]}'  (skip)")
            changelog.append({"op": "rename", "id": tid, "status": "noop", "reason": "already_canonical", "current": old_subject})
            continue
        if SMCGP_OLD_SUBJECT_FRAGMENT.lower() not in old_subject.lower():
            print(f"  [{tid}] UNEXPECTED subject (not SMCGP long form): '{old_subject[:60]}'  (skip — manual review)")
            changelog.append({"op": "rename", "id": tid, "status": "skipped", "reason": "subject_signature_mismatch", "current": old_subject})
            continue
        if dry_run:
            print(f"  [{tid}] DRY: rename '{old_subject[:60]}' → '{NEW_SMCGP_SUBJECT}'")
            changelog.append({"op": "rename", "id": tid, "status": "dry_run", "before": old_subject, "after": NEW_SMCGP_SUBJECT})
            continue
        result = patch_subject(tok, tid, NEW_SMCGP_SUBJECT)
        if "_err" in result:
            print(f"  [{tid}] PATCH FAILED: {result['_err']}")
            changelog.append({"op": "rename", "id": tid, "status": "patch_failed", "before": old_subject, "error": result["_err"]})
        else:
            new_subject = result.get("properties", {}).get("hs_task_subject", NEW_SMCGP_SUBJECT)
            print(f"  [{tid}] ✓ renamed to '{new_subject[:60]}'")
            changelog.append({"op": "rename", "id": tid, "status": "ok", "before": old_subject, "after": new_subject})
        time.sleep(SLEEP)


def op_re_due(tok, changelog, dry_run):
    print(f"\n[{ts()}] === 2. RE-DUE 7 past-due open tasks → {NEW_DUE_HUMAN} ===")
    for tid, _hint in REDUE_TASKS:
        before = fetch_task(tok, tid)
        if "_err" in before:
            print(f"  [{tid}] FETCH FAILED: {before['_err']}")
            changelog.append({"op": "re_due", "id": tid, "status": "fetch_failed", "error": before["_err"]})
            continue
        props = before.get("properties", {})
        old_due = props.get("hs_timestamp", "")
        status = props.get("hs_task_status", "")
        if status != "NOT_STARTED":
            print(f"  [{tid}] status={status} (not NOT_STARTED) — skip")
            changelog.append({"op": "re_due", "id": tid, "status": "skipped", "reason": f"status={status}", "current_due": old_due})
            continue
        # already past-due?
        if old_due:
            try:
                cur_dt = datetime.fromisoformat(old_due.replace("Z", "+00:00"))
                if cur_dt > datetime.now(timezone.utc):
                    print(f"  [{tid}] due {old_due[:10]} is still in the future — skip")
                    changelog.append({"op": "re_due", "id": tid, "status": "skipped", "reason": "future_dated", "current_due": old_due})
                    continue
            except Exception:
                pass
        if dry_run:
            print(f"  [{tid}] DRY: re-due '{old_due[:10] if old_due else 'none'}' → {NEW_DUE_HUMAN}  (status={status}, subj='{props.get('hs_task_subject','')[:50]}')")
            changelog.append({"op": "re_due", "id": tid, "status": "dry_run", "before": old_due, "after": NEW_DUE_ISO, "subject": props.get("hs_task_subject", "")})
            continue
        result = patch_due(tok, tid, NEW_DUE_ISO)
        if "_err" in result:
            print(f"  [{tid}] PATCH FAILED: {result['_err']}")
            changelog.append({"op": "re_due", "id": tid, "status": "patch_failed", "before": old_due, "error": result["_err"]})
        else:
            new_due = result.get("properties", {}).get("hs_timestamp", NEW_DUE_ISO)
            print(f"  [{tid}] ✓ re-due {old_due[:10] if old_due else 'none'} → {new_due[:10]}  (subj='{props.get('hs_task_subject','')[:50]}')")
            changelog.append({"op": "re_due", "id": tid, "status": "ok", "before": old_due, "after": new_due, "subject": props.get("hs_task_subject", "")})
        time.sleep(SLEEP)


def op_re_associate(tok, changelog, dry_run):
    print(f"\n[{ts()}] === 3. RE-ASSOCIATE 6 orphan tasks ===")
    for spec in ORPHAN_TASKS:
        tid = spec["id"]
        print(f"\n  [{tid}] {spec['subject'][:60]}")
        before = fetch_task(tok, tid)
        if "_err" in before:
            print(f"    FETCH FAILED: {before['_err']}")
            changelog.append({"op": "re_associate", "id": tid, "status": "fetch_failed", "error": before["_err"]})
            continue
        current_assoc = fetch_task_associations(tok, tid)
        result_log = {
            "op": "re_associate",
            "id": tid,
            "subject": spec["subject"],
            "current_associations": current_assoc,
            "search_results": {},
            "links_applied": [],
            "status": "ok",
        }

        # 3a. search company
        company_id = None
        company_name = None
        if spec["company_query"]:
            sr = search_companies(tok, spec["company_query"], limit=3)
            if "_err" in sr:
                print(f"    company search FAILED: {sr['_err']}")
                result_log["search_results"]["company_err"] = sr["_err"]
            else:
                results = sr.get("results", [])
                result_log["search_results"]["company"] = [
                    {"id": r["id"], "name": r.get("properties", {}).get("name", "")}
                    for r in results
                ]
                if results:
                    company_id = results[0]["id"]
                    company_name = results[0].get("properties", {}).get("name", "")
                    print(f"    company match: {company_id}  '{company_name}'  ({len(results)} candidates)")
                else:
                    print(f"    company search: NO MATCH for '{spec['company_query']}'")
            time.sleep(SLEEP)

        # 3b. search contact
        contact_id = None
        contact_name = None
        if spec["contact_query"]:
            sr = search_contacts(tok, spec["contact_query"], limit=3)
            if "_err" in sr:
                print(f"    contact search FAILED: {sr['_err']}")
                result_log["search_results"]["contact_err"] = sr["_err"]
            else:
                results = sr.get("results", [])
                result_log["search_results"]["contact"] = [
                    {"id": r["id"], "name": f'{r.get("properties", {}).get("firstname","")} {r.get("properties", {}).get("lastname","")}'.strip(),
                     "email": r.get("properties", {}).get("email", "")}
                    for r in results
                ]
                if results:
                    contact_id = results[0]["id"]
                    contact_name = f'{results[0].get("properties", {}).get("firstname","")} {results[0].get("properties", {}).get("lastname","")}'.strip()
                    print(f"    contact match: {contact_id}  '{contact_name}'  ({len(results)} candidates)")
                else:
                    print(f"    contact search: NO MATCH for '{spec['contact_query']}'")
            time.sleep(SLEEP)

        # 3b.5. FALLBACK: if no company match yet but a contact matched, try the contact's associatedcompanyid
        if not company_id and contact_id:
            cid2, cname2 = get_company_from_contact(tok, contact_id)
            if cid2:
                company_id = cid2
                company_name = cname2
                result_log["search_results"]["company_via_contact"] = {"id": cid2, "name": cname2}
                print(f"    company via contact fallback: {cid2}  '{cname2}'")
            time.sleep(SLEEP)

        # 3c. find deals via company
        deal_ids = []
        if spec["link_deals_via_company"] and company_id:
            deal_ids = get_company_deals(tok, company_id)
            result_log["search_results"]["deals_via_company"] = deal_ids
            print(f"    deals via company: {len(deal_ids)} found → {deal_ids[:5]}")
            time.sleep(SLEEP)

        # 3d. apply associations
        def apply(target_type, target_id, label):
            if not target_id:
                return False
            if target_id in current_assoc.get(target_type, []):
                print(f"    {label}: already linked ({target_type}/{target_id}) — skip")
                result_log["links_applied"].append({"type": target_type, "id": target_id, "status": "noop_existing"})
                return True
            if dry_run:
                print(f"    {label}: DRY PUT {target_type}/{target_id}")
                result_log["links_applied"].append({"type": target_type, "id": target_id, "status": "dry_run"})
                return True
            res = put_association(tok, tid, target_type, target_id)
            if "_err" in res:
                print(f"    {label}: PUT FAILED {res['_err']}")
                result_log["links_applied"].append({"type": target_type, "id": target_id, "status": "failed", "error": res["_err"]})
                return False
            print(f"    {label}: ✓ linked {target_type}/{target_id}")
            result_log["links_applied"].append({"type": target_type, "id": target_id, "status": "ok"})
            time.sleep(SLEEP)
            return True

        apply("companies", company_id, f"company={company_name}" if company_name else "company")
        apply("contacts", contact_id, f"contact={contact_name}" if contact_name else "contact")
        for did in deal_ids[:3]:  # cap to top 3 deals
            apply("deals", did, f"deal={did}")

        # final status
        if not any(l["status"] == "ok" or l["status"] == "noop_existing" or l["status"] == "dry_run" for l in result_log["links_applied"]):
            result_log["status"] = "no_links"
        changelog.append(result_log)


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print what would change, no writes")
    ap.add_argument("--execute", action="store_true", help="apply changes (default)")
    args = ap.parse_args()
    dry_run = args.dry_run or not args.execute

    print(f"\nHubSpot Duplicate-Tasks Audit — APPLY FIXES")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"New SMCGP subject: '{NEW_SMCGP_SUBJECT}'")
    print(f"New due date for stale tasks: {NEW_DUE_HUMAN} ({NEW_DUE_ISO})")

    tok = load_token()
    print(f"[{ts()}] Token loaded (44 chars)")

    changelog = []
    rollback = []

    op_rename_smcgp(tok, changelog, dry_run)
    op_re_due(tok, changelog, dry_run)
    op_re_associate(tok, changelog, dry_run)

    # write changelog
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    cl_path = REPORTS_DIR / f"audit_fixes_changelog_{stamp}.json"
    cl_path.write_text(json.dumps({
        "generated_at": now_iso(),
        "mode": "dry_run" if dry_run else "execute",
        "new_smcgp_subject": NEW_SMCGP_SUBJECT,
        "new_due_date": NEW_DUE_ISO,
        "operations": changelog,
    }, indent=2, default=str), encoding="utf-8")
    print(f"\n[{ts()}] Changelog written: {cl_path}")

    # write rollback (revert instructions)
    rb_path = REPORTS_DIR / f"audit_fixes_rollback_{stamp}.json"
    rollback_ops = [
        {
            "op": "rename",
            "revert": "PATCH hs_task_subject back to 'before' value",
            "items": [c for c in changelog if c["op"] == "rename" and c.get("status") == "ok"],
        },
        {
            "op": "re_due",
            "revert": "PATCH hs_timestamp back to 'before' value",
            "items": [c for c in changelog if c["op"] == "re_due" and c.get("status") == "ok"],
        },
        {
            "op": "re_associate",
            "revert": "PUT to v4 default association. To remove, use: DELETE /crm/v4/objects/tasks/{tid}/associations/default/{type}/{id}",
            "items": [c for c in changelog if c["op"] == "re_associate" and c.get("status") == "ok"],
        },
    ]
    rb_path.write_text(json.dumps({
        "generated_at": now_iso(),
        "mode": "dry_run" if dry_run else "execute",
        "rollback_ops": rollback_ops,
    }, indent=2, default=str), encoding="utf-8")
    print(f"[{ts()}] Rollback instructions: {rb_path}")

    # final summary
    print(f"\n{'='*60}")
    print(f"SUMMARY  (mode: {'DRY RUN' if dry_run else 'EXECUTED'})")
    print(f"{'='*60}")
    op_counts = {}
    for c in changelog:
        op = c["op"]
        s = c.get("status", "?")
        op_counts.setdefault(op, {}).setdefault(s, 0)
        op_counts[op][s] += 1
    for op, counts in op_counts.items():
        print(f"  {op}: {counts}")
    if dry_run:
        print(f"\nRe-run with --execute to apply.")


if __name__ == "__main__":
    main()
