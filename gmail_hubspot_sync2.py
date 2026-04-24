#!/usr/bin/env python3
import subprocess, json, os, urllib.parse
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# 1. REFRESH GMAIL TOKEN via curl (urllib.request unreliable in venv)
TOKEN_FILE = os.path.expanduser('~/.hermes/google_token.json')
CLIENT_SECRET_FILE = os.path.expanduser('~/.hermes/google_client_secret.json')

with open(TOKEN_FILE) as f:
    tok = json.load(f)
with open(CLIENT_SECRET_FILE) as f:
    cs = json.load(f)['installed']

refresh_result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://oauth2.googleapis.com/token',
    '-d', f'client_id={cs["client_id"]}&client_secret={cs["client_secret"]}&refresh_token={tok["refresh_token"]}&grant_type=refresh_token'
], capture_output=True, text=True)
new_token = json.loads(refresh_result.stdout)['access_token']
tok['access_token'] = new_token
with open(TOKEN_FILE, 'w') as f:
    json.dump(tok, f, indent=2)
print(f"Token refreshed: {new_token[:15]}...")

# 2. READ HUBSPOT TOKEN
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        if 'HUBSPOT' in line and 'TOKEN' in line:
            PAT = line.split('=', 1)[1].strip().strip('"').strip("'")
            break
print(f"HubSpot token: {PAT[:15]}...")

# 3. SEARCH STARRED EMAILS (last 7 days)
after_ts = int((datetime.now() - timedelta(days=7)).timestamp())
q = urllib.parse.quote(f"is:starred after:{after_ts}")
result = subprocess.run([
    'curl', '-s',
    f'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=50&q={q}',
    '-H', f'Authorization: Bearer {new_token}'
], capture_output=True, text=True)
messages = json.loads(result.stdout).get('messages', [])
print(f"Starred emails found: {len(messages)}")

# 4. READ SYNCED THREADS
SYNC_FILE = os.path.expanduser('~/ECONARES_WORKSPACE/synced_gmail_threads.txt')
LOG_FILE = os.path.expanduser('~/ECONARES_WORKSPACE/logs/gmail_hubspot_sync.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

synced_ids = set()
if os.path.exists(SYNC_FILE):
    with open(SYNC_FILE) as f:
        synced_ids = set(line.strip() for line in f if line.strip())
print(f"Already synced: {len(synced_ids)}")

# 5. DEDUP — check HubSpot for existing [Gmail *] tasks
search_payload = json.dumps({
    'filterGroups': [{'filters': [
        {'propertyName': 'hs_task_subject', 'operator': 'CONTAINS_TOKEN', 'value': '[Gmail'}
    ]}],
    'properties': ['hs_task_subject'],
    'limit': 100
})
r = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://api.hubapi.com/crm/v3/objects/tasks/search',
    '-H', f'Authorization: Bearer {PAT}',
    '-H', 'Content-Type: application/json',
    '-d', search_payload
], capture_output=True, text=True)
existing_tasks = json.loads(r.stdout).get('results', [])
hubspot_subjects = {t['properties']['hs_task_subject'] for t in existing_tasks}
print(f"Existing HubSpot [Gmail] tasks: {len(hubspot_subjects)}")

# 6. GET METADATA FOR NEW EMAILS & CREATE TASKS
new_tasks = 0
errors = []
created_subjects = []

for m in messages:
    msg_id = m['id']
    if msg_id in synced_ids:
        print(f"  SKIP (already synced): {msg_id}")
        continue

    meta = subprocess.run([
        'curl', '-s',
        f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date',
        '-H', f'Authorization: Bearer {new_token}'
    ], capture_output=True, text=True)
    try:
        msg_data = json.loads(meta.stdout)
    except:
        errors.append(f"FAIL parse {msg_id}")
        continue

    headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
    subject = headers.get('Subject', '(no subject)')
    sender = headers.get('From', '')
    date = headers.get('Date', '')
    snippet = msg_data.get('snippet', '')
    thread_id = msg_data.get('threadId', '')

    task_subject = f"[Gmail *] {subject}"
    if task_subject in hubspot_subjects:
        print(f"  SKIP (exists in HubSpot): {subject[:60]}")
        with open(SYNC_FILE, 'a') as f:
            f.write(msg_id + '\n')
        continue

    try:
        dt = parsedate_to_datetime(date)
        hs_timestamp = dt.isoformat()
    except:
        hs_timestamp = datetime.now().isoformat()

    task_body = f"From: {sender}\nDate: {date}\n\nSnippet: {snippet}\n\nView in Gmail: https://mail.google.com/mail/u/0/#inbox/{thread_id}\nGmail Message ID: {msg_id}"

    task_payload = {
        'properties': {
            'hs_task_subject': task_subject,
            'hs_task_body': task_body,
            'hs_task_status': 'NOT_STARTED',
            'hs_task_priority': 'HIGH',
            'hs_timestamp': hs_timestamp
        }
    }

    with open('/tmp/hubspot_task.json', 'w') as f:
        json.dump(task_payload, f)

    r = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://api.hubapi.com/crm/v3/objects/tasks',
        '-H', f'Authorization: Bearer {PAT}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/hubspot_task.json'
    ], capture_output=True, text=True)

    result = json.loads(r.stdout)
    if 'id' in result:
        new_tasks += 1
        created_subjects.append(subject)
        with open(SYNC_FILE, 'a') as f:
            f.write(msg_id + '\n')
        print(f"  CREATED task: {subject[:60]}")
    else:
        err_msg = f"Task fail {msg_id}: {result}"
        errors.append(err_msg)
        print(f"  {err_msg}")

# 7. LOG RESULTS
timestamp = datetime.now().isoformat()
log_entry = f"[{timestamp}] Starred: {len(messages)}, New tasks: {new_tasks}, Errors: {len(errors)}\n"
if created_subjects:
    log_entry += "  Created: " + "; ".join(created_subjects[:10]) + "\n"
with open(LOG_FILE, 'a') as f:
    f.write(log_entry)

print(f"\nSummary: {new_tasks} tasks created, {len(errors)} errors")

# 8. TELEGRAM NOTIFY IF TASKS CREATED
if new_tasks > 0:
    subjects_preview = "; ".join(created_subjects[:5])
    tg_msg = f" Gmail-Starred to HubSpot Sync Done\nStarred found: {len(messages)}\nNew tasks: {new_tasks}\n{subjects_preview}"
    subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://api.telegram.org/bot7035193978:AAEQ4ejdkg_qfI9e2Q2U5en5U5en5U5en5/sendMessage',
        '-d', f'chat_id=707620807&text={urllib.parse.quote(tg_msg)}'
    ], capture_output=True)
    print("Telegram notification sent")
else:
    print("No new tasks -- skipping Telegram notification")

print("DONE")
