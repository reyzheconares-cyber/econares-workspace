"""Log LinkedIn connection request (one-liner) sent to Jungeun Yi - 2026-07-06."""
import json, urllib.request, datetime

ENV = r'C:\Users\reyma\.hermes\.env'
with open(ENV, 'r', encoding='utf-8') as f:
    T = None
    for line in f:
        if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN='):
            T = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

BASE = 'https://api.hubapi.com'

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return resp.status, (json.loads(resp.read().decode()) if resp.length else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:300]

now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
today = datetime.date.today().isoformat()

# Jungeun Yi HubSpot ID = 512570728144
contact_id = '512570728144'

# Update lead status: OPEN (already OPEN from earlier email; just log the new LinkedIn connect attempt)
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{contact_id}', {
    'properties': {
        'hs_lead_status': 'OPEN'
    }
})
print(f'PATCH Jungeun Yi status=OPEN: HTTP {sc}')

# Engagement note - LinkedIn Connect (one-liner)
note_body = (
    f'**LINKEDIN CONNECTION REQUEST SENT - 2026-07-06 ~16:15 PHT**\n\n'
    f'Channel: LinkedIn Connect + 300-char connection note (one-liner)\n'
    f'Profile: https://www.linkedin.com/in/jungeun-christine-yi-58b1a224\n'
    f'Note length: ~280 chars (under 300 limit)\n\n'
    f'ONE-LINER USED:\n'
    f'"Hi Ms. Yi - I\'m Reymarr Hijara with ECONARES (PH nickel ore supplier). Reaching out re: '
    f'POSCO Future M\'s NPSI/MC Group JV + your 10+ yrs in POSCO raw materials procurement. '
    f'Detailed email sent to jungeun.yi@posco.com (CC Young-Hoon YOU). - RZH"\n\n'
    f'FULL MESSAGE (1,392 chars) was prepared in the previous turn but user opted for '
    f'one-liner connection note instead (fits LinkedIn\'s 300-char connect note limit). '
    f'Once connected, the full message can be sent via LinkedIn DM OR follow up via email.\n\n'
    f'CHANNEL CONTEXT:\n'
    f'- 2026-07-06 11:21 PHT: Email to jungeun.yi@posco.com (CC young-hoon.you@posco.com) sent - msg 227\n'
    f'- 2026-07-06 14:31 PHT: Email to young-hoon.you@posco.com (CC jungeun.yi@posco.com) sent - msg 231\n'
    f'- 2026-07-06 15:40 PHT: LinkedIn message to Young-Hoon YOU sent (user manually) - Note 381270329046\n'
    f'- 2026-07-06 16:15 PHT: LinkedIn connection request to Jungeun Yi sent (user manually) - THIS NOTE\n\n'
    f'FOLLOW-UP PLAN: +7 days (around 2026-07-13). If connection accepted, send the full 1,392-char '
    f'LinkedIn DM. If no acceptance, follow up via email to jungeun.yi@posco.com again. Task 3811... (created earlier today).\n\n'
    f'Source: ECONARES sales outreach 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_body},
    'associations': [{'to': {'id': contact_id}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
note_id = d.get('id', '?') if isinstance(d, dict) else '?'
print(f'NOTE LinkedIn Connect logged: HTTP {sc} | id={note_id}')

print()
print('=== Done ===')
print(f'Contact: Jungeun Yi ({contact_id})')
print(f'Note: {note_id}')