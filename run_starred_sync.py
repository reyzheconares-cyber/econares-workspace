#!/usr/bin/env python3
import subprocess
import json
import os
from datetime import datetime, timedelta

TOKEN_FILE = os.path.expanduser('~/.hermes/google_token.json')
CLIENT_SECRET_FILE = os.path.expanduser('~/.hermes/google_client_secret.json')
ENV_FILE = os.path.expanduser('~/.hermes/.env')
SYNCED_FILE = os.path.expanduser('~/ECONARES_WORKSPACE/synced_gmail_threads.txt')
LOG_DIR = os.path.expanduser('~/ECONARES_WORKSPACE/logs')
LOG_FILE = os.path.join(LOG_DIR, 'gmail_hubspot_sync.log')

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def refresh_gmail_token():
    with open(TOKEN_FILE) as f:
        token = json.load(f)
    with open(CLIENT_SECRET_FILE) as f:
        client = json.load(f)['installed']
    cmd = ['curl', '-s', '-X', 'POST', 'https://oauth2.googleapis.com/token',
           '-d', f"client_id={client['client_id']}&client_secret={client['client_secret']}&refresh_token={token['refresh_token']}&grant_type=refresh_token"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    new_data = json.loads(result.stdout)
    if 'access_token' in new_data:
        token['access_token'] = new_data['access_token']
        token['expires_in'] = new_data.get('expires_in', 3599)
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token, f)
        log(f"Gmail token refreshed")
        return new_data['access_token']
    log(f"ERROR refreshing: {new_data}")
    return None

def get_hubspot_token():
    with open(ENV_FILE) as f:
        for line in f:
            if 'HUBSPOT_ACCESS_TOKEN' in line:
                tok = line.split('=', 1)[1].strip().strip('"').strip("'")
                if tok.startswith('export '):
                    tok = tok[7:].strip().strip('"').strip("'")
                return tok
    return None

def gmail_api(endpoint, token, method='GET'):
    cmd = ['curl', '-s', '-X', method,
           f'https://gmail.googleapis.com/gmail/v1{endpoint}',
           '-H', f'Authorization: Bearer {token}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

HEADERS = ['From', 'Subject', 'Date', 'To', 'Cc']
METADATA_STR = '&'.join(f'metadataHeaders={h}' for h in HEADERS)

def get_msg_metadata(token, msg_id):
    msg = gmail_api(f'/users/me/messages/{msg_id}?format=metadata&{METADATA_STR}', token)
    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
    return {
        'id': msg_id,
        'from': headers.get('From', ''),
        'subject': headers.get('Subject', '(no subject)'),
        'date': headers.get('Date', ''),
        'snippet': msg.get('snippet', ''),
        'thread_id': msg.get('threadId', '')
    }

def get_synced_ids():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def get_existing_task_subjects(hs_token):
    query = {"filterGroups": [{"filters": [{"propertyName": "hs_task_subject", "operator": "CONTAINS_TOKEN", "value": "[Gmail"}]}]}
    cmd = ['curl', '-s', '-X', 'POST', 'https://api.hubapi.com/crm/v3/objects/tasks/search',
           '-H', f'Authorization: Bearer {hs_token}', '-H', 'Content-Type: application/json',
           '-d', json.dumps(query)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    subjects = set()
    for t in data.get('results', []):
        subj = t.get('properties', {}).get('hs_task_subject', '')
        if '[Gmail ' in subj:
            subjects.add(subj)
    return subjects

def create_hubspot_task(hs_token, subject, body, timestamp):
    try:
        dt = datetime.strptime(timestamp[:25], '%a, %d %b %Y %H:%M:%S')
        iso_ts = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        iso_ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    task_data = {"properties": {"hs_task_subject": subject, "hs_task_body": body,
                               "hs_task_status": "NOT_STARTED", "hs_task_priority": "HIGH",
                               "hs_timestamp": iso_ts}}
    payload_file = '/tmp/hubspot_task.json'
    with open(payload_file, 'w') as f:
        json.dump(task_data, f)
    cmd = ['curl', '-s', '-X', 'POST', 'https://api.hubapi.com/crm/v3/objects/tasks',
           '-H', f'Authorization: Bearer {hs_token}', '-H', 'Content-Type: application/json',
           '-d', f'@{payload_file}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    resp = json.loads(result.stdout)
    return (resp.get('id'), resp) if 'id' in resp else (None, resp)

def send_telegram(message):
    bot_token = None
    chat_id = '707620807'
    with open(ENV_FILE) as f:
        for line in f:
            if 'TELEGRAM_BOT_TOKEN' in line:
                bot_token = line.split('=', 1)[1].strip().strip('"').strip("'")
                if bot_token.startswith('export '):
                    bot_token = bot_token[7:].strip().strip('"').strip("'")
                break
    if not bot_token:
        log("Telegram token not found")
        return
    import urllib.request, urllib.parse
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message}).encode()
    req = urllib.request.Request(f'https://api.telegram.org/bot{bot_token}/sendMessage', data=data, method='POST')
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        log(f"Telegram sent OK")
    except Exception as e:
        log(f"Telegram error: {e}")

def main():
    log("=== Gmail Starred -> HubSpot Sync Started ===")
    gmail_token = refresh_gmail_token()
    if not gmail_token:
        log("FATAL: Could not refresh Gmail token")
        return
    hs_token = get_hubspot_token()
    if not hs_token:
        log("FATAL: HubSpot token not found")
        return
    synced_ids = get_synced_ids()
    log(f"Already synced: {len(synced_ids)} IDs")
    existing_subjects = get_existing_task_subjects(hs_token)
    log(f"Existing HubSpot Gmail tasks: {len(existing_subjects)}")
    after_ts = int((datetime.now() - timedelta(days=7)).timestamp())
    q = f"is:starred after:{after_ts}"
    log(f"Searching: {q}")
    result = gmail_api(f'/users/me/messages?maxResults=50&q={q}', gmail_token)
    msgs = result.get('messages', [])
    log(f"Found {len(msgs)} starred emails in last 7 days")
    created = []
    skipped = 0
    errors = 0
    for m in msgs:
        msg_id = m['id']
        if msg_id in synced_ids:
            log(f"  SKIP (synced): {msg_id}")
            skipped += 1
            continue
        meta = get_msg_metadata(gmail_token, msg_id)
        subject = meta['subject']
        task_subject = f"[Gmail] {subject}"
        if task_subject in existing_subjects:
            log(f"  SKIP (in HubSpot): {subject[:60]}")
            skipped += 1
            with open(SYNCED_FILE, 'a') as f:
                f.write(msg_id + '\n')
            continue
        body = f"From: {meta['from']}\nDate: {meta['date']}\n\nSnippet: {meta['snippet']}\n\nView in Gmail: https://mail.google.com/mail/u/0/#inbox/{meta['thread_id']}\nGmail Message ID: {msg_id}"
        task_id, task_resp = create_hubspot_task(hs_token, task_subject, body, meta['date'])
        if task_id:
            log(f"  CREATED {task_id}: {subject[:60]}")
            created.append({'id': task_id, 'subject': subject, 'msg_id': msg_id})
            with open(SYNCED_FILE, 'a') as f:
                f.write(msg_id + '\n')
        else:
            log(f"  ERROR: {task_resp}")
            errors += 1
    log(f"=== Done: Created={len(created)} Skipped={skipped} Errors={errors} ===")
    if created:
        summary = f"*Gmail->HubSpot Sync*\n\nCreated {len(created)} tasks:\n"
        for c in created:
            summary += f"• {c['subject'][:70]}\n"
        send_telegram(summary)
    else:
        log("No new tasks — no Telegram message.")

if __name__ == '__main__':
    main()
