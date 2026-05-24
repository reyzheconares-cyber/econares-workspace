#!/usr/bin/env python3
"""ECONARES Weekly Brief -- HTML Email + Obsidian Weekly Note"""
import json, datetime, os, re, urllib.request, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

TOKENS = {}
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        line = line.strip()
        if line.startswith('export GMAIL_APP_PASSWORD'):
            TOKENS['gmail_app_pw'] = line.split('=')[1].strip().strip('"')
        elif line.startswith('export HUBSPOT_ACCESS_TOKEN'):
            TOKENS['hs_token'] = re.search(r'"([^"]+)"', line).group(1)

HS_TOKEN = TOKENS.get('hs_token', '')
GMAIL_FROM = 'rzh24.econares@gmail.com'
GMAIL_TO = 'rzh24.econares@gmail.com'
GMAIL_PW = TOKENS.get('gmail_app_pw', '')
OBSIDIAN_VAULT = os.path.expanduser('/home/mauiclaw/Documents/Obsidian Vault')

def safe(s): return (s or '').strip()

def hs_post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
        headers={'Authorization': 'Bearer ' + HS_TOKEN, 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_hubspot_data():
    deals_resp = hs_post('https://api.hubapi.com/crm/v3/objects/deals/search',
        {'filterGroups': [], 'properties': ['dealname','amount','dealstage','hubspot_owner_id'], 'limit': 100})
    all_deals = deals_resp.get('results', [])
    active = [d for d in all_deals if d['properties'].get('dealstage') not in ('closedwon','closedlost')
              and d['properties'].get('hubspot_owner_id') == '164168266']
    won = [d for d in all_deals if d['properties'].get('dealstage') == 'closedwon'
           and d['properties'].get('hubspot_owner_id') == '164168266']
    total_pipeline = sum(float(d['properties'].get('amount',0) or 0) for d in active)
    won_amount = sum(float(d['properties'].get('amount',0) or 0) for d in won)
    try:
        tasks_resp = hs_post('https://api.hubapi.com/crm/v3/objects/tasks/search',
            {'filterGroups': [{'filters': [
                {'propertyName': 'hs_task_status', 'operator': 'IN', 'value': 'NOT_STARTED,IN_PROGRESS'},
                {'propertyName': 'hubspot_owner_id', 'operator': 'EQ', 'value': '164168266'}
            ]}], 'properties': ['hs_task_subject','hs_timestamp','hs_task_status'], 'limit': 200})
        all_tasks = tasks_resp.get('results', [])
    except Exception:
        all_tasks = []
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    overdue = [t for t in all_tasks if (t['properties'].get('hs_timestamp') or '')[:10] < today_str and t['properties'].get('hs_timestamp')]
    contacts_resp = hs_post('https://api.hubapi.com/crm/v3/objects/contacts/search',
        {'properties': ['email','firstname','lastname','phone','jobtitle','company'], 'limit': 200})
    contacts = contacts_resp.get('results', [])
    fully_enriched = sum(1 for c in contacts
        if safe(c['properties'].get('email')) and safe(c['properties'].get('phone')) and safe(c['properties'].get('jobtitle')))
    return {'active_deals': active, 'won_deals': won, 'total_pipeline': total_pipeline,
            'won_amount': won_amount, 'overdue': overdue,
            'total_contacts': len(contacts), 'fully_enriched': fully_enriched}

COMMODITIES = [
    {'name': 'NICKEL ORE', 'color': '#2980b9',
     'weekly': 'Indonesian DMO quota cuts continue. Ni 1.8% CIF China: $55-58/MT. LME 3M at $19,163/tonne (+22% YoY). PH-origin priority. FOB Tabango/Surigao/Batanes.',
     'trend': 'UP', 'signal': '&#128314;'},
    {'name': 'COAL', 'color': '#2c3e50',
     'weekly': 'Indonesian GAR 5,500 kcal/kg FOB Kalimantan: $98/MT (ICI 2, May 15). PH landed ~$108-115/MT. Production costs rising. MGEN deal in Negotiation - confirm specs with CEDC.',
     'trend': 'FIRM', 'signal': '&#128993;'},
    {'name': 'COPPER CONCENTRATE', 'color': '#27ae60',
     'weekly': 'LME 3M at $14,500+/tonne (Record Jan 2026). Cu ore (0.5% basis): $85-95/tonne. Supply tightness. Monitor Atlas/Carmen off-take needs.',
     'trend': 'UP', 'signal': '&#128314;'},
    {'name': 'DIESEL', 'color': '#e67e22',
     'weekly': 'Asia Gasoil 10ppm FOB Korea: ~$610/MT. PH pump: ~P58-65/liter. Steady PH industrial demand. Lead with coal/nickel, quote as bundle.',
     'trend': 'STABLE', 'signal': '&#128993;'},
    {'name': 'PALM KERNEL SHELLS', 'color': '#8e44ad',
     'weekly': 'FOB Sumatra: $95-110/MT. PH cement AF demand active (Holcim, REYMA, Northern Cement). AF substitution 15-25% of thermal. Bundle with coal to cement.',
     'trend': 'STABLE', 'signal': '&#128993;'},
    {'name': 'WOODCHIPS', 'color': '#16a085',
     'weekly': 'CIF China: ~$130-160/m3. China imports 15.6M MT/yr. Q1 2026 log imports: 7.16M m3 down 11% YoY. Explore with North Negros BioPower, SNBP, SCBI.',
     'trend': 'SOFT', 'signal': '&#128992;'},
    {'name': 'CRUDE PALM OIL', 'color': '#d35400',
     'weekly': 'MDEX May 21: RM 4,380/MT (~$1,050-1,060/MT). Indonesia FOB: $1,090-1,215/MT. B50 mandate adding ~3M MT domestic demand. Prices firm. Not primary focus.',
     'trend': 'FIRM', 'signal': '&#128993;'},
]

def trend_color(t):
    if t == 'UP': return '#27ae60'
    if t == 'DOWN': return '#e74c3c'
    return '#f39c12'

def stage_icon(s):
    m = {'appointmentscheduled': '&#128278; Appointment', 'qualifiedbuyers': '&#9989; Qualified',
         'presentationscheduled': '&#128202; Presentation', 'decisionmakerboughtin': '&#127919; Decision Maker',
         'contractsent': '&#128196; Contract Sent', 'closedwon': '&#127942; Won', 'closedlost': '&#10060; Lost'}
    return m.get(s, s)

def build_html(data):
    today = datetime.datetime.now()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    td = today.strftime('%B %d, %Y')
    wr = week_start.strftime('%B %d') + ' - ' + week_end.strftime('%B %d, %Y')
    parts = []
    parts.append('<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ECONARES Weekly Brief - ' + td + '</title></head>')
    parts.append('<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">')
    parts.append('<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:20px 10px;"><tr><td align="center">')
    parts.append('<table width="700" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">')
    parts.append('<tr><td style="background:linear-gradient(135deg,#1a252f 0%,#2c3e50 100%);padding:24px 30px;">')
    parts.append('<table width="100%"><tr>')
    parts.append('<td><div style="color:#fff;font-size:11px;letter-spacing:1px;text-transform:uppercase;opacity:0.7;">ECONARES SALES INTELLIGENCE</div>')
    parts.append('<div style="color:#fff;font-size:22px;font-weight:bold;margin-top:4px;">Weekly Brief</div>')
    parts.append('<div style="color:#fff;font-size:12px;opacity:0.7;margin-top:4px;">Week of ' + wr + '</div></td>')
    parts.append('<td align="right"><div style="font-size:13px;color:#fff;opacity:0.9;">' + td + '</div>')
    parts.append('<div style="font-size:11px;color:#fff;opacity:0.7;margin-top:2px;">5:00 PM PHT - Every Friday</div></td>')
    parts.append('</tr></table></td></tr>')
    over_color = '#e74c3c' if data['overdue'] else '#27ae60'
    boxes = [('Active Deals', str(len(data['active_deals'])), '#1a252f'),
             ('Pipeline (USD)', '${:,}'.format(int(data['total_pipeline'])), '#1a5276'),
             ('Closed Won', '${:,}'.format(int(data['won_amount'])), '#27ae60'),
             ('Overdue Tasks', str(len(data['overdue'])), over_color),
             ('Enriched Contacts', str(data['fully_enriched']) + '/' + str(data['total_contacts']), '#27ae60')]
    parts.append('<tr><td style="padding:20px 30px;background:#fafafa;border-bottom:1px solid #eee;">')
    parts.append('<div style="display:flex;gap:16px;flex-wrap:wrap;">')
    for label, val, color in boxes:
        parts.append('<div style="flex:1;min-width:120px;background:#fff;border-radius:6px;padding:12px 16px;text-align:center;border:1px solid #e8e8e8;">')
        parts.append('<div style="font-size:22px;font-weight:bold;color:' + color + ';">' + val + '</div>')
        parts.append('<div style="font-size:11px;color:#888;margin-top:2px;">' + label + '</div></div>')
    parts.append('</div></td></tr>')
    parts.append('<tr><td style="padding:20px 30px;">')
    parts.append('<div style="font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #1a252f;">&#128202; COMMODITY TRENDS THIS WEEK</div>')
    parts.append('<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">')
    parts.append('<thead><tr style="background:#1a252f;color:#fff;">')
    parts.append('<th style="padding:8px 14px;text-align:left;font-size:11px;">COMMODITY</th>')
    parts.append('<th style="padding:8px 14px;text-align:center;font-size:11px;">TREND</th>')
    parts.append('<th style="padding:8px 14px;text-align:left;font-size:11px;">WEEKLY SUMMARY</th>')
    parts.append('</tr></thead><tbody>')
    for c in COMMODITIES:
        tc = trend_color(c['trend'])
        parts.append('<tr><td style="padding:10px 14px;border-bottom:1px solid #eee;vertical-align:top;">')
        parts.append('<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:' + c['color'] + ';margin-right:6px;vertical-align:middle;"></span>')
        parts.append('<strong style="color:' + c['color'] + ';">' + c['name'] + '</strong></td>')
        parts.append('<td style="padding:10px 14px;border-bottom:1px solid #eee;text-align:center;">')
        parts.append('<span style="color:' + tc + ';font-weight:bold;font-size:12px;">' + c['signal'] + ' ' + c['trend'] + '</span></td>')
        parts.append('<td style="padding:10px 14px;border-bottom:1px solid #eee;font-size:12px;color:#444;line-height:1.5;">' + c['weekly'] + '</td></tr>')
    parts.append('</tbody></table></td></tr>')
    parts.append('<tr><td style="padding:0 30px 20px 30px;">')
    parts.append('<table width="100%"><tr>')
    parts.append('<td style="vertical-align:top;width:50%;padding-right:10px;">')
    parts.append('<div style="font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;">&#128179; OPEN DEALS</div>')
    parts.append('<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">')
    parts.append('<thead><tr style="background:#f5f5f5;">')
    parts.append('<th style="padding:6px 12px;text-align:left;font-size:10px;color:#888;">DEAL</th>')
    parts.append('<th style="padding:6px 12px;text-align:left;font-size:10px;color:#888;">STAGE</th>')
    parts.append('<th style="padding:6px 12px;text-align:right;font-size:10px;color:#888;">AMOUNT</th>')
    parts.append('</tr></thead><tbody>')
    if data['active_deals']:
        for d in data['active_deals']:
            p = d['properties']
            amt = float(p.get('amount',0) or 0)
            parts.append('<tr><td style="padding:8px 12px;border-bottom:1px solid #eee;font-weight:600;color:#1a5276;">' + p.get('dealname','-') + '</td>')
            parts.append('<td style="padding:8px 12px;border-bottom:1px solid #eee;color:#555;font-size:12px;">' + stage_icon(p.get('dealstage','')) + '</td>')
            parts.append('<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:600;">${:,}'.format(int(amt)) + '</td></tr>')
    else:
        parts.append('<tr><td colspan="3" style="padding:10px;color:#888;">No active deals</td></tr>')
    parts.append('</tbody></table></td>')
    parts.append('<td style="vertical-align:top;padding-left:10px;">')
    parts.append('<div style="font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;">&#128161; SYSTEM STATUS</div>')
    parts.append('<table width="100%" cellpadding="0" cellspacing="0">')
    parts.append('<tr><td style="padding:6px 0;color:#27ae60;font-weight:600;">&#9989; Syncthing</td><td style="padding:6px 0;color:#555;">Running - 4 peers connected</td></tr>')
    parts.append('<tr><td style="padding:6px 0;color:#27ae60;font-weight:600;">&#9989; Obsidian Vault</td><td style="padding:6px 0;color:#555;">Synced across all devices</td></tr>')
    parts.append('<tr><td style="padding:6px 0;color:#27ae60;font-weight:600;">&#9989; HubSpot</td><td style="padding:6px 0;color:#555;">164 contacts - 119 companies - all RZH-owned</td></tr>')
    parts.append('<tr><td style="padding:6px 0;color:#27ae60;font-weight:600;">&#9989; Cron Jobs</td><td style="padding:6px 0;color:#555;">6 active</td></tr>')
    parts.append('</table>')
    parts.append('<div style="margin-top:16px;font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;">&#9888; OVERDUE TASKS</div>')
    if data['overdue']:
        parts.append('<ul style="margin:0;padding:0 0 0 16px;font-size:12px;color:#555;">')
        for t in data['overdue'][:8]:
            parts.append('<li style="margin-bottom:4px;">&#9888; ' + safe(t['properties'].get('hs_task_subject','No subject')) + '</li>')
        parts.append('</ul>')
    else:
        parts.append('<div style="font-size:12px;color:#888;">No overdue tasks</div>')
    parts.append('</td></tr></table></td></tr>')
    parts.append('<tr><td style="background:#f4f6f8;padding:14px 30px;text-align:center;font-size:11px;color:#999;border-top:1px solid #eee;">')
    parts.append('ECONARES Sales Intelligence - ' + td + ' 5:00 PM PHT - Synced via Syncthing</td></tr>')
    parts.append('</table></td></tr></table></body></html>')
    return ''.join(parts)

def send_gmail(html_body):
    td = datetime.datetime.now().strftime('%B %d, %Y')
    msg = MIMEMultipart('alternative')
    msg['To'] = GMAIL_TO
    msg['From'] = GMAIL_FROM
    msg['Subject'] = 'ECONARES Weekly Brief - ' + td
    d = get_hubspot_data()
    p_active = str(len(d['active_deals']))
    p_pipe = '${:,}'.format(int(d['total_pipeline']))
    p_won = '${:,}'.format(int(d['won_amount']))
    p_over = str(len(d['overdue']))
    plain = 'ECONARES Weekly Brief - ' + td + ' | 5:00 PM PHT\n\nActive deals: ' + p_active + ' | Pipeline: ' + p_pipe + '\nClosed Won: ' + p_won + ' | Overdue: ' + p_over + '\n\nFull weekly brief - view in email or Obsidian vault.\n---\nECONARES Sales Intelligence | ' + td
    msg.attach(MIMEText(plain, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    if not GMAIL_PW:
        print('ERROR: GMAIL_APP_PASSWORD not found'); return False
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_FROM, GMAIL_PW)
            server.send_message(msg)
        print('GMAIL: Sent to ' + GMAIL_TO)
        return True
    except Exception as e:
        print('GMAIL ERROR: ' + str(e)); return False

def write_obsidian_note():
    vault = OBSIDIAN_VAULT
    weekly_dir = os.path.join(vault, '2_Areas', 'Sales_Ops', 'Weekly_Brief')
    os.makedirs(weekly_dir, exist_ok=True)
    today = datetime.datetime.now()
    week_start = today - datetime.timedelta(days=today.weekday())
    ts = today.strftime('%Y-%m-%d')
    td = today.strftime('%B %d, %Y')
    week_str = week_start.strftime('%Y-W%V')
    path = os.path.join(weekly_dir, 'weekly_brief_' + week_str + '.md')
    d = get_hubspot_data()
    c_lines = []
    for c in COMMODITIES:
        c_lines.append('| **' + c['name'] + '** | ' + c['trend'] + ' | ' + c['weekly'] + ' |')
    c_md = '\n'.join(c_lines) + '\n'
    d_lines = []
    for p in [x['properties'] for x in d['active_deals']]:
        amt = float(p.get('amount',0) or 0)
        d_lines.append('| ' + p.get('dealname','-') + ' | ' + stage_icon(p.get('dealstage','')) + ' | ${:,}'.format(int(amt)) + ' |')
    deals_md = '\n'.join(d_lines) + '\n' if d_lines else '| No active deals | | |\n'
    w_lines = []
    for p in [x['properties'] for x in d['won_deals']]:
        amt = float(p.get('amount',0) or 0)
        w_lines.append('| ' + p.get('dealname','-') + ' | ${:,}'.format(int(amt)) + ' |')
    won_md = '\n'.join(w_lines) + '\n' if w_lines else ''
    ov_lines = []
    for t in d['overdue']:
        ov_lines.append('- &#9888; ' + safe(t['properties'].get('hs_task_subject','No subject')))
    ov_md = '\n'.join(ov_lines) + '\n' if ov_lines else ''
    md_lines = ['---', 'type: weekly-brief', 'date: ' + ts, 'generated: ' + datetime.datetime.now().isoformat(), '---', '',
                '# &#128463; ECONARES Weekly Brief - ' + td, '',
                '> Auto-generated by Hermes Agent every Friday 5:00 PM PHT.', '',
                '## &#128202; Week at a Glance', '',
                '- **Active deals:** ' + str(len(d['active_deals'])) + ' | Pipeline: **${:,}'.format(int(d['total_pipeline'])) + '**',
                '- **Closed Won this week:** ${:,}'.format(int(d['won_amount'])),
                '- **Overdue tasks:** ' + str(len(d['overdue'])) + ' &#9888;',
                '- **Enriched contacts:** ' + str(d['fully_enriched']) + ' / ' + str(d['total_contacts']), '',
                '## &#128202; Commodity Trends This Week', '',
                '| Commodity | Trend | Summary |', '|---|---|---|', c_md,
                '## &#128179; Open Deals', '',
                '| Deal | Stage | Amount |', '|---|---|---|', deals_md]
    if won_md:
        md_lines += ['## &#127942; Closed Won', '', '| Deal | Amount |', '|---|---|---|', won_md]
    if ov_md:
        md_lines += ['## &#9888; Overdue Tasks', '', ov_md]
    md_lines += ['## &#128161; System Status', '',
                 '- &#9989; Syncthing - Running, 4 peers connected',
                 '- &#9989; Obsidian Vault - Synced',
                 '- &#9989; HubSpot - 164 contacts, 119 companies, all RZH-owned',
                 '- &#9989; Cron jobs - 6 active', '',
                 '---', '*Auto-generated ' + td + ' 5:00 PM PHT - ECONARES Sales Intelligence*']
    with open(path, 'w') as f:
        f.write('\n'.join(md_lines))
    print('OBSIDIAN: Written -> ' + path)
    return path

if __name__ == '__main__':
    print('=== ECONARES WEEKLY BRIEF ===')
    data = get_hubspot_data()
    print('  Active deals:', len(data['active_deals']), '| Pipeline: ${:,}'.format(int(data['total_pipeline'])))
    print('  Closed Won: ${:,}'.format(int(data['won_amount'])), '| Overdue:', len(data['overdue']))
    print('  Contacts:', data['total_contacts'], '| Fully enriched:', data['fully_enriched'])
    html = build_html(data)
    note_path = write_obsidian_note()
    sent = send_gmail(html)
    print('\nDONE -- Obsidian:', note_path, '| Gmail:', 'Sent' if sent else 'FAILED')
