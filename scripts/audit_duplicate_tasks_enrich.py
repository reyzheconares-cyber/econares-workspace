#!/usr/bin/env python
"""Second-pass: enrich the duplicate report with full task detail so the user
can see WHY each group is a duplicate, and check for stale recurring tasks."""

import os
import re
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import requests

TOKEN_PATH = Path.home() / ".hermes" / ".env"
BASE = "https://api.hubapi.com"
PAGE_SIZE = 100

def load_token():
    text = TOKEN_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        if s.startswith("HUBSPOT_ACCESS_TOKEN="):
            if s.startswith("HUBSPOT_ACCESS_TOKEN="):
                val = s.split("=", 1)[1].strip().strip('"').strip("'")
                return val
    raise RuntimeError("no token")

def headers(tok):
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

def get_json(url, h, params=None):
    r = requests.get(url, headers=h, params=params, timeout=30)
    if r.status_code != 200:
        return {"_err": f"{r.status_code} {r.text[:200]}"}
    return r.json()

def fetch_all(tok):
    h = headers(tok)
    url = f"{BASE}/crm/v3/objects/tasks"
    all_tasks = []
    after = None
    properties = [
        "hs_task_subject", "hs_task_body", "hs_task_status",
        "hs_task_priority", "hs_task_type", "hs_timestamp",
        "hs_createdate", "hs_lastmodifieddate",
    ]
    while True:
        params = {"limit": PAGE_SIZE, "properties": ",".join(properties)}
        if after:
            params["after"] = after
        d = get_json(url, h, params)
        all_tasks.extend(d.get("results", []))
        paging = d.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return all_tasks

def norm_subject(s):
    if not s: return ""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s★\-:/.@]", "", s.strip().lower()))

def fetch_assoc(tok, task_id):
    h = headers(tok)
    out = {"contacts": [], "companies": [], "deals": []}
    for kind in ("contacts", "companies", "deals"):
        url = f"{BASE}/crm/v3/objects/tasks/{task_id}/associations/{kind}"
        d = get_json(url, h)
        if "_err" not in d:
            out[kind] = [r["id"] for r in d.get("results", [])]
    return out

def main():
    tok = load_token()
    tasks = fetch_all(tok)
    by_id = {t["id"]: t["properties"] for t in tasks}

    # group by normalized subject (ignoring due date) — these are the "same follow-up" recurrences
    by_subj = defaultdict(list)
    for tid, p in by_id.items():
        s = norm_subject(p.get("hs_task_subject", ""))
        by_subj[s].append(tid)

    # For each subject that has >=2 tasks: fetch associations + body excerpt + dates
    print(f"\n=== SUBJECTS WITH >= 2 TASKS (all statuses, all dates) ===\n")
    rec_clusters = []
    for subj, ids in sorted(by_subj.items(), key=lambda x: -len(x[1])):
        if len(ids) < 2:
            continue
        rows = []
        for tid in ids:
            p = by_id[tid]
            a = fetch_assoc(tok, tid)
            rows.append({
                "id": tid,
                "subject": p.get("hs_task_subject"),
                "status": p.get("hs_task_status"),
                "priority": p.get("hs_task_priority"),
                "type": p.get("hs_task_type"),
                "due_ts": p.get("hs_timestamp"),
                "createdate": p.get("hs_createdate"),
                "lastmodified": p.get("hs_lastmodifieddate"),
                "body_excerpt": (p.get("hs_task_body") or "")[:140],
                "assoc": a,
            })
        rows.sort(key=lambda r: r["createdate"] or "")
        rec_clusters.append({"subject": subj, "count": len(rows), "tasks": rows})
        print(f"### '{subj}' ({len(rows)}x)")
        for r in rows:
            n_assoc = sum(len(v) for v in r["assoc"].values() if isinstance(v, list))
            print(f"  - id={r['id']} [{r['status']}] due={r['due_ts'][:10] if r['due_ts'] else 'none'}  created={r['createdate'][:10] if r['createdate'] else '?'}  assoc={n_assoc}  body='{r['body_excerpt']}'")
        print()

    # Detect STALE OPEN tasks: NOT_STARTED with createdate > 30 days ago
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    stale = []
    for tid, p in by_id.items():
        if p.get("hs_task_status") == "NOT_STARTED" and (p.get("hs_createdate") or "") < cutoff:
            stale.append({
                "id": tid,
                "subject": p.get("hs_task_subject"),
                "status": p.get("hs_task_status"),
                "createdate": p.get("hs_createdate"),
                "due_ts": p.get("hs_timestamp"),
            })
    stale.sort(key=lambda r: r["createdate"] or "")
    print(f"\n=== STALE OPEN TASKS (NOT_STARTED, >30 days old): {len(stale)} ===")
    for s in stale[:40]:
        print(f"  - {s['id']}  {s['subject'][:60]}  created={s['createdate'][:10]}  due={s['due_ts'][:10] if s['due_ts'] else 'none'}")

    # Write enrichment JSON
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recurring_subject_clusters": rec_clusters,
        "stale_open_tasks": stale,
    }
    out_path = Path(r"C:\Users\reyma\Documents\ECONARES_WORKSPACE\reports\duplicate_tasks_enrich_20260618.json")
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote enrichment: {out_path}")

if __name__ == "__main__":
    main()
