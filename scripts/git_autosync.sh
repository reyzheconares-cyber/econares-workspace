#!/bin/bash
# ECONARES_WORKSPACE Git Autosync Script
# Scheduled: 0 */2 * * 1-6 (every 2 hours Mon-Sat)
# IMPORTANT: Run via Python subprocess, NOT terminal() — terminal() blocks this script

REPO="${REPO:-/home/mauiclaw/ECONARES_WORKSPACE}"
LOG="${REPO}/logs/git_autosync.log"

cd "$REPO" || exit 1
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] Git autosync starting..." >> "$LOG"

git_mode=$(stat -c '%a' "$REPO/.git" 2>/dev/null)
if [ "$git_mode" = "40555" ]; then
    chmod u+w "$REPO/.git" 2>/dev/null
    chmod -R u+w "$REPO/.git/objects" 2>/dev/null
    chmod -R u+w "$REPO/.git/refs" 2>/dev/null
    chmod u+w "$REPO/.git/index" 2>/dev/null
elif [ -f "$REPO/.git/index.lock" ]; then
    rm -f "$REPO/.git/index.lock"
fi

if ! git config --get credential.helper 2>/dev/null | grep -q "/git-credential-store"; then
    git config --global credential.helper /usr/lib/git-core/git-credential-store 2>/dev/null
fi

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
