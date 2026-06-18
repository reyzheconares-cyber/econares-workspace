#!/usr/bin/env python
"""
HubSpot Duplicate-Task Audit (READ-ONLY)
========================================
Pulls all tasks from portal 245683432, groups them by likely-duplicate signature,
and writes a JSON report + a markdown summary.

NO WRITES. NO DELETES. NO MERGES. This is the audit pass before sign-off.

Signature (in order of strictness):
  TIER 1 — Exact: same subject string (case-trimmed) + same due date + same status
  TIER 2 — Near: same subject + same day + same status (whitespace/punct normalized)
  TIER 3 — Looser: same subject prefix (first 30 chars) + same day + same status
  TIER 4 — Gmail sync residue: multiple [Gmail ★] tasks for the same thread id

Also tallies:
  - Total tasks
  - Open vs completed
  - Tasks missing associations (no contact/company/deal)
  - Top subjects by volume (noise / recurring-tasks)
  - Gmail★ sync count vs manual
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

import requests

# --- config ---
TOKEN_PATH = Path.home() / ".hermes" / ".env"
_MASK = "***"  # placeholder, real value below in load_token()
BASE = "https://api.hubapi.com"
PORTAL_ID = 245683432
PAGE_SIZE = 100   # max allowed by v3
OUTPUT_DIR = Path.home() / "Documents" / "ECONARES_WORKSPACE" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- token ---
def load_token() -> str:
    text = TOKEN_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        if s.startswith("HUBSPOT_ACCESS_TOKEN="):
            if s.startswith("HUBSPOT_ACCESS_TOKEN="):
                val = s.split("=", 1)[1].strip().strip('"').strip("'")
                return val
    raise RuntimeError("HUBSPOT_ACCESS_TOKEN not found in .env")


def headers(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def get_json(url, h, params=None):
    r = requests.get(url, headers=h, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {url}: {r.text[:200]}")
    return r.json()


# --- normalization helpers ---
def norm_subject(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s★\-:/.@]", "", s)
    return s


def subject_prefix(s: str, n: int = 30) -> str:
    return norm_subject(s)[:n]


def due_day(ts: str | None) -> str:
    if not ts:
        return "(no-due-date)"
    # HubSpot returns ISO with Z or ms
    try:
        if ts.endswith("Z"):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        else:
            # handle ms
            if ts.isdigit():
                dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            else:
                dt = datetime.fromisoformat(ts)
        return dt.date().isoformat()
    except Exception:
        return ts[:10] if len(ts) >= 10 else "(bad-date)"


def status_of(t: dict) -> str:
    # v3 returns hs_task_status or status
    return t.get("hs_task_status") or t.get("status") or "(no-status)"


# --- pull all tasks (paginated) ---
def fetch_all_tasks(tok: str) -> list:
    h = headers(tok)
    url = f"{BASE}/crm/v3/objects/tasks"
    all_tasks = []
    after = None
    page = 0
    properties = [
        "hs_task_subject", "hs_task_body", "hs_task_status",
        "hs_task_priority", "hs_task_type", "hs_timestamp",
        "hs_createdate", "hs_lastmodifieddate", "hs_object_id",
    ]
    while True:
        page += 1
        params = {"limit": PAGE_SIZE, "properties": ",".join(properties)}
        if after:
            params["after"] = after
        data = get_json(url, h, params)
        results = data.get("results", [])
        all_tasks.extend(results)
        paging = data.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return all_tasks


# --- fetch associations for a batch ---
def fetch_associations(tok: str, task_ids: list) -> dict:
    """For each task, GET associations to contacts/companies/deals."""
    h = headers(tok)
    out = {}
    for tid in task_ids:
        out[tid] = {"contacts": [], "companies": [], "deals": []}
        for kind in ("contacts", "companies", "deals"):
            url = f"{BASE}/crm/v3/objects/tasks/{tid}/associations/{kind}"
            try:
                d = get_json(url, h)
                ids = [r["id"] for r in d.get("results", [])]
                out[tid][kind] = ids
            except Exception as e:
                out[tid][kind] = f"ERR: {e}"
    return out


# --- main ---
def main():
    tok = load_token()
    print(f"[{now()}] Token loaded. Fetching all tasks (paginated)…", file=sys.stderr)
    tasks = fetch_all_tasks(tok)
    print(f"[{now()}] Pulled {len(tasks)} tasks.", file=sys.stderr)

    # index by id
    by_id = {}
    for t in tasks:
        props = t.get("properties", {})
        tid = t.get("id")
        by_id[tid] = {
            "id": tid,
            "subject": props.get("hs_task_subject", ""),
            "status": status_of(props),
            "priority": props.get("hs_task_priority", ""),
            "type": props.get("hs_task_type", ""),
            "due_ts": props.get("hs_timestamp", ""),
            "due_day": due_day(props.get("hs_timestamp")),
            "createdate": props.get("hs_createdate", ""),
            "lastmodified": props.get("hs_lastmodifieddate", ""),
            "body_excerpt": (props.get("hs_task_body", "") or "")[:160],
            "is_gmail_sync": "[Gmail ★]" in (props.get("hs_task_subject", "") or ""),
        }

    # associations (batch)
    print(f"[{now()}] Fetching associations for {len(tasks)} tasks…", file=sys.stderr)
    assoc = fetch_associations(tok, list(by_id.keys()))
    for tid, t in by_id.items():
        a = assoc.get(tid, {})
        t["contacts"] = a.get("contacts", [])
        t["companies"] = a.get("companies", [])
        t["deals"] = a.get("deals", [])
        t["has_any_assoc"] = bool(
            (isinstance(t["contacts"], list) and t["contacts"])
            or (isinstance(t["companies"], list) and t["companies"])
            or (isinstance(t["deals"], list) and t["deals"])
        )

    # bucket by signature
    tiers = {
        "tier1_exact": defaultdict(list),
        "tier2_near_day": defaultdict(list),
        "tier3_prefix_day": defaultdict(list),
    }
    for tid, t in by_id.items():
        subj = norm_subject(t["subject"])
        day = t["due_day"]
        st = t["status"]
        # TIER 1: full subject + day + status
        sig1 = (subj, day, st)
        # TIER 2: subject + day + status (looser on whitespace)
        sig2 = (re.sub(r"\s+", " ", subj), day, st)
        # TIER 3: 30-char prefix + day + status
        sig3 = (subject_prefix(t["subject"]), day, st)
        tiers["tier1_exact"][sig1].append(tid)
        tiers["tier2_near_day"][sig2].append(tid)
        tiers["tier3_prefix_day"][sig3].append(tid)

    # duplicate groups (≥2 members)
    def groups_with_dupes(d):
        return {k: v for k, v in d.items() if len(v) >= 2}

    dup_t1 = groups_with_dupes(tiers["tier1_exact"])
    dup_t2 = groups_with_dupes(tiers["tier2_near_day"])
    dup_t3 = groups_with_dupes(tiers["tier3_prefix_day"])

    # Gmail thread-id dedup: extract the "(thread:...)" or similar from body
    gmail_groups = defaultdict(list)
    for tid, t in by_id.items():
        if t["is_gmail_sync"]:
            # subject starts with [Gmail ★] <subject>
            sub = t["subject"]
            m = re.search(r"\[Gmail ★\]\s*(.+)$", sub)
            if m:
                gmail_groups[m.group(1).strip()].append(tid)

    dup_gmail = {k: v for k, v in gmail_groups.items() if len(v) >= 2}

    # noise / recurring task subjects
    subj_counter = Counter(norm_subject(t["subject"]) for t in by_id.values())
    noisy_subjects = [(s, c) for s, c in subj_counter.most_common(20) if c >= 2]

    # orphans (no associations at all)
    orphans = [t for t in by_id.values() if not t["has_any_assoc"]]
    # status breakdown
    status_counter = Counter(t["status"] for t in by_id.values())
    # gmail vs manual
    gmail_count = sum(1 for t in by_id.values() if t["is_gmail_sync"])
    manual_count = len(by_id) - gmail_count

    # write JSON report
    out_json = {
        "generated_at": now_iso(),
        "portal_id": PORTAL_ID,
        "totals": {
            "total_tasks": len(by_id),
            "open": sum(1 for t in by_id.values() if t["status"] in ("NOT_STARTED", "DEFERRED", "IN_PROGRESS", "WAITING")),
            "completed": sum(1 for t in by_id.values() if t["status"] == "COMPLETED"),
            "gmail_sync": gmail_count,
            "manual": manual_count,
            "orphan_no_associations": len(orphans),
            "status_breakdown": dict(status_counter),
        },
        "duplicates": {
            "tier1_exact_subject_day_status": {
                "group_count": len(dup_t1),
                "total_dupe_task_ids": sum(len(v) for v in dup_t1.values()),
                "groups": [
                    {"signature": list(k), "task_ids": v, "count": len(v)}
                    for k, v in dup_t1.items()
                ],
            },
            "tier2_normalized_day_status": {
                "group_count": len(dup_t2),
                "total_dupe_task_ids": sum(len(v) for v in dup_t2.values()),
                "groups": [
                    {"signature": list(k), "task_ids": v, "count": len(v)}
                    for k, v in dup_t2.items()
                ],
            },
            "tier3_prefix_day_status": {
                "group_count": len(dup_t3),
                "total_dupe_task_ids": sum(len(v) for v in dup_t3.values()),
                "groups": [
                    {"signature": list(k), "task_ids": v, "count": len(v)}
                    for k, v in dup_t3.items()
                ],
            },
            "gmail_thread_dupes": {
                "group_count": len(dup_gmail),
                "total_dupe_task_ids": sum(len(v) for v in dup_gmail.values()),
                "groups": [
                    {"subject": k, "task_ids": v, "count": len(v)}
                    for k, v in dup_gmail.items()
                ],
            },
        },
        "noisy_subjects_top20": [
            {"subject": s, "count": c} for s, c in noisy_subjects
        ],
        "orphan_tasks_no_associations": [
            {
                "id": t["id"],
                "subject": t["subject"],
                "status": t["status"],
                "createdate": t["createdate"],
                "body_excerpt": t["body_excerpt"],
            }
            for t in sorted(orphans, key=lambda x: x["createdate"], reverse=True)
        ],
    }

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = OUTPUT_DIR / f"duplicate_tasks_audit_{stamp}.json"
    json_path.write_text(json.dumps(out_json, indent=2, default=str), encoding="utf-8")
    print(f"[{now()}] JSON report: {json_path}", file=sys.stderr)

    # write markdown summary
    md = render_markdown(out_json)
    md_path = OUTPUT_DIR / f"duplicate_tasks_audit_{stamp}.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"[{now()}] Markdown report: {md_path}", file=sys.stderr)

    # print compact summary to stdout
    print(json.dumps(out_json["totals"], indent=2))
    print("\n--- Tier-1 (exact subject + day + status) duplicate groups ---")
    for g in out_json["duplicates"]["tier1_exact_subject_day_status"]["groups"][:10]:
        print(f"  {g['count']}x  {g['signature']}")
    print(f"\n--- Gmail★ sync duplicate groups: {len(dup_gmail)} ---")
    for g in list(out_json["duplicates"]["gmail_thread_dupes"]["groups"])[:10]:
        print(f"  {g['count']}x  {g['subject'][:80]}")
    print(f"\n--- No-association orphan tasks: {len(orphans)} ---")


def now():
    return datetime.now().strftime("%H:%M:%S")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def render_markdown(rep: dict) -> str:
    t = rep["totals"]
    d = rep["duplicates"]
    md = []
    md.append(f"# HubSpot Duplicate Tasks Audit")
    md.append(f"_Generated: {rep['generated_at']} · Portal: {rep['portal_id']}_")
    md.append("")
    md.append("## Totals")
    md.append(f"- **Total tasks**: {t['total_tasks']}")
    md.append(f"- **Open** (NOT_STARTED/DEFERRED/IN_PROGRESS/WAITING): {t['open']}")
    md.append(f"- **Completed**: {t['completed']}")
    md.append(f"- **Gmail★ sync tasks**: {t['gmail_sync']}  (manual: {t['manual']})")
    md.append(f"- **Orphan tasks (no contact/company/deal)**: {t['orphan_no_associations']}")
    md.append("")
    md.append("### Status breakdown")
    for k, v in sorted(t["status_breakdown"].items(), key=lambda x: -x[1]):
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Duplicate groups")
    md.append("")
    md.append(f"### Tier 1 — exact (subject + due-day + status): {d['tier1_exact_subject_day_status']['group_count']} groups, {d['tier1_exact_subject_day_status']['total_dupe_task_ids']} task IDs in groups of ≥2")
    for g in d["tier1_exact_subject_day_status"]["groups"][:25]:
        md.append(f"- **{g['count']}x** `{g['signature'][0][:80]}` (day={g['signature'][1]}, status={g['signature'][2]}) — ids: {', '.join(g['task_ids'])}")
    md.append("")
    md.append(f"### Tier 2 — normalized subject + day + status: {d['tier2_normalized_day_status']['group_count']} groups")
    md.append("")
    md.append(f"### Tier 3 — 30-char prefix + day + status: {d['tier3_prefix_day_status']['group_count']} groups")
    md.append("")
    md.append(f"### Gmail★ thread-level duplicates: {d['gmail_thread_dupes']['group_count']} groups")
    for g in d["gmail_thread_dupes"]["groups"][:25]:
        md.append(f"- **{g['count']}x** `{g['subject'][:80]}` — ids: {', '.join(g['task_ids'])}")
    md.append("")
    md.append("## Top noisy subjects (≥2 tasks, all statuses)")
    for s in rep["noisy_subjects_top20"]:
        md.append(f"- {s['count']}x — {s['subject'][:80]}")
    md.append("")
    md.append(f"## Orphan tasks (no contact/company/deal associations): {len(rep['orphan_tasks_no_associations'])}")
    for t in rep["orphan_tasks_no_associations"][:30]:
        md.append(f"- {t['id']} [{t['status']}] {t['subject'][:80]}  (created {t['createdate'][:10]})")
    md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    main()
