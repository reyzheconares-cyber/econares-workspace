#!/usr/bin/env python3
"""ECONARES Evening DSR — FIXED: Uses notes as "completed today" activity log"""
import subprocess, json, datetime, os, base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

PAT = None
GMAIL_TOKEN = None
try:
    with open(os.path.expanduser('/home/mauiclaw/.hermes/.env')) as f:
        for line in f:
            if line.startswith('export HUBSPOT_ACCESS_TOKEN'):
                PAT = line.split('"')[1].strip()
except: pass
try:
    with open(os.path.expanduser('/home/mauiclaw/.hermes/google_token.json')) as f:
        GMAIL_TOKEN = json.load(f).get('access_token')
except: pass

def api_post(url, token, data):
    r = subprocess.run(['curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(data), url],
        capture_output=True, text=True, timeout=20)
    try: return json.loads(r.stdout)
    except: return {}

today = datetime.datetime.utcnow()
today_str = today.strftime('%Y-%m-%d')
today_display = today.strftime('%B %d, %Y')

# ── COMPLETED TODAY: Notes created today (our outreach activities) ──
notes_res = api_post('https://api.hubapi.com/crm/v3/objects/notes/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'createdate', 'operator': 'GTE', 'value': today_str + 'T00:00:00Z'}]}],
    'properties': ['hs_note_body', 'createdate'],
    'limit': 50
})
completed_today = []
for n in notes_res.get('results', []):
    body = n['properties'].get('hs_note_body', '')
    first_line = body.strip().split('\n')[0][:80]
    if first_line: completed_today.append(first_line)

# Backup: also count actual task completions
tasks_res = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'COMPLETED'}]}],
    'properties': ['hs_task_subject', 'hs_lastmodifieddate'],
    'sorts': [{'propertyName': 'hs_lastmodifieddate', 'direction': 'DESCENDING'}],
    'limit': 20
})
for t in tasks_res.get('results', []):
    modified = (t['properties'].get('hs_lastmodifieddate') or '')[:10]
    if modified == today_str:
        subj = t['properties'].get('hs_task_subject', 'N/A')
        if subj not in completed_today:
            completed_today.append(subj)

# ── ACTIVE TASKS ────────────────────────────────────────────────
not_started = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'NOT_STARTED'}]}],
    'properties': ['hs_task_subject', 'hs_timestamp', 'hs_task_status'],
    'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'ASCENDING'}],
    'limit': 30
})
in_progress = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'IN_PROGRESS'}]}],
    'properties': ['hs_task_subject', 'hs_timestamp', 'hs_task_status'],
    'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'ASCENDING'}],
    'limit': 30
})
all_active = not_started.get('results', []) + in_progress.get('results', [])
due_today = [t for t in all_active if (t['properties'].get('hs_timestamp') or '')[:10] == today_str]
overdue = [t for t in all_active if (t['properties'].get('hs_timestamp') or '')[:10] < today_str and (t['properties'].get('hs_timestamp') or '')[:10] != '']

# ── ACTIVE DEALS ────────────────────────────────────────────────
deals_res = api_post('https://api.hubapi.com/crm/v3/objects/deals/search', PAT, {
    'filterGroups': [],
    'properties': ['dealname', 'amount', 'dealstage', 'closedate'],
    'sorts': [{'propertyName': 'amount', 'direction': 'DESCENDING'}],
    'limit': 10
})
active_deals = [d for d in deals_res.get('results', []) if d['properties'].get('dealstage') != 'closedwon']
total_pipeline = sum(float(d['properties'].get('amount') or 0) for d in active_deals)

# ── NEW CONTACTS TODAY ────────────────────────────────────────────
contacts_res = api_post('https://api.hubapi.com/crm/v3/objects/contacts/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'createdate', 'operator': 'GTE', 'value': today_str + 'T00:00:00Z'}]}],
    'properties': ['firstname', 'lastname', 'company', 'email'],
    'limit': 20
})
new_contacts = []
for c in contacts_res.get('results', []):
    p = c['properties']
    name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or 'N/A'
    new_contacts.append(f"  - {name} | {p.get('company','N/A')} | {p.get('email','N/A')}")

# ── BUILD DSR TEXT ───────────────────────────────────────────────
dsr_lines = [f"COMPLETED TODAY ({today_display}):"]
if completed_today:
    for t in completed_today: dsr_lines.append(f"  - {t}")
else:
    dsr_lines.append("  - No activities recorded today.")

dsr_lines += ["", "PIPELINE SNAPSHOT:", f"  Active deals: {len(active_deals)} | Total pipeline: ${total_pipeline:,.0f} USD"]
for d in active_deals:
    p = d['properties']
    amt = float(p.get('amount') or 0)
    dsr_lines.append(f"  - {p.get('dealname')} | ${amt:,.0f} USD | Close: {p.get('closedate','')[:10]}")

dsr_lines += ["", "NEW CONTACTS TODAY:"]
if new_contacts: dsr_lines.extend(new_contacts)
else: dsr_lines.append("  - No new contacts today.")

dsr_lines += ["", f"PENDING TASKS — Active: {len(all_active)} | Overdue: {len(overdue)} | Due Today: {len(due_today)}:"]
if overdue:
    dsr_lines.append("  OVERDUE:")
    for t in overdue: dsr_lines.append(f"    - {t['properties'].get('hs_task_subject')}")
if due_today:
    dsr_lines.append("  DUE TODAY:")
    for t in due_today: dsr_lines.append(f"    - {t['properties'].get('hs_task_subject')}")
dsr_lines += ["", "TOMORROW'S ACTION PLAN:", "  [Fill in each morning]"]

dsr_plain = "\n".join(dsr_lines)

# ── BUILD HTML ───────────────────────────────────────────────────
active_list_html = "".join(f"<li>{d['properties'].get('dealname')} | ${float(d['properties'].get('amount') or 0):,.0f} USD | Close: {d['properties'].get('closedate','')[:10]}</li>" for d in active_deals)
completed_html = "".join(f"<li>{t}</li>" for t in completed_today) if completed_today else "<li>No activities recorded today.</li>"
contacts_html = "".join(f"<li>{c}</li>" for c in new_contacts) if new_contacts else "<li>No new contacts today.</li>"
overdue_html = "".join(f"<li>{t['properties'].get('hs_task_subject')}</li>" for t in overdue) if overdue else ""
due_today_html = "".join(f"<li>{t['properties'].get('hs_task_subject')}</li>" for t in due_today) if due_today else ""

html_body = f"""<html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
<p>Dear Ma'am/Sir Eleizer,</p>
<p>Please see below the Daily Sales Report for <strong>{today_display}</strong>.</p>
<hr style="border: 1px solid #eee; margin: 20px 0;">
<h2 style="color: #e67e22;">COMPLETED TODAY</h2><ul>{completed_html}</ul>
<hr style="border: 1px solid #eee; margin: 20px 0;">
<h2 style="color: #e67e22;">PIPELINE SNAPSHOT</h2>
<p><strong>Active deals:</strong> {len(active_deals)} | <strong>Total pipeline:</strong> ${total_pipeline:,.0f} USD</p>
<ul>{active_list_html}</ul>
<hr style="border: 1px solid #eee; margin: 20px 0;">
<h2 style="color: #e67e22;">NEW CONTACTS TODAY</h2><ul>{contacts_html}</ul>
<hr style="border: 1px solid #eee; margin: 20px 0;">
<h2 style="color: #e67e22;">PENDING TASKS</h2>
<p>Active: {len(all_active)} | Overdue: {len(overdue)} | Due Today: {len(due_today)}</p>
{overdue_html and f'<p><strong>Overdue:</strong><ul>{overdue_html}</ul></p>' or ''}
{due_today_html and f'<p><strong>Due Today:</strong><ul>{due_today_html}</ul></p>' or ''}
<hr style="border: 1px solid #eee; margin: 20px 0;">
<h2 style="color: #e67e22;">TOMORROW'S ACTION PLAN</h2>
<p>[To be filled by RZH each morning]</p>
<hr style="border: 1px solid #eee; margin: 20px 0;">
<p><strong>Reymarr Hijara (RZH)</strong><br>Sales and Marketing Officer | <strong>ECONARES</strong><br>reyzh.econares@gmail.com | +639278725194 | WhatsApp/Telegram/Viber</p>
</body></html>"""

# ── GMAIL DRAFT ──────────────────────────────────────────────────
gmail_status = "Gmail OAuth disabled — draft not created"
draft_id = "N/A"
if GMAIL_TOKEN:
    msg = MIMEMultipart('alternative')
    msg['to'] = 'ece.eleguinresources@yahoo.com'
    msg['subject'] = f'Daily Sales Report — {today_display} | ECONARES'
    msg.attach(MIMEText(dsr_plain, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode().replace('/', '_').replace('+', '-').rstrip('=')
    draft_res = subprocess.run(['curl', '-s', '-X', 'POST',
        'https://gmail.googleapis.com/gmail/v1/users/me/drafts',
        '-H', f'Authorization: Bearer {GMAIL_TOKEN}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'message': {'raw': raw}})],
        capture_output=True, text=True, timeout=20)
    result = json.loads(draft_res.stdout)
    draft_id = result.get('id', 'N/A')
    gmail_status = f"Draft created: {draft_id}" if draft_id != 'N/A' else "Draft failed"
else:
    gmail_status = "Gmail OAuth disabled — draft not created"

print(dsr_plain)
print(f"\nGMAIL STATUS: {gmail_status}")

# ── TELEGRAM ─────────────────────────────────────────────────────
bot_token = os.getenv('HERMES_TELEGRAM_BOT_TOKEN', '')
chat_id = '707620807'
if bot_token:
    tele_lines = [
        f"DSR — {today_display}",
        f"────────────────────────────",
        f"Completed today: {len(completed_today)}",
        f"New contacts: {len(new_contacts)}",
        f"Pipeline: ${total_pipeline:,.0f} USD",
        f"Active tasks: {len(all_active)} | Overdue: {len(overdue)} | Due today: {len(due_today)}",
        f"Gmail: {gmail_status}",
    ]
    tg = subprocess.run(['curl', '-s', '-X', 'POST',
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'chat_id': chat_id, 'text': "\n".join(tele_lines)})],
        capture_output=True, text=True, timeout=15)
    print(f"Telegram: {tg.stdout[:100]}")
