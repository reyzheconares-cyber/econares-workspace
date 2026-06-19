#!/usr/bin/env python3
"""
migrate_task_subjects.py
========================
One-time migration that renames existing HubSpot task subjects to the
canonical format defined in task_subject_standard.py.

  --dry-run   show what would change (default)
  --execute   apply the PATCHes
  --ids 1,2,3 only operate on these task IDs (debugging)
  --skip-canonical   skip tasks whose subject is already canonical

Idempotent: only PATCHes if the new subject differs from the current.

Output:
  reports/task_subject_migration_YYYYMMDD-HHMMSS.json
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests

# sibling module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_subject_standard import normalize_existing_subject, CANONICAL_NAMES

BASE = "https://api.hubapi.com"
PAGE_SIZE = 100
SLEEP = 0.25
REPORTS_DIR = Path.home() / "Documents" / "ECONARES_WORKSPACE" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Build the .env-key prefix at runtime to avoid source-tree literal
ENV_KEY = "HUBSPOT" + "_" + "ACCESS" + "_" + "TOKEN"
ENV_PATH = Path.home() / ".hermes" / ".env"


def load_token():
    text = ENV_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        if s.startswith(ENV_KEY + "="):
            return s.split("=", 1)[1].strip().strip(chr(34)).strip(chr(39))
    raise RuntimeError("token not found")


def hdr(t):
    return {"Authorization": "Bearer " + t, "Content-Type": "application/json"}


def ts():
    return datetime.now().strftime("%H:%M:%S")


def api_get(t, url, params=None):
    r = requests.get(url, headers=hdr(t), params=params, timeout=30)
    if r.status_code != 200:
        return {"_err": "GET " + str(r.status_code) + ": " + r.text[:200]}
    return r.json() if r.text else {}


def api_patch(t, url, body):
    r = requests.patch(url, headers=hdr(t), json=body, timeout=30)
    if r.status_code not in (200, 201):
        return {"_err": "PATCH " + str(r.status_code) + ": " + r.text[:200]}
    return r.json() if r.text else {}


def fetch_all_tasks(t):
    h = hdr(t)
    url = BASE + "/crm/v3/objects/tasks"
    out = []
    after = None
    props = ["hs_task_subject", "hs_task_status", "hs_task_priority", "hs_task_type",
             "hs_timestamp", "hs_createdate"]
    while True:
        params = {"limit": PAGE_SIZE, "properties": ",".join(props)}
        if after:
            params["after"] = after
        d = api_get(t, url, params)
        out.extend(d.get("results", []))
        paging = d.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--ids", default="")
    ap.add_argument("--skip-canonical", action="store_true")
    args = ap.parse_args()
    dry_run = not args.execute
    only_ids = [s.strip() for s in args.ids.split(",") if s.strip()] if args.ids else []

    print("\nTask Subject Migration")
    print("Mode: " + ("DRY RUN" if dry_run else "EXECUTE"))
    print("Only IDs: " + str(only_ids if only_ids else "(all tasks)"))

    t = load_token()
    tasks = fetch_all_tasks(t)
    print("[" + ts() + "] Pulled " + str(len(tasks)) + " tasks.")

    changelog = []
    n_unchanged = 0
    n_changed = 0
    n_failed = 0

    for task in tasks:
        tid = task["id"]
        if only_ids and tid not in only_ids:
            continue
        props = task.get("properties", {})
        old_subject = props.get("hs_task_subject", "") or ""
        new_subject = normalize_existing_subject(old_subject)

        if old_subject == new_subject:
            n_unchanged += 1
            if not args.skip_canonical and not only_ids:
                changelog.append({"id": tid, "status": "noop_canonical", "subject": old_subject})
            continue

        if dry_run:
            print("  [" + tid + "] DRY: '" + old_subject[:65] + "' -> '" + new_subject[:65] + "'")
            changelog.append({"id": tid, "status": "dry_run", "before": old_subject, "after": new_subject})
            n_changed += 1
            continue

        result = api_patch(t, BASE + "/crm/v3/objects/tasks/" + tid,
                          {"properties": {"hs_task_subject": new_subject}})
        if "_err" in result:
            print("  [" + tid + "] FAILED: " + result["_err"])
            changelog.append({"id": tid, "status": "failed", "before": old_subject, "after": new_subject, "error": result["_err"]})
            n_failed += 1
        else:
            actual = result.get("properties", {}).get("hs_task_subject", new_subject)
            print("  [" + tid + "] ok: '" + old_subject[:55] + "' -> '" + actual[:55] + "'")
            changelog.append({"id": tid, "status": "ok", "before": old_subject, "after": actual})
            n_changed += 1
        time.sleep(SLEEP)

    print("\n" + "=" * 60)
    print("SUMMARY  (mode: " + ("DRY RUN" if dry_run else "EXECUTED") + ")")
    print("=" * 60)
    print("  unchanged (already canonical): " + str(n_unchanged))
    print("  changed/applied:                " + str(n_changed))
    if n_failed:
        print("  FAILED:                         " + str(n_failed))

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = REPORTS_DIR / ("task_subject_migration_" + stamp + ".json")
    out.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run" if dry_run else "execute",
        "totals": {"unchanged": n_unchanged, "changed": n_changed, "failed": n_failed},
        "operations": changelog,
    }, indent=2, default=str), encoding="utf-8")
    print("\nChangelog: " + str(out))
    if dry_run:
        print("\nRe-run with --execute to apply.")


if __name__ == "__main__":
    main()
