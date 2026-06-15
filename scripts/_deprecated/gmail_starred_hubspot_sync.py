#!/usr/bin/env python3
"""Gmail starred → HubSpot tasks sync

Usage:
  python gmail_starred_hubspot_sync.py                # normal run
  python gmail_starred_hubspot_sync.py --dry-run      # read-only — no HubSpot writes, no Telegram
  python gmail_starred_hubspot_sync.py --no-telegram  # create tasks but skip the Telegram summary
  python gmail_starred_hubspot_sync.py --days 14      # widen the search window (default 7)
"""
import subprocess, json, os, sys
from datetime import datetime, timedelta
import urllib.parse

# ── CLI flags (added Jun 2026 — was running unconditionally before) ──
import argparse
_parser = argparse.ArgumentParser(add_help=True, description='Gmail starred → HubSpot tasks sync')
_parser.add_argument('--dry-run', action='store_true',
                     help='Read-only mode: do not create HubSpot tasks, do not send Telegram.')
_parser.add_argument('--no-telegram', action='store_true',
                     help='Create tasks as normal, but skip the Telegram summary.')
_parser.add_argument('--days', type=int, default=7,
                     help='Look back N days for starred messages (default 7).')
_args = _parser.parse_args()
DRY_RUN = _args.dry_run
NO_TELEGRAM = _args.no_telegram
LOOKBACK_DAYS = _args.days

HERMES_DIR = os.path.expanduser('~/.hermes')
TOKEN_FILE = os.path.join(HERMES_DIR, 'google_token.json')
CLIENT_FILE = os.path.join(HERMES_DIR, 'google_client_secret.json')
WORKSPACE  = os.path.expanduser('~/ECONARES_WORKSPACE')
SYNC_FILE  = os.path.join(WORKSPACE, 'synced_gmail_threads.txt')
LOG_FILE   = os.path.join(WORKSPACE, 'logs', 'gmail_hubspot_sync.log')

# ── helpers ──────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def run(cmd, timeout=30):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout, result.stderr, result.returncode

# ── 1. Refresh Gmail token (form-encoded) ────────────────────────────
log("Refreshing Gmail OAuth token...")
with open(TOKEN_FILE) as f:
    gmail_tok = json.load(f)
with open(CLIENT_FILE) as f:
    client = json.load(f)['installed']

rt  = gmail_tok['refresh_token']
cid = client['client_id']
csec = client['client_secret']

refresh_cmd = [
    'curl', '-s', '-X', 'POST', 'https://oauth2.googleapis.com/token',
    '-d', f'client_id={cid}&client_secret={csec}&refresh_token={rt}&grant_type=refresh_token'
]
out, err, rc = run(' '.join(refresh_cmd))
log(f"Refresh rc={rc} out={out[:200]}")

try:
    new_tok_data = json.loads(out)
    access_token = new_tok_data['access_token']
    gmail_tok['access_token'] = access_token
    gmail_tok['expires_in'] = new_tok_data.get('expires_in', 3599)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(gmail_tok, f, indent=2)
    log(f"Token refreshed OK ({len(access_token)} chars)")
except Exception as e:
    log(f"ERROR refreshing token: {e} | out={out[:300]}")
    sys.exit(1)

# Verify token
verify_out, _, _ = run(f'curl -s "https://gmail.googleapis.com/gmail/v1/users/me/profile" -H "Authorization: Bearer {access_token}"')
try:
    profile = json.loads(verify_out)
    log(f"Gmail profile: {profile.get('emailAddress')} | {profile.get('messagesTotal')} msgs")
except:
    log(f"Token verify failed: {verify_out[:200]}")

# ── 2. Get HubSpot PAT ───────────────────────────────────────────────
# Accepts both `export HUBSPOT_ACCESS_TOKEN=...` and `HUBSPOT_ACCESS_TOKEN=...`
env_content = open(os.path.expanduser('~/.hermes/.env')).read()
hubspot_token = None
for line in env_content.splitlines():
    stripped = line.lstrip()
    if stripped.startswith('export '):
        stripped = stripped[len('export '):]
    if stripped.startswith('HUBSPOT_ACCESS_TOKEN'):
        hubspot_token = stripped.split('=', 1)[1].strip().strip('"').strip("'")
        break
if not hubspot_token:
    log("ERROR: HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env")
    sys.exit(2)
log(f"HubSpot token: {hubspot_token[:15]}...")

# ── 3. Read already-synced IDs ──────────────────────────────────────
synced = set()
if os.path.exists(SYNC_FILE):
    with open(SYNC_FILE) as f:
        synced = set(line.strip() for line in f if line.strip())
log(f"Already synced: {len(synced)} IDs")

# ── 4. Search starred emails (last LOOKBACK_DAYS days) ──────────────
after_ts = int((datetime.now() - timedelta(days=LOOKBACK_DAYS)).timestamp())
q = f"is:starred after:{after_ts}"
encoded_q = urllib.parse.quote(q)
list_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=50&q={encoded_q}"
list_out, _, _ = run(f'curl -s "{list_url}" -H "Authorization: Bearer {access_token}"')
log(f"Search query: {q}")
log(f"Search raw: {list_out[:300]}")

try:
    list_data = json.loads(list_out)
    messages = list_data.get('messages', [])
    log(f"Found {len(messages)} starred messages in last {LOOKBACK_DAYS} days")
except Exception as e:
    log(f"ERROR parsing search: {e} | {list_out[:300]}")
    messages = []

# ── 5. Fetch metadata for each message ──────────────────────────────
HEADERS = ['From', 'Subject', 'Date', 'To']
METADATA_STR = '&'.join(f'metadataHeaders={h}' for h in HEADERS)

def get_metadata(msg_id):
    url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&{METADATA_STR}'
    out, _, _ = run(f'curl -s "{url}" -H "Authorization: Bearer {access_token}"')
    try:
        data = json.loads(out)
        headers = {h['name']: h['value'] for h in data.get('payload', {}).get('headers', [])}
        return {
            'id': msg_id,
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', '(no subject)'),
            'date': headers.get('Date', ''),
            'snippet': data.get('snippet', ''),
            'thread_id': data.get('threadId', '')
        }
    except Exception as e:
        log(f"Metadata error for {msg_id}: {e}")
        return None

# ── 6. Check existing HubSpot tasks to avoid duplicates ─────────────
log("Fetching existing HubSpot tasks with [Gmail★] prefix...")
search_payload = json.dumps({
    "filterGroups": [{
        "filters": [{
            "propertyName": "hs_task_subject",
            "operator": "CONTAINS_TOKEN",
            "value": "[Gmail"
        }]
    }],
    "properties": ["hs_task_subject"],
    "limit": 200
})
search_cmd = (
    f'curl -s -X POST "https://api.hubapi.com/crm/v3/objects/tasks/search" '
    f'-H "Authorization: Bearer {hubspot_token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{search_payload}\''
)
search_out, _, _ = run(search_cmd)
try:
    existing_tasks = json.loads(search_out)
    existing_subjects = set()
    for t in existing_tasks.get('results', []):
        subj = t.get('properties', {}).get('hs_task_subject', '')
        if '[Gmail' in subj:
            existing_subjects.add(subj)
    log(f"Existing HubSpot [Gmail★] tasks: {len(existing_subjects)}")
except Exception as e:
    log(f"Error fetching existing tasks: {e} | {search_out[:200]}")
    existing_subjects = set()

# ── 7. Parse email date to ISO ────────────────────────────────────────
from email.utils import parsedate_to_datetime

def parse_email_date(date_str):
    """Parse email Date header to ISO format."""
    if not date_str:
        return datetime.now().isoformat() + 'Z'
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except:
        try:
            # Try manual parse
            from email.utils import parsedate
            t = parsedate(date_str)
            if t:
                dt = datetime(*t[:6])
                return dt.isoformat()
        except:
            pass
    return datetime.now().isoformat() + 'Z'

# ── 8. Create HubSpot tasks for new emails ──────────────────────────
created = []
skipped = 0

for m in messages:
    msg_id = m['id']
    if msg_id in synced:
        log(f"  SKIP (already synced): {msg_id}")
        skipped += 1
        continue

    meta = get_metadata(msg_id)
    if not meta:
        skipped += 1
        continue

    # Check duplicate by subject
    task_subject = f"[Gmail ★] {meta['subject']}"
    if task_subject in existing_subjects:
        log(f"  SKIP (task exists in HubSpot): {meta['subject'][:60]}")
        synced.add(msg_id)
        with open(SYNC_FILE, 'a') as f:
            f.write(msg_id + '\n')
        skipped += 1
        continue

    # Parse date
    ts_iso = parse_email_date(meta['date'])

    # Build task body
    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{meta['thread_id']}"
    task_body = (
        f"From: {meta['from']}\n"
        f"Date: {meta['date']}\n\n"
        f"Snippet: {meta['snippet']}\n\n"
        f"View in Gmail: {gmail_link}\n"
        f"Gmail Message ID: {msg_id}"
    )

    if DRY_RUN:
        log(f"  DRY-RUN would create task: {task_subject[:60]}")
        created.append({'id': 'DRY-RUN', 'subject': meta['subject'], 'from': meta['from']})
        skipped += 1
        continue

    # Create task via HubSpot API
    task_payload = {
        "properties": {
            "hs_task_subject": task_subject,
            "hs_task_body": task_body,
            "hs_task_status": "NOT_STARTED",
            "hs_task_priority": "HIGH",
            "hs_timestamp": ts_iso
        }
    }

    payload_file = '/tmp/hubspot_task_payload.json'
    with open(payload_file, 'w') as f:
        json.dump(task_payload, f)

    create_cmd = (
        f'curl -s -X POST "https://api.hubapi.com/crm/v3/objects/tasks" '
        f'-H "Authorization: Bearer {hubspot_token}" '
        f'-H "Content-Type: application/json" '
        f'-d @{payload_file}'
    )
    create_out, _, create_rc = run(create_cmd)

    try:
        result = json.loads(create_out)
        if 'id' in result:
            log(f"  CREATED task: {result['id']} — {meta['subject'][:60]}")
            created.append({'id': result['id'], 'subject': meta['subject'], 'from': meta['from']})
            # Mark as synced
            synced.add(msg_id)
            with open(SYNC_FILE, 'a') as f:
                f.write(msg_id + '\n')
        elif 'error' in result:
            log(f"  ERROR creating task: {result['error']['message']}")
        else:
            log(f"  UNKNOWN response: {create_out[:200]}")
    except Exception as e:
        log(f"  EXCEPTION creating task: {e} | {create_out[:200]}")

# ── 9. Summary ───────────────────────────────────────────────────────
log("=== SYNC COMPLETE ===")
log(f"  Total starred found: {len(messages)}")
log(f"  Already synced:     {skipped}")
log(f"  New tasks created:  {len(created)}")

if created and not DRY_RUN and not NO_TELEGRAM:
    for c in created:
        log(f"    → {c['id']} | {c['subject'][:70]}")
    # Send telegram summary
    token_idx = hubspot_token.find('pat-na')
    safe_tok = hubspot_token[token_idx:token_idx+20] + '...' if token_idx >= 0 else '...'
    tg_text = (
        f"✅ *Gmail★ → HubSpot Sync Done*\n"
        f"📬 Starred emails (7d): {len(messages)}\n"
        f"🆕 Tasks created: {len(created)}\n"
        f"⏭️  Skipped (already synced): {skipped}\n\n"
        f"New tasks:\n"
    )
    for c in created:
        tg_text += f"• {c['subject'][:60]}\n"

    # Write temp file for curl
    tg_payload = json.dumps({'text': tg_text})
    with open('/tmp/tg_payload.json', 'w') as f:
        f.write(tg_payload)
    tg_cmd = (
        f'curl -s -X POST "https://api.telegram.org/bot6065174688:AAEh6LPTdd-WaSPmLYK_WXAeZK4lRdT6o_g/sendMessage" '
        f'-H "Content-Type: application/json" '
        f'-d @/tmp/tg_payload.json '
        f'-d chat_id=707620807'
    )
    tg_out, _, _ = run(tg_cmd)
    log(f"Telegram sent: {tg_out[:100]}")
else:
    log("No new tasks — skipping telegram notification.")
