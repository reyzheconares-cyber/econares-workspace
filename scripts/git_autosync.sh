#!/bin/bash
# ECONARES_WORKSPACE Git Autosync Script
# Scheduled: 0 */2 * * 1-6 (every 2 hours Mon-Sat)
# IMPORTANT: Run via Python subprocess, NOT terminal() — terminal() blocks this script

REPO="${REPO:-/home/mauiclaw/ECONARES_WORKSPACE}"
LOG="${REPO}/logs/git_autosync.log"

cd "$REPO" || exit 1
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] Git autosync starting..." >> "$LOG"

# FIX .git permissions — .git periodically reverts to mode 0o555 (read-only).
# The old check `stat -c '%a'` returns decimal (e.g. 555), NOT octal 40555.
# Unconditionally chmod to ensure write access before any git operation.
chmod -f 755 "$REPO/.git" "$REPO/.git/objects" "$REPO/.git/refs" "$REPO/.git/index" 2>/dev/null

if ! git config --get credential.helper 2>/dev/null | grep -q "/git-credential-store"; then
    git config --global credential.helper /usr/lib/git-core/git-credential-store 2>/dev/null
fi

if git diff --quiet && git diff --cached --quiet; then
    echo "[$TIMESTAMP] No changes" >> "$LOG"
    exit 0
fi

# Fix read-only files in .tmp.driveupload that block git add
chmod -Rf u+w "$REPO/.tmp.driveupload" 2>/dev/null

git add -A && git add -u

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
