#!/bin/bash
# ECONARES Workspace — Git Auto-Sync
REPO="/home/mauiclaw/ECONARES_WORKSPACE"
LOG="$REPO/logs/git_autosync.log"
cd "$REPO" || exit 1
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Git autosync starting..." >> "$LOG"
if git diff --quiet && git diff --cached --quiet; then
    echo "[$TIMESTAMP] No changes" >> "$LOG"
    exit 0
fi
git add -A
if git diff --cached --quiet; then
    echo "[$TIMESTAMP] Nothing to commit" >> "$LOG"
    exit 0
fi
git commit -m "Auto-save: $TIMESTAMP" >> "$LOG" 2>&1
if git push origin master >> "$LOG" 2>&1; then
    echo "[$TIMESTAMP] Pushed OK" >> "$LOG"
else
    echo "[$TIMESTAMP] PUSH FAILED" >> "$LOG"
fi
