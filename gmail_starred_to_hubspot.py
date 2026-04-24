#!/usr/bin/env python3
"""
gmail_starred_to_hubspot.py
Syncs Gmail starred emails (or label-matched emails) to HubSpot tasks.
Run: python3 gmail_starred_to_hubspot.py [--dry-run] [--days N] [--label Name]
"""

import subprocess, json, os, sys, base64, urllib.request, urllib.parse, argparse, re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

HERMES_HOME = os.path.expanduser("~/.hermes")
TOKEN_FILE  = os.path.join(HERMES_HOME, "google_token.json")
CLIENT_FILE = os.path.join(HERMES_HOME, "google_client_secret.json")
ENV_FILE    = os.path.join(HERMES_HOME, ".env")
WORKSPACE   = os.path.expanduser("~/ECONARES_WORKSPACE")
SYNC_DB     = os.path.join(WORKSPACE, "synced_gmail_threads.txt")
VENV_PY     = "/home/mauiclaw/.hermes/hermes-agent/venv/bin/python3"

os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(os.path.join(WORKSPACE, "logs"), exist_ok=True)

def refresh_gmail_token():
    with open(TOKEN_FILE) as f: tok = json.load(f)
    with open(CLIENT_FILE) as f: client = json.load(f)
    installed = client.get("installed", {})
    data = urllib.parse.urlencode({
        "refresh_token": tok["refresh_token"],
        "client_id":     installed["client_id"],
        "client_secret": installed["client_secret"],
        "grant_type":     "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = urllib.request.urlopen(req, timeout=15)
    new_tok = json.loads(resp.read())
    tok["access_token"] = new_tok["access_token"]
    tok["expires_in"]   = new_tok["expires_in"]
    with open(TOKEN_FILE, "w") as f: json.dump(tok, f, indent=2)
    return tok["access_token"]

def get_hubspot_token():
    with open(ENV_FILE) as f:
        for line in f:
            # Handle "export HUBSPOT_ACCESS_TOKEN=..." and "HUBSPOT_ACCESS_TOKEN=..."
            line = line.strip()
            if "HUBSPOT_ACCESS_TOKEN" in line and "=" in line:
                val = line.split("=", 1)[1].strip().strip('"').strip("'").strip()
                if val and val != "***":
                    return val
    raise RuntimeError("HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env")

def curl_gmail(url):
    with open(TOKEN_FILE) as f: tok = json.load(f)
    out = subprocess.run(["curl", "-s", url,
        "-H", f"Authorization: Bearer {tok['access_token']}"],
        capture_output=True, text=True)
    return json.loads(out.stdout)

def curl_hubspot(method, endpoint, data=None):
    url = f"https://api.hubapi.com{endpoint}"
    token = get_hubspot_token()
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json"]
    if data:
        tmp = "/tmp/hubspot_payload.json"
        with open(tmp, "w") as f: json.dump(data, f)
        cmd += ["-d", f"@{tmp}"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(out.stdout) if out.stdout.strip() else {}

def get_gmail_token():
    with open(TOKEN_FILE) as f: tok = json.load(f)
    out = subprocess.run(["curl", "-s",
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        "-H", f"Authorization: Bearer {tok['access_token']}"],
        capture_output=True, text=True)
    resp = json.loads(out.stdout)
    if "emailAddress" in resp: return tok["access_token"]
    print("[TOKEN] Refreshing expired token...")
    return refresh_gmail_token()

def search_starred_emails(token, days=7, label_name=None):
    after_ts = int((datetime.now() - timedelta(days=days)).timestamp())
    if label_name:
        query = urllib.parse.quote(f"label:{label_name} after:{after_ts}")
    else:
        query = urllib.parse.quote(f"is:starred after:{after_ts}")
    METADATA_HEADERS = ["From", "Subject", "Date", "To"]
    meta_str = "&".join(f"metadataHeaders={h}" for h in METADATA_HEADERS)
    results = []
    page_token = None
    while True:
        params = {"maxResults": 50, "q": query}
        if page_token: params["pageToken"] = page_token
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        out = subprocess.run(["curl", "-s",
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{qs}",
            "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True)
        resp = json.loads(out.stdout)
        for m in resp.get("messages", []):
            detail = curl_gmail(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}?format=metadata&{meta_str}")
            headers = {h["name"]: h["value"]
                       for h in detail.get("payload", {}).get("headers", [])}
            snippet = detail.get("snippet", "")
            if len(snippet) > 200: snippet = snippet[:197] + "..."
            results.append({
                "id":        m["id"],
                "thread_id": m["threadId"],
                "from":      headers.get("From", ""),
                "subject":   headers.get("Subject", "(no subject)"),
                "date":      headers.get("Date", ""),
                "snippet":   snippet,
            })
        page_token = resp.get("nextPageToken")
        if not page_token: break
    return results

def create_hubspot_task(email_data):
    subject   = email_data["subject"]
    snippet   = email_data["snippet"]
    sender    = email_data["from"]
    date      = email_data["date"]
    thread_id = email_data["thread_id"]
    msg_id    = email_data["id"]
    try:
        dt = parsedate_to_datetime(date)
        hs_ts = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        hs_ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    task_body = (f"From: {sender}\nDate: {date}\n\nSnippet: {snippet}\n\n"
                 f"View in Gmail: https://mail.google.com/mail/u/0/#inbox/{thread_id}\n"
                 f"Gmail Message ID: {msg_id}")
    if len(task_body) > 1900: task_body = task_body[:1897] + "..."
    return curl_hubspot("POST", "/crm/v3/objects/tasks", {
        "properties": {
            "hs_task_subject": f"[Gmail ★] {subject}",
            "hs_task_body":    task_body,
            "hs_task_status":  "NOT_STARTED",
            "hs_task_priority": "HIGH",
            "hs_timestamp":    hs_ts,
        }
    })

def task_exists_for_thread(thread_id):
    payload = {
        "filterGroups": [{"filters": [{
            "propertyName": "hs_task_subject",
            "operator":     "CONTAINS_TOKEN",
            "value":        "[Gmail ★]",
        }]}],
        "properties": ["hs_task_subject"],
        "limit": 5,
    }
    result = curl_hubspot("POST", "/crm/v3/objects/tasks/search", payload)
    return len(result.get("results", [])) > 0

def load_synced():
    if not os.path.exists(SYNC_DB): return set()
    with open(SYNC_DB) as f:
        return {line.strip() for line in f if line.strip()}

def save_synced(msg_id):
    with open(SYNC_DB, "a") as f: f.write(msg_id + "\n")

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--days",    type=int, default=7)
    p.add_argument("--label",  type=str,  default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    log_path = os.path.join(WORKSPACE, "logs", "gmail_hubspot_sync.log")
    log = open(log_path, "a")
    log.write(f"\n{'='*60}\n")
    log.write(f"SYNC RUN: {datetime.now().isoformat()}\n")
    def plog(msg):
        print(msg); log.write(msg + "\n")

    try:
        token    = get_gmail_token()
        synced   = load_synced()
        plog(f"[OK] Gmail + HubSpot auth OK | Sync DB: {len(synced)} entries")

        mode = f"label:{args.label}" if args.label else "starred"
        emails = search_starred_emails(token, days=args.days, label_name=args.label)
        plog(f"[OK] Gmail search ({mode}, last {args.days}d): {len(emails)} found")

        to_sync = [e for e in emails
                   if e["id"] not in synced
                   and e["subject"] != "(no subject)"
                   and "Auto-Generated" not in e["subject"]]
        plog(f"[OK] After filter: {len(to_sync)} to sync")

        if not to_sync:
            plog("[INFO] Nothing new to sync."); return

        created, skipped, errors = 0, 0, 0
        for email in to_sync:
            plog(f"  -> [{email['id'][:12]}] {email['subject'][:55]}")
            if args.dry_run:
                plog(f"      [DRY RUN] Would create HubSpot task"); continue
            if task_exists_for_thread(email["thread_id"]):
                plog(f"      [SKIP] Task already exists"); save_synced(email["id"]); skipped += 1; continue
            result = create_hubspot_task(email)
            if "id" in result:
                plog(f"      [OK] Task created: {result['id']}"); save_synced(email["id"]); created += 1
            elif "error" in result:
                plog(f"      [ERROR] {result['error'].get('message', result)}"); errors += 1
            else:
                plog(f"      [WARN] {str(result)[:80]}"); errors += 1

        plog(f"\n[DONE] created={created} skipped={skipped} errors={errors}")
    except Exception as e:
        plog(f"[FATAL] {type(e).__name__}: {e}"); raise
    finally:
        log.close()

if __name__ == "__main__": main()
