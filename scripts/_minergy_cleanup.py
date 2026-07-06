"""Minergy cleanup per user Option C: try merge API, fallback to reassign+delete."""
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

STALE_COMPANY = '320523465441'  # Minergy Coal Corporation
REAL_COMPANY = '320527602408'    # Minergy Power Corporation - Balingasag Power Station
CONTACT_ON_STALE = '478913617612'  # Procurement Minergy

# === Step 1: Try the HubSpot merge API ===
# HubSpot's merge endpoint is POST /crm/v3/objects/companies/merge
print('=== Step 1: Try HubSpot merge API ===')
merge_body = {
    'mergeTo': REAL_COMPANY,  # merge INTO this company (the real one)
    'objectIdsToMerge': [STALE_COMPANY]  # this company gets merged
}
sc, d = http('POST', f'{BASE}/crm/v3/objects/companies/merge', merge_body)
print(f'Merge API: HTTP {sc}')
if sc == 200:
    print('  Merge SUCCESS! Stale company merged into real one.')
    print(f'  Response: {d}')
    merge_worked = True
else:
    print(f'  Merge not available (HTTP {sc}). Falling back to manual reassign+delete.')
    if isinstance(d, dict) and 'message' in d:
        msg = d.get('message')
        print(f'  Reason: {msg}')
    merge_worked = False

# === Step 2 (if merge failed): Reassign contact to the real company ===
if not merge_worked:
    print()
    print('=== Step 2: Reassign contact to real company ===')
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{CONTACT_ON_STALE}', {
        'properties': {
            'associatedcompanyid': REAL_COMPANY
        }
    })
    print(f'PATCH contact associatedcompanyid: HTTP {sc}')

    if sc == 200:
        # Add a note explaining the re-tag
        note_body = (
            f'**RE-ASSIGNED - {today}**\n\n'
            f'Contact was originally associated with company 320523465441 ("Minergy Coal Corporation") '
            f'which is a STALE DUPLICATE. The real entity is 320527602408 ("Minergy Power Corporation - Balingasag Power Station").\n\n'
            f'Email info@minergypower.com.ph is the Balingasag Power Station (MPC) procurement shared inbox - '
            f'correctly tagged to MPC, not the deprecated Minergy Coal Corporation record.\n\n'
            f'Reason for reassignment: 320523465441 was marked as a duplicate of 320527602408 '
            f'(MPC is wholly-owned by Mindanao Energy Systems Inc, and 40% by Vivant Corp). '
            f'Stale company record deleted after contact re-assignment.\n\n'
        )
        sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
            'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_body},
            'associations': [{'to': {'id': CONTACT_ON_STALE}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
        })
        print(f'NOTE re-assignment documented: HTTP {sc}')

# === Step 3 (if merge failed): Delete the stale company ===
if not merge_worked:
    print()
    print('=== Step 3: Delete stale company 320523465441 ===')
    sc, d = http('DELETE', f'{BASE}/crm/v3/objects/companies/{STALE_COMPANY}')
    print(f'DELETE stale company: HTTP {sc}')
    if sc == 204:
        print('  Stale company DELETED.')
    else:
        print(f'  Warning: {d}')

# === Step 4: Verify final state ===
print()
print('=== Step 4: Verify final Minergy state ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'CONTAINS_TOKEN', 'value': 'Minergy'}]}], 'properties': ['name','industry','city','country','domain','num_associated_contacts','hs_object_id'], 'limit': 20}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Minergy companies remaining: {d.get("total",0)}')
for c in d.get('results',[]):
    p = c['properties']
    print(f'  {c["id"]}: {p.get("name","")} | industry={p.get("industry","")} | domain={p.get("domain","")} | contacts={p.get("num_associated_contacts","")}')

print()
print('=== Contact 478913617612 state ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': CONTACT_ON_STALE}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    print(f'  {c["id"]}: {name} | email={p.get("email","")} | job={p.get("jobtitle","")} | co={p.get("associatedcompanyid","")}')

print()
print('=== Done ===')