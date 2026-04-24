#!/usr/bin/env python3
"""ECONARES Morning Brief — Enhanced with contacts, outreach, commodity prices, tomorrow's actions"""
import subprocess, json, datetime, os, re

# Load tokens
PAT = None
TAVILY_KEY = None
TELEGRAM_BOT_TOKEN = None
try:
    with open(os.path.expanduser('/home/mauiclaw/.hermes/.env')) as f:
        for line in f:
            if line.startswith('export HUBSPOT_ACCESS_TOKEN'):
                PAT = line.split('"')[1].strip()
            elif line.startswith('TAVILY_API_KEY'):
                TAVILY_KEY = line.split('=')[1].strip()
            elif line.startswith('TELEGRAM_BOT_TOKEN'):
                TELEGRAM_BOT_TOKEN = line.split('=')[1].strip()
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
yesterday = today - datetime.timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')
tomorrow = today + datetime.timedelta(days=1)
tomorrow_str = tomorrow.strftime('%Y-%m-%d')
today_display = today.strftime('%B %d, %Y')

# ── YESTERDAY'S NEW CONTACTS ─────────────────────────────────────
new_contacts = api_post('https://api.hubapi.com/crm/v3/objects/contacts/search', PAT, {
    'filterGroups': [{'filters': [
        {'propertyName': 'createdate', 'operator': 'GTE', 'value': yesterday_str + 'T00:00:00Z'},
        {'propertyName': 'createdate', 'operator': 'LTE', 'value': yesterday_str + 'T23:59:59Z'}
    ]}],
    'properties': ['firstname', 'lastname', 'email', 'phone', 'jobtitle', 'company'],
    'limit': 20
})
contacts_list = new_contacts.get('results', [])

# ── YESTERDAY'S OUTREACH (notes, emails, calls) ────────────────
# Query engagements from yesterday
engagements = api_post('https://api.hubapi.com/crm/v3/objects/notes/search', PAT, {
    'filterGroups': [{'filters': [
        {'propertyName': 'hs_timestamp', 'operator': 'GTE', 'value': yesterday_str + 'T00:00:00Z'},
        {'propertyName': 'hs_timestamp', 'operator': 'LTE', 'value': yesterday_str + 'T23:59:59Z'}
    ]}],
    'properties': ['hs_note_body', 'hs_timestamp'],
    'limit': 10
})
outreach_notes = engagements.get('results', [])

# ── TASKS: OVERDUE, TODAY, TOMORROW ─────────────────────────────
not_started = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'NOT_STARTED'}]}],
    'properties': ['hs_task_subject', 'hs_timestamp', 'hs_task_status'],
    'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'ASCENDING'}],
    'limit': 50
})
in_progress = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [{'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'IN_PROGRESS'}]}],
    'properties': ['hs_task_subject', 'hs_timestamp', 'hs_task_status'],
    'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'ASCENDING'}],
    'limit': 50
})
all_active = not_started.get('results', []) + in_progress.get('results', [])

due_today = [t for t in all_active if (t['properties'].get('hs_timestamp') or '')[:10] == today_str]
overdue = [t for t in all_active if (t['properties'].get('hs_timestamp') or '')[:10] < today_str and (t['properties'].get('hs_timestamp') or '')[:10] != '']
due_tomorrow = [t for t in all_active if (t['properties'].get('hs_timestamp') or '')[:10] == tomorrow_str]

# ── DEALS ───────────────────────────────────────────────────────
deals_res = api_post('https://api.hubapi.com/crm/v3/objects/deals/search', PAT, {
    'filterGroups': [],
    'properties': ['dealname', 'amount', 'dealstage', 'closedate'],
    'sorts': [{'propertyName': 'amount', 'direction': 'DESCENDING'}],
    'limit': 10
})
active_deals = [d for d in deals_res.get('results', []) if d['properties'].get('dealstage') != 'closedwon']
total_pipeline = sum(float(d['properties'].get('amount') or 0) for d in active_deals)

# ── THIS WEEK COMPLETED ────────────────────────────────────────
week_start = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
week_res = api_post('https://api.hubapi.com/crm/v3/objects/tasks/search', PAT, {
    'filterGroups': [{'filters': [
        {'propertyName': 'hs_task_status', 'operator': 'EQ', 'value': 'COMPLETED'},
        {'propertyName': 'hs_lastmodifieddate', 'operator': 'GTE', 'value': week_start + 'T00:00:00Z'}
    ]}],
    'properties': ['hs_task_subject'],
    'limit': 20
})
completed_week = len(week_res.get('results', []))

# ── COMMODITY PRICES (Tavily) ────────────────────────────────────
commodity_data = {}
if TAVILY_KEY:
    commodities = ['nickel ore price', 'copper ore price', 'coal thermal price', 'diesel price Asia']
    for cmd in commodities:
        try:
            r = subprocess.run(['curl', '-s', '-H', f'X-Api-Key: {TAVILY_KEY}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({'query': cmd, 'max_results': 3}),
                'https://api.tavily.com/search'],
                capture_output=True, text=True, timeout=15)
            result = json.loads(r.stdout)
            # Extract snippet from first result
            if result.get('results'):
                snippet = result['results'][0].get('content', '')[:120]
                commodity_data[cmd] = snippet
        except:
            pass

# ── BUILD MESSAGE ──────────────────────────────────────────────
lines = [
    f"GOOD MORNING, REYMARR",
    f"{'━' * 22}",
    f"",
    f"{today_display} | 7:30 AM PHT",
    f"",
    f"📊 OVERVIEW:",
    f"  Active deals: {len(active_deals)} | Pipeline: ${total_pipeline:,.0f} USD",
    f"  Tasks completed this week: {completed_week}",
    f"  Active tasks in HubSpot: {len(all_active)}",
    f"",
]

# Yesterday's new contacts
if contacts_list:
    lines.append(f"📇 YESTERDAY'S NEW CONTACTS ({len(contacts_list)}):")
    for c in contacts_list[:5]:
        name = f"{c['properties'].get('firstname','')} {c['properties'].get('lastname','')}".strip()
        company = c['properties'].get('company', '')
        title = c['properties'].get('jobtitle', '')
        lines.append(f"  • {name}" + (f" | {title}" if title else "") + (f" @ {company}" if company else ""))
    if len(contacts_list) > 5:
        lines.append(f"  ...and {len(contacts_list)-5} more")
    lines.append("")
else:
    lines.append("📇 YESTERDAY'S NEW CONTACTS: None")
    lines.append("")

# Yesterday's outreach
if outreach_notes:
    lines.append(f"📝 YESTERDAY'S OUTREACH ({len(outreach_notes)} activities):")
    for n in outreach_notes[:5]:
        body = n['properties'].get('hs_note_body', '')
        # Clean HTML tags
        body = re.sub(r'<[^>]+>', '', body)[:100]
        if body:
            lines.append(f"  • {body}")
    lines.append("")
else:
    lines.append("📝 YESTERDAY'S OUTREACH: No logged activities")
    lines.append("")

# Commodity prices
if commodity_data:
    lines.append("📈 COMMODITY SNAPSHOT:")
    for cmd, info in commodity_data.items():
        # Shorten commodity name
        short_name = cmd.replace(' price', '').replace(' ore', '').title()
        lines.append(f"  • {short_name}: {info}")
    lines.append("")

# Tasks
if overdue:
    lines.append(f"⚠️ OVERDUE ({len(overdue)}):")
    for t in overdue[:5]:
        lines.append(f"  [{t['properties'].get('hs_task_status','N/A')}] {t['properties'].get('hs_task_subject','N/A')}")
    lines.append("")

if due_today:
    lines.append(f"✅ DUE TODAY ({len(due_today)}):")
    for t in due_today:
        lines.append(f"  • {t['properties'].get('hs_task_subject','N/A')}")
    lines.append("")

if not overdue and not due_today:
    lines.append("No overdue or due-today tasks.")
    lines.append("")

# TOMORROW ACTION PLAN
if due_tomorrow:
    lines.append(f"📅 TOMORROW'S ACTION PLAN ({len(due_tomorrow)}):")
    for t in due_tomorrow:
        lines.append(f"  • {t['properties'].get('hs_task_subject','N/A')}")
else:
    lines.append("📅 TOMORROW'S ACTION PLAN: No tasks scheduled")

lines += [
    "",
    "POWER SECTOR FOCUS — Cebu Cluster:",
    "  CEDC, Therma Visayas, AboitizPower, KEPCO-Salcon",
]

msg = "\n".join(lines)
print(msg)

# ── TELEGRAM ──────────────────────────────────────────────────
chat_id = '707620807'
if TELEGRAM_BOT_TOKEN and msg:
    tg = subprocess.run(['curl', '-s', '-X', 'POST',
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'chat_id': chat_id, 'text': msg})],
        capture_output=True, text=True, timeout=15)
    print(f"\nTelegram: {tg.stdout[:100]}")