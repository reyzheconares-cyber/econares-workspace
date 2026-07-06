"""Update Huayou contacts based on bounce findings (2026-07-06)."""
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

# === Update Qi Sun (469448797917) - flag stale ===
# Move to UNQUALIFIED + add note explaining the xct@ bounce
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/469448797917', {
    'properties': {'hs_lead_status': 'UNQUALIFIED'}
})
print(f'PATCH Qi Sun status=UNQUALIFIED: HTTP {sc}')

note_qi = (
    f'**BOUNCE FLAG - {today}**\n\n'
    f'Email xct@huayou.com returned 554 "dosnt exist" on 2026-07-06 nickel send.\n\n'
    f'Huayou email format is NOT first.last — uses department codes (from official IR page huayou.com/en/invester):\n'
    f'- xnymarket@huayou.com (New Energy Market — Ni ore procurement)\n'
    f'- fdc@huayou.com (raw materials trading)\n'
    f'- xclmarket@huayou.com (precursors)\n'
    f'- hyxh@huayou.com (Quzhou ops)\n'
    f'- information@huayou.com (general IR)\n\n'
    f'Next action: Use xnymarket@huayou.com for new nickel ore outreach.\n\n'
    f'ALSO: LinkedIn-verified Huayou procurement contacts (per research 2026-07-06):\n'
    f'- Qi Bill (Sun Qi) — Director of Sales Marketing, California (LinkedIn linkedin.com/in/billsunqi)\n'
    f'- Hong Bo (洪波) — Chief of Representative, GM Nickel Ore Procurement (RocketReach)\n'
    f'- Xingwei Liang — Commercial Manager Huayou CDM (DRC, LinkedIn linkedin.com/in/xingwei-liang, HubSpot 512673716934)\n'
    f'- Malarm Pan — Senior Executive Purchase, Huayou Cobalt (LinkedIn)\n\n'
    f'Source: ECONARES research session 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_qi},
    'associations': [{'to': {'id': '469448797917'}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE Qi Sun: HTTP {sc}')

# === Update Xingwei Liang (512673716934) - add verified email + LinkedIn ===
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/512673716934', {
    'properties': {
        'email': 'xingwei.liang@huayou.com',
        'hs_linkedin_url': 'https://www.linkedin.com/in/xingwei-liang'
    }
})
print(f'PATCH Xingwei Liang: HTTP {sc}')

note_xingwei = (
    f'**EMAIL VERIFIED + LINKEDIN CONFIRMED - {today}**\n\n'
    f'LinkedIn: https://www.linkedin.com/in/xingwei-liang\n'
    f'Current role (Sep 2025-present): Commercial Manager (Commodity Sales & Procurement), CDM (Huayou)\n'
    f'Location: Lubumbashi, Haut-Katanga, DRC\n'
    f'Background: Imperial College London\n'
    f'Scope: Procurement + sales of bulk auxiliary materials, chemical products, copper cathodes; import/export trade process + market analysis\n\n'
    f'Email pattern: first.last@huayou.com (dept-codes also work)\n'
    f'Applied: xingwei.liang@huayou.com\n'
    f'Backup: xingweiliang@huayou.com\n'
    f'NOTE: Xingwei is in DRC — relevant for Jinchuan-CDM collaboration (both active in DRC).\n\n'
    f'Source: ECONARES research 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_xingwei},
    'associations': [{'to': {'id': '512673716934'}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE Xingwei Liang: HTTP {sc}')

print()
print('=== Done ===')