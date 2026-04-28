#!/usr/bin/env python3
"""ECONARES Morning Brief — Daily 7:30 AM PHT"""
import subprocess, json, datetime, os

PAT = None
try:
    with open(os.path.expanduser('/home/mauiclaw/.hermes/.env')) as f:
        for line in f:
            if line.startswith('export HUBSPOT_ACCESS_TOKEN'):
                PAT = line.split('"')[1].strip()
except: pass

def api_post(url, token, data):
    r = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json', '-d', json.dumps(data), url],
        capture_output=True, text=True, timeout=20)
    try: return json.loads(r.stdout)
    except: return {}

def api_get(url, token):
    r = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {token}', url],
        capture_output=True, text=True, timeout=20)
    try: return json.loads(r.stdout)
    except: return {}

today = datetime.datetime.utcnow()
today_str = today.strftime('%Y-%m-%d')
today_display = today.strftime('%B %d, %Y')

# ── TASKS NOT_STARTED ──────────────────────────────────────
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

# ── DEALS ──────────────────────────────────────────────────
deals_res = api_post('https://api.hubapi.com/crm/v3/objects/deals/search', PAT, {
    'filterGroups': [],
    'properties': ['dealname', 'amount', 'dealstage', 'closedate'],
    'sorts': [{'propertyName': 'amount', 'direction': 'DESCENDING'}],
    'limit': 10
})
active_deals = [d for d in deals_res.get('results', []) if d['properties'].get('dealstage') != 'closedwon']
total_pipeline = sum(float(d['properties'].get('amount') or 0) for d in active_deals)

# ── THIS WEEK COMPLETED ────────────────────────────────────
week_start = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
week_res = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [
        {'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'COMPLETED'},
        {'propertyName': 'hs_lastmodifieddate', 'operator': 'GTE', 'value': week_start + 'T00:00:00Z'}
    ]}],
    'properties': ['hs_task_subject'],
    'limit': 10
})
completed_week = len(week_res.get('results', []))

# ── BUILD MESSAGE ─────────────────────────────────────────
lines = [
    f"GOOD MORNING, REYMARR",
    f"━━━━━━━━━━━━━━━━━━━━",
    f"",
    f"{today_display} | 7:30 AM PHT",
    f"",
    f"OVERVIEW:",
    f"  Active deals: {len(active_deals)} | Pipeline: ${total_pipeline:,.0f} USD",
    f"  Tasks completed this week: {completed_week}",
    f"  Active tasks in HubSpot: {len(all_active)}",
    f"",
]
if overdue:
    lines.append(f"OVERDUE ({len(overdue)}):")
    for t in overdue[:10]:
        lines.append(f"  [{t['properties'].get('hs_task_status','N/A')}] {t['properties'].get('hs_task_subject','N/A')}")
    lines.append("")
if due_today:
    lines.append(f"DUE TODAY ({len(due_today)}):")
    for t in due_today:
        lines.append(f"  {t['properties'].get('hs_task_subject','N/A')}")
    lines.append("")
if not overdue and not due_today:
    lines.append("No overdue or due-today tasks.")
    lines.append("")

lines += [
    "POWER SECTOR FOCUS — Cebu Cluster:",
    "  CEDC, Therma Visayas, AboitizPower, KEPCO-Salcon",
    "",
    "TOMORROW: Follow up China Nickel (Tsingshan, YNQSGT)",
]
msg = "\n".join(lines)
print(msg)

# ── TELEGRAM ─────────────────────────────────────────────
bot_token = os.getenv('HERMES_TELEGRAM_BOT_TOKEN', '')
chat_id = '707620807'
if bot_token and msg:
    tg = subprocess.run(['curl', '-s', '-X', 'POST',
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'chat_id': chat_id, 'text': msg})],
        capture_output=True, text=True, timeout=15)
    print(f"\nTelegram: {tg.stdout[:100]}")
