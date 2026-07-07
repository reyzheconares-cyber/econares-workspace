"""Delete 2 RENEWABLES_ENVIRONMENT companies + re-tag Acciona Daanbantayan."""
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

RENEWABLE_COMPANIES = [
    '320722047717',  # Alsons Power Group (renewable-tagged)
    '322943715053',  # MINERGY
]
ACCIONA_ID = '319247626955'  # Acciona Energia - Daanbantayan Solar Project

# === Step 0: Inventory contacts on the 2 renewables companies ===
print('=== Step 0: Inventory contacts + notes + tasks on renewables companies ===')
for cid in RENEWABLE_COMPANIES:
    print(f'\\nCompany {cid}:')
    for obj_type in ['contacts', 'notes', 'tasks']:
        body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id' if obj_type == 'contacts' else 'hs_object_id', 'operator': 'EQ', 'value': cid}]}], 'limit': 10}).encode()
        req = urllib.request.Request(f'{BASE}/crm/v3/objects/{obj_type}/search', data=body, method='POST')
        req.add_header('Authorization', f'Bearer {T}')
        req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req) as r:
                d = json.loads(r.read().decode())
        except urllib.error.HTTPError:
            d = {'total': 0}
        # Use associatedcompanyid for contacts
        if obj_type == 'contacts':
            body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': cid}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_object_id'], 'limit': 10}).encode()
            req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
            req.add_header('Authorization', f'Bearer {T}')
            req.add_header('Content-Type', 'application/json')
            try:
                with urllib.request.urlopen(req) as r:
                    d = json.loads(r.read().decode())
            except urllib.error.HTTPError:
                d = {'total': 0}
        print(f'  {obj_type}: {d.get("total",0)}')
        if obj_type == 'contacts' and d.get('total', 0) > 0:
            for c in d.get('results', []):
                p = c['properties']
                name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
                print(f'    {c["id"]}: {name} | email={p.get("email","")} | job={p.get("jobtitle","")}')

# === Step 1: Re-tag Acciona Daanbantayan to OIL_ENERGY ===
print()
print('=== Step 1: Re-tag Acciona Daanbantayan to OIL_ENERGY ===')
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/companies/{ACCIONA_ID}', {
    'properties': {
        'industry': 'OIL_ENERGY'
    }
})
print(f'PATCH Acciona industry: HTTP {sc}')

# Add a note explaining the re-tag
note_body = (
    f'**RE-TAGGED - {today}**\n\n'
    f'Industry changed from null to OIL_ENERGY.\n\n'
    f'Reason: While the Acciona Daanbantayan Solar Project itself is solar (180MWp PV), '
    f'ECONARES fit is for construction-phase diesel/fuel supply (not renewables power). '
    f'Project is currently in construction (target completion late 2026) — short-term '
    f'fuel supply opportunity, not a long-term renewables offtake. Tagged as OIL_ENERGY '
    f'to keep in the active procurement pipeline.\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_body},
    'associations': [{'to': {'id': ACCIONA_ID}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE Acciona re-tag: HTTP {sc}')

# === Step 2: Delete the 2 RENEWABLES companies ===
print()
print('=== Step 2: Delete RENEWABLES companies ===')
for cid in RENEWABLE_COMPANIES:
    print(f'\\nDeleting company {cid}...')
    sc, d = http('DELETE', f'{BASE}/crm/v3/objects/companies/{cid}')
    print(f'  DELETE: HTTP {sc}')
    if sc == 204:
        print(f'  Company {cid} DELETED successfully')
    else:
        print(f'  Warning: {d}')

# === Step 3: Verify final state ===
print()
print('=== Step 3: Verify zero RENEWABLES_ENVIRONMENT companies ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'industry', 'operator': 'EQ', 'value': 'RENEWABLES_ENVIRONMENT'}]}], 'properties': ['name','hs_object_id'], 'limit': 10}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'RENEWABLES_ENVIRONMENT companies remaining: {d.get("total",0)}')

# Verify the deleted companies are gone
print()
print('=== Verify deletions ===')
for cid in RENEWABLE_COMPANIES:
    sc, d = http('GET', f'{BASE}/crm/v3/objects/companies/{cid}')
    print(f'  Company {cid}: HTTP {sc}', '(expected 404)')

# Verify Acciona re-tag
print()
print('=== Acciona Daanbantayan re-tag verification ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': ACCIONA_ID}]}], 'properties': ['name','industry','hs_object_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for c in d.get('results',[]):
    p = c['properties']
    print(f'  {c["id"]}: {p.get("name","")} | industry={p.get("industry","")}')

print()
print('=== Done ===')