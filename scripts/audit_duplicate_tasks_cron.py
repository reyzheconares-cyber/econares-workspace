#!/usr/bin/env python3
"""
audit_duplicate_tasks_cron.py
=============================
Weekly wrapper that re-runs the HubSpot duplicate-tasks audit and pings
Telegram (if configured) with a compact summary of any new fragmentation.

Schedule: Mon 8:00 AM PHT (before the daily brief)
Skips:    PH regular holidays + non-Mondays

The wrapper exits silently on skip-days (no Telegram noise).
On run days, the audit JSON is saved to reports/ and a short Telegram
message is sent listing the top fragmentation issues, if any.

Audit script:  ~/Documents/ECONARES_WORKSPACE/scripts/audit_duplicate_tasks.py
This wrapper:  ~/AppData/Local/hermes/scripts/audit_duplicate_tasks_cron.py
"""

import os
import sys
import json
import subprocess
import datetime
import urllib.request
import urllib.error
from pathlib import Path
import zoneinfo

# === Philippine Regular Holidays 2024-2027 (synced with trade_signal_monitor_cron.py) ===
PH_REGULAR_HOLIDAYS = {
    2024: [(1, 1, "New Years Day"), (2, 10, "Chinese New Year"), (3, 28, "Maundy Thursday"), (3, 29, "Good Friday"), (4, 9, "Araw ng Kagitingan"), (5, 1, "Labor Day"), (6, 12, "Independence Day"), (8, 26, "National Heroes Day"), (11, 1, "All Saints Day"), (11, 30, "Bonifacio Day"), (12, 25, "Christmas Day"), (12, 30, "Rizal Day")],
    2025: [(1, 1, "New Years Day"), (1, 29, "Chinese New Year"), (4, 17, "Maundy Thursday"), (4, 18, "Good Friday"), (4, 9, "Araw ng Kagitingan"), (5, 1, "Labor Day"), (6, 12, "Independence Day"), (8, 25, "National Heroes Day"), (11, 1, "All Saints Day"), (11, 30, "Bonifacio Day"), (12, 25, "Christmas Day"), (12, 30, "Rizal Day")],
    2026: [(1, 1, "New Years Day"), (2, 17, "Chinese New Year"), (4, 2, "Maundy Thursday"), (4, 3, "Good Friday"), (4, 9, "Araw ng Kagitingan"), (5, 1, "Labor Day"), (6, 12, "Independence Day"), (8, 31, "National Heroes Day"), (11, 1, "All Saints Day"), (11, 30, "Bonifacio Day"), (12, 25, "Christmas Day"), (12, 30, "Rizal Day")],
    2027: [(1, 1, "New Years Day"), (2, 6, "Chinese New Year"), (3, 25, "Maundy Thursday"), (3, 26, "Good Friday"), (4, 9, "Araw ng Kagitingan"), (5, 1, "Labor Day"), (6, 12, "Independence Day"), (8, 30, "National Heroes Day"), (11, 1, "All Saints Day"), (11, 30, "Bonifacio Day"), (12, 25, "Christmas Day"), (12, 30, "Rizal Day")],
}


def is_ph_holiday(today):
    year_holidays = PH_REGULAR_HOLIDAYS.get(today.year, [])
    return (today.month, today.day) in [(m, d) for m, d, _ in year_holidays]


def is_monday(today):
    return today.weekday() == 0


def load_env():
    env_path = Path.home() / ".hermes" / ".env"
    env = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export "):]
        if "=" in s:
            k, v = s.split("=", 1)
            env[k.strip()] = v.strip().strip(chr(34)).strip(chr(39))
    return env


def send_telegram(message, env):
    bot = env.get("TELEGRAM_BOT_TOKEN", "")
    chat = env.get("TELEGRAM_CHAT_ID", "")
    if not bot or not chat:
        print("  ! Telegram not configured (no TELEGRAM_BOT_TOKEN/CHAT_ID in .env).")
        return False
    url = "https://api.telegram.org/bot" + bot + "/sendMessage"
    payload = json.dumps({
        "chat_id": chat,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            ok = r.status == 200
            if not ok:
                print("  ! Telegram send HTTP " + str(r.status))
            return ok
    except urllib.error.URLError as e:
        print("  ! Telegram send error: " + str(e))
        return False


def fmt_message(rep):
    totals = rep.get("totals", {})
    dupes = rep.get("duplicates", {})
    t1 = dupes.get("tier1_exact_subject_day_status", {})
    t3 = dupes.get("tier3_prefix_day_status", {})
    gmail = dupes.get("gmail_thread_dupes", {})
    orphans = rep.get("orphan_tasks_no_associations", [])

    lines = []
    lines.append("<b>HubSpot Tasks Audit (weekly)</b>")
    lines.append("Total: " + str(totals.get("total_tasks", 0)) +
                 "  Open: " + str(totals.get("open", 0)) +
                 "  Completed: " + str(totals.get("completed", 0)))
    lines.append("")
    lines.append("Tier-1 dupes: " + str(t1.get("group_count", 0)) +
                 " groups / " + str(t1.get("total_dupe_task_ids", 0)) + " tasks")
    lines.append("Recurring clusters: " + str(t3.get("group_count", 0)) + " subjects")
    lines.append("Orphans (no assoc): " + str(len(orphans)))
    lines.append("Gmail* dupes: " + str(gmail.get("group_count", 0)))

    top_clusters = t3.get("groups", [])[:5]
    if top_clusters:
        lines.append("")
        lines.append("<b>Top recurring clusters:</b>")
        for g in top_clusters:
            sig = g.get("signature", ["", "", ""])
            lines.append("- " + str(g.get("count", 0)) + "x " + chr(39) + str(sig[0])[:50] + chr(39))

    if orphans:
        lines.append("")
        lines.append("<b>Orphan tasks (top 3):</b>")
        for o in orphans[:3]:
            lines.append("- " + str(o.get("id")) + " " + chr(39) + str(o.get("subject"))[:50] + chr(39))

    if not t1.get("groups") and not t3.get("groups") and not orphans:
        lines.append("")
        lines.append("OK - no fragmentation, no orphans, no dupes.")
    return chr(10).join(lines)


def main():
    try:
        tz = zoneinfo.ZoneInfo("Asia/Manila")
    except Exception:
        tz = None
    today = datetime.datetime.now(tz).date() if tz else datetime.date.today()
    date_str = today.isoformat()
    weekday = today.strftime("%A")

    if not is_monday(today):
        print("[" + date_str + " " + weekday + " SKIP] Audit runs Mondays only.")
        return 0

    if is_ph_holiday(today):
        year_holidays = PH_REGULAR_HOLIDAYS.get(today.year, [])
        holiday_name = next(
            (name for m, d, name in year_holidays if (m, d) == (today.month, today.day)),
            "PH Regular Holiday",
        )
        print("[" + date_str + " SKIP] " + holiday_name + " - audit not running.")
        return 0

    print("[" + date_str + " Monday RUN] Starting HubSpot task audit...")

    audit_script = Path.home() / "Documents" / "ECONARES_WORKSPACE" / "scripts" / "audit_duplicate_tasks.py"
    if not audit_script.exists():
        print("  ! Audit script not found: " + str(audit_script))
        return 1

    result = subprocess.run(
        [sys.executable, str(audit_script)],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        print("  ! Audit script failed (exit " + str(result.returncode) + "):")
        print(result.stderr[-500:])
        return result.returncode

    reports_dir = Path.home() / "Documents" / "ECONARES_WORKSPACE" / "reports"
    audit_jsons = sorted(reports_dir.glob("duplicate_tasks_audit_*.json"), reverse=True)
    if not audit_jsons:
        print("  ! No audit JSON found in " + str(reports_dir))
        return 1
    latest = audit_jsons[0]

    rep = json.loads(latest.read_text(encoding="utf-8"))
    msg = fmt_message(rep)
    msg = msg + chr(10) + chr(10) + "Report: " + str(latest.name)

    env = load_env()
    sent = send_telegram(msg, env)
    if sent:
        print("  ok Audit summary sent to Telegram.")
    else:
        print("  ! Audit summary NOT sent (Telegram unconfigured or error).")
        print("  Message was:" + chr(10) + msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())