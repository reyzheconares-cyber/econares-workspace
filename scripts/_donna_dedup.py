"""Fix Donna Mezo duplicates per user option C.
1. Re-tag Donna 1 (473828030185, gnpres@gnpower.com) from GNPK -> GNPower Group (parent)
2. Delete Donna 2 (486883896055, recruitment@gnpk.com.ph) - wrong role label
"""
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

# === Step 1: Re-tag Donna 1 (473828030185) from GNPK to GNPower Group ===
print('=== Step 1: Re-tag Donna 1 to GNPower Group ===')
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/473828030185', {
    'properties': {
        'associatedcompanyid': '319028063953',  # GNPower Group (parent)
        'jobtitle': 'Purchasing Officer (GNPower Group - shared procurement inbox)'
    }
})
print(f'PATCH Donna 1 (473828030185): HTTP {sc}')

# Add a note documenting the re-tag + merge rationale
note_body = (
    f'**DEDUPLICATION - {today}**\n\n'
    f'Reason: Duplicate "Donna Mezo" contacts found during 2026-07-06 cleanup. '
    f'HubSpot 486883896055 (recruitment@gnpk.com.ph, GNPK) had wrong role label '
    f'(recruitment email but Purchasing Officer jobtitle) - DELETED per user direction.\n\n'
    f'Record 473828030185 (gnpres@gnpower.com) KEPT.\n'
    f'- Re-tagged from GNPower Kauswagan (GNPK, 328345657071) to GNPower Group (parent, 319028063953) '
    f'because gnpres@gnpower.com is a GROUP-level procurement shared inbox, not GNPK-specific.\n'
    f'- Jobtitle updated to reflect group-level purchasing officer role.\n\n'
    f'Email gnpres@gnpower.com: this is a SHARED INBOX, not an individual person. '
    f'Use it for GNPower group-wide procurement inquiries (touches all 3 GNPower entities: '
    f'GNPower Inc., GNPK, GNPD). For GNPK-specific: use the GNPK company record (328345657071) '
    f'and look for procurement contacts on the GNPK domain (gnpk.com.ph).\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_body},
    'associations': [{'to': {'id': '473828030185'}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE Donna 1: HTTP {sc}')

# === Step 2: Delete Donna 2 (486883896055) ===
print()
print('=== Step 2: Delete Donna 2 (recruitment@gnpk.com.ph - wrong role label) ===')
sc, d = http('DELETE', f'{BASE}/crm/v3/objects/contacts/486883896055')
print(f'DELETE Donna 2 (486883896055): HTTP {sc}')

# === Step 3: Verify only one Donna Mezo remains ===
print()
print('=== Step 3: Verify only one Donna Mezo remains ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'firstname', 'operator': 'CONTAINS_TOKEN', 'value': 'Donna'}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_lead_status','associatedcompanyid'], 'limit': 10}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Donna contacts remaining: {d.get("total",0)}')
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    print(f'  {c["id"]}: {name} | email={p.get("email","")} | job={p.get("jobtitle","")} | co={p.get("associatedcompanyid","")}')

# === Step 4: Verify final Donna 1 state ===
print()
print('=== Step 4: Final state of Donna 1 ===')
sc, d = http('GET', f'{BASE}/crm/v3/objects/contacts/473828030185?properties=firstname,lastname,email,jobtitle,associatedcompanyid,hs_lead_status')
if sc == 200:
    p = d.get('properties', {})
    for k, v in sorted(p.items()):
        print(f'  {k}: {v}')

print()
print('=== Done ===')