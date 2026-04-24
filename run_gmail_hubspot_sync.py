#!/usr/bin/env python3
import subprocess, json, os, urllib.parse, urllib.request, base64, re
from datetime import datetime, timedelta

PYTHON = '/home/mauiclaw/.hermes/hermes-agent/venv/bin/python3'

# HubSpot token
env_content = open(os.path.expanduser('~/.hermes/.env')).read()
for line in env_content.splitlines():
    if line.startswith('export HUBSPOT_ACCESS_TOKEN='):
        HUBSPOT_TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")
        break
print(f"HubSpot token: {HUBSPOT_TOKEN[:15]}...")

# Gmail token refresh
TOKEN_FILE = os.path.expanduser('~/.hermes/google_token.json')
CLIENT_SECRET_PATH = os.path.expanduser('~/.hermes/google_client_secret.json')
with open(TOKEN_FILE) as f:
    tok = json.load(f)
with open(CLIENT_SECRET_PATH) as f:
    client = json.load(f)['installed']

data = urllib.parse.urlencode({
    'refresh_token': tok['refresh_token'],
    'client_id': client['client_id'],
    'client_secret': client['client_secret'],
    'grant_type': 'refresh_token'
}).encode()
req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
resp = urllib.request.urlopen(req, timeout=20)
new_token = json.loads(resp.read())['access_token']
tok['access_token'] = new_token
with open(TOKEN_FILE, 'w') as f:
    json.dump(tok, f, indent=2)
print(f"Gmail token refreshed: {len(new_token)} chars")

def gmail_api(endpoint, method='GET', data=None):
    cmd = ['curl', '-s', '-X', method,
           f'https://gmail.googleapis.com/gmail/v1{endpoint}',
           '-H', f'Authorization: Bearer {new_token}',
           '-H', 'Content-Type: application/json']
    if data:
        cmd += ['-d', json.dumps(data)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)

profile = gmail_api('/users/me/profile')
print(f"Gmail: {profile.get('emailAddress')} | {profile.get('messagesTotal')} msgs")

# HubSpot search existing Gmail tasks
def hubspot_search_tasks(subject_contains):
    payload = {
        "filterGroups": [{"filters": [{
            "propertyName": "hs_task_subject",
            "operator": "CONTAINS_TOKEN",
            "value": subject_contains
        }]}],
        "properties": ["hs_task_subject", "hs_task_body", "hs_timestamp"]
    }
    cmd = ['curl', '-s', '-X', 'POST',
        'https://api.hubapi.com/crm/v3/objects/tasks/search',
        '-H', f'Authorization: Bearer {HUBSPOT_TOKEN}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)

existing = hubspot_search_tasks('[Gmail')
existing_msg_ids = set()
if existing.get('results'):
    for t in existing['results']:
        body = t.get('properties', {}).get('hs_task_body', '')
        m = re.search(r'Gmail Message ID:\s*([^\s]+)', body)
        if m:
            existing_msg_ids.add(m.group(1))
print(f"Existing Gmail tasks in HubSpot: {len(existing_msg_ids)}")

# Synced file
SYNC_FILE = os.path.expanduser('~/ECONARES_WORKSPACE/synced_gmail_threads.txt')
try:
    with open(SYNC_FILE) as f:
        synced_ids = set(line.strip() for line in f if line.strip())
except FileNotFoundError:
    synced_ids = set()
print(f"Previously synced: {len(synced_ids)}")

# Search starred
now = datetime.now()
after_ts = int((now - timedelta(days=7)).timestamp())
print(f"Searching starred after: {after_ts}")

result = gmail_api(f'/users/me/messages?maxResults=50&q=is%3Astarred+is%3Aunread')
result_all = gmail_api(f'/users/me/messages?maxResults=50&q=is%3Astarred')
all_starred = {}
for m in result.get('messages', []):
    all_starred[m['id']] = m
for m in result_all.get('messages', []):
    all_starred[m['id']] = m
print(f"Total starred found: {len(all_starred)}")

HEADERS = ['From', 'Subject', 'Date', 'To']
METADATA_STR = '&'.join(f'metadataHeaders={h}' for h in HEADERS)

def get_msg_metadata(msg_id):
    msg = gmail_api(f'/users/me/messages/{msg_id}?format=metadata&{METADATA_STR}')
    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
    date_str = headers.get('Date', '')
    try:
        parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        try:
            parsed_date = datetime.strptime(date_str[:25], '%d %b %Y %H:%M:%S %z').strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            parsed_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    return {
        'id': msg_id,
        'from': headers.get('From', ''),
        'subject': headers.get('Subject', '(no subject)'),
        'date': headers.get('Date', ''),
        'date_iso': parsed_date,
        'snippet': msg.get('snippet', ''),
        'thread_id': msg.get('threadId', '')
    }

tasks_created = 0
errors = []

for msg_id in all_starred:
    if msg_id in synced_ids or msg_id in existing_msg_ids:
        print(f"  SKIP (already synced/exists): {msg_id}")
        synced_ids.add(msg_id)
        continue
    
    meta = get_msg_metadata(msg_id)
    
    # Check if within 7 days
    try:
        msg_time = datetime.strptime(meta['date'][:25], '%d %b %Y %H:%M:%S %z')
        if (now - msg_time.replace(tzinfo=None)) > timedelta(days=7):
            print(f"  SKIP (older than 7d): {msg_id} - {meta['date'][:20]}")
            synced_ids.add(msg_id)
            continue
    except Exception as e:
        print(f"  Date parse issue {msg_id}: {e}")
    
    task_body = (
        f"From: {meta['from']}\n"
        f"Date: {meta['date']}\n\n"
        f"Snippet: {meta['snippet']}\n\n"
        f"View in Gmail: https://mail.google.com/mail/u/0/#inbox/{meta['thread_id']}\n"
        f"Gmail Message ID: {msg_id}"
    )
    
    payload = {
        "properties": {
            "hs_task_subject": f"[Gmail ★] {meta['subject']}",
            "hs_task_body": task_body,
            "hs_task_status": "NOT_STARTED",
            "hs_task_priority": "HIGH",
            "hs_timestamp": meta['date_iso']
        }
    }
    
    r = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://api.hubapi.com/crm/v3/objects/tasks',
        '-H', f'Authorization: Bearer {HUBSPOT_TOKEN}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ], capture_output=True, text=True)
    
    result_hs = json.loads(r.stdout)
    if result_hs.get('id'):
        print(f"  CREATED {result_hs['id']}: {meta['subject'][:60]}")
        synced_ids.add(msg_id)
        with open(SYNC_FILE, 'a') as f:
            f.write(msg_id + '\n')
        tasks_created += 1
    else:
        err = f"  ERROR {msg_id}: {result_hs}"
        print(err)
        errors.append(err)

print(f"\n=== DONE: {tasks_created} created, {len(errors)} errors ===")

# Log
LOG_DIR = os.path.expanduser('~/ECONARES_WORKSPACE/logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'gmail_hubspot_sync.log')
with open(LOG_FILE, 'a') as f:
    f.write(f"\n--- {datetime.now().isoformat()} ---\n")
    f.write(f"Tasks: {tasks_created} | Starred: {len(all_starred)} | Errors: {len(errors)}\n")

# Telegram
if tasks_created > 0:
    TG_TOKEN = None
    TG_CHAT = '707620807'
    try:
        with open(os.path.expanduser('~/.hermes/.env')) as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    TG_TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    except:
        pass
    if TG_TOKEN:
        msg = f"Gmail Starred->HubSpot Sync\n\nTasks created: {tasks_created}\nStarred scanned: {len(all_starred)}\nErrors: {len(errors)}"
        subprocess.run([
            'curl', '-s', '-X', 'POST',
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            '-d', f'chat_id={TG_CHAT}&text={urllib.parse.quote(msg)}'
        ], capture_output=True)
        print("Telegram sent.")
else:
    print("No new tasks — skipping Telegram.")

print("Done.")
