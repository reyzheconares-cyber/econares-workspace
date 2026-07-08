"""Log 2026-07-08 soft-bounce delays to HubSpot."""
import json, urllib.request, datetime

ENV_PATH = r'C:\Users\reyma\.hermes\.env'
T = None
with open(ENV_PATH, 'r', encoding='utf-8') as f:
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

# === Bounce 665: Roderick Fernandez (FDCUI) - already known ===
print('=== Bounce 665: roderick.fernandez@fdcui.com.ph ===')
RODERICK = '514137483968'
note_roderick = (
    f'**SOFT-BOUNCE (DELAY) - 2026-07-08 ~11:54 PHT (03:54 UTC)**\n\n'
    f'Channel: Gmail SMTP retry notification (bounce id 665)\n'
    f'Recipient: roderick.fernandez@fdcui.com.ph\n'
    f'Server: fdcui.com.ph 45.79.222.138 - timed out\n'
    f'Status: Gmail will retry for 22 more hours. Will be notified if delivery fails permanently.\n\n'
    f'This is the SAME server IP that has been timing out since 2026-06-29 (3 hard bounces + now 1 soft-bounce delay).\n\n'
    f'ACTION: Continue holding off on email outreach to fdcui.com.ph. Proceed with landline call to +63 2 8575 1600 (per Task 381437522656, due 2026-07-08).\n\n'
    f'Source: ECONARES CRM tracking 2026-07-08.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_roderick},
    'associations': [{'to': {'id': RODERICK}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'  NOTE Roderick: HTTP {sc}')

# === Bounce 658: procurement@tsingshan.com.cn (NEW) ===
# First check the existing Tsingshan contacts in HubSpot
print()
print('=== Search for procurement@tsingshan.com.cn contact ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'email', 'operator': 'EQ', 'value': 'procurement@tsingshan.com.cn'}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid','hs_lead_status','hs_object_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Found: {d.get("total",0)}')
PROCUREMENT_CONTACT = None
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    PROCUREMENT_CONTACT = c['id']
    print(f'  {c["id"]}: {name} | email={p.get("email")} | job={p.get("jobtitle")} | co={p.get("associatedcompanyid")} | status={p.get("hs_lead_status")}')

# Also search by jobtitle
print()
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'jobtitle', 'operator': 'CONTAINS_TOKEN', 'value': 'Tsingshan'}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid','hs_lead_status','hs_object_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Jobtitle contains "Tsingshan": {d.get("total",0)}')
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    print(f'  {c["id"]}: {name} | email={p.get("email")} | job={p.get("jobtitle")} | co={p.get("associatedcompanyid")}')

# Also try the procurement keyword
print()
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'jobtitle', 'operator': 'CONTAINS_TOKEN', 'value': 'procurement'}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid','hs_object_id'], 'limit': 10}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Jobtitle contains "procurement": {d.get("total",0)}')

# Add note to Tsingshan Holding Group company record (since procurement@tsingshan.com.cn is a generic shared inbox)
print()
print('=== Add bounce note to Tsingshan Holding Group company ===')
TSINGSHAN_CO = '317279658732'
note_tsingshan = (
    f'**SOFT-BOUNCE (DELAY) - 2026-07-08 ~11:58 PHT (03:58 UTC)**\n\n'
    f'Channel: Gmail SMTP retry notification (bounce id 658)\n'
    f'Recipient: procurement@tsingshan.com.cn (legacy/generic Tsingshan procurement inbox)\n'
    f'Server: 211.149.226.144 - FAILED_PRECONDITION: Connection refused\n'
    f'Status: Gmail will retry for 22 more hours. Will be notified if delivery fails permanently.\n\n'
    f'IMPORTANT: This is a DIFFERENT server IP from the tssgroup.com.cn domain (45.79.222.138 was FDCUI; this is 211.149.226.144).\n'
    f'Older bounce in 2026-07-05/06 for procurement@tsingshan.com.cn had a separate issue.\n\n'
    f'CURRENT WORKING TSINGSHAN EMAILS (from 2026-07-06 verification):\n'
    f'- rhea.li@tssgroup.com.cn (Board Procurement)\n'
    f'- arthur.wang@tssgroup.com.cn (Procurement Manager, Shanghai Tsingshan Mineral)\n'
    f'- monalisa.mancong@tssgroup.com.cn (Purchasing Admin, IMIP Morowali)\n'
    f'All 3 use tssgroup.com.cn (NOT tsingshan.com.cn).\n\n'
    f'RECOMMENDATION: Do NOT use procurement@tsingshan.com.cn (deprecated or blacklisted). Use the 3 verified tssgroup.com.cn addresses above.\n\n'
    f'Source: ECONARES CRM tracking 2026-07-08.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_tsingshan},
    'associations': [{'to': {'id': TSINGSHAN_CO}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'  NOTE Tsingshan company: HTTP {sc}')

# Also flag the procurement contact if found
if PROCUREMENT_CONTACT:
    print()
    print('=== Flag the procurement contact as UNQUALIFIED ===')
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{PROCUREMENT_CONTACT}', {
        'properties': {
            'hs_lead_status': 'UNQUALIFIED'
        }
    })
    print(f'  PATCH status: HTTP {sc}')

print()
print('=== Done ===')