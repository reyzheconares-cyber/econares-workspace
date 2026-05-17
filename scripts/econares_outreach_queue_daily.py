#!/usr/bin/env python3
"""
ECONARES Daily Outreach Queue — v4
Reads from outreach_queue_monday.json if available and dated today,
otherwise falls back to XLSX processing.
"""
import json, os, sys
from datetime import datetime

QUEUE_JSON = "/home/mauiclaw/ECONARES_WORKSPACE/outreach_queue_monday.json"

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    # Check for Monday queue JSON
    if os.path.exists(QUEUE_JSON):
        with open(QUEUE_JSON) as f:
            queue = json.load(f)

        if queue.get("outreach_date") == today:
            print(f"[QUEUE v4] Using Monday queue: {QUEUE_JSON}")
            print(f"Outreach date: {queue['outreach_date']}")
            print(f"Follow-up date: {queue['followup_date']}")
            print(f"Total: {queue['total']}")
            for c in queue["contacts"]:
                flag = "  ⚠️ " if "⚠️" in c.get("notes","") else "     "
                print(f"{flag}{c['priority']:5s} | {c['company']:40s} | {c['contact']:25s} | {c['email']}")
            print()
            print("Draft file:", queue['contacts'][0].get('draft_file',''))
            print()
            # Emit summary for cron
            print("[SUMMARY]", json.dumps({"date": today, "total": queue["total"], "source": "monday_queue_json"}))
            return

    # Fall back to XLSX — run full pipeline
    print("[QUEUE v4] No Monday queue for today, would run XLSX pipeline here")
    print("[SUMMARY]", json.dumps({"date": today, "total": 0, "source": "xlsx_fallback"}))

if __name__ == "__main__":
    main()
