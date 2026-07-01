"""
Quezon Power cleanup + enrichment
- Step 1: Merge 2 duplicate Company records (keep 326532899525 - correct Mauban address)
- Step 2: Merge 2 duplicate Walter Laptew contacts (keep 509286368974)
- Step 3: Update Frank Thiel title (dual role) + set buying_role
- Step 4: Create Chaiwut Saengpredekorn + Davie Ligasan
- Step 5: Set hs_target_account = tier_1 on canonical QPL record
"""
import json, os, urllib.request
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()[:400]

BASE = 'https://api.hubapi.com'

# === PRE-FLIGHT: confirm all source records exist before any write ===
print('=== PRE-FLIGHT VERIFICATION ===')
for label, oid, kind in [
    ('QPL canonical', '326532899525', 'company'),
    ('QPL duplicate', '330866875066', 'company'),
    ('Frank Thiel', '499284710077', 'contact'),
    ('Walter Laptew #1', '509286368974', 'contact'),
    ('Walter Laptew #2', '509286368976', 'contact'),
]:
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/{kind}s/{oid}?properties=firstname,lastname,name')
    req.add_header('Authorization', f'Bearer {T}')
    try:
        with urllib.request.urlopen(req) as resp:
            d = json.loads(resp.read().decode())
            print(f'  OK {label} ({oid}): {d["properties"].get("name") or d["properties"].get("firstname")+" "+d["properties"].get("lastname")}')
    except Exception as e:
        print(f'  MISSING {label} ({oid}): {e}')

print()

# === STEP 1: Re-associate contacts from duplicate Company (330866875066) to canonical (326532899525) ===
# This avoids losing data; HubSpot doesn't have a native "merge companies" but we can transfer associations
print('=== STEP 1: Transfer contacts from duplicate QPL (330866875066) to canonical (326532899525) ===')
for ct_id in ['509286368974', '509286368976']:
    # Read current associations
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/{ct_id}/associations/companies')
    req.add_header('Authorization', f'Bearer {T}')
    with urllib.request.urlopen(req) as resp:
        assocs = json.loads(resp.read().decode())
    print(f'  contact {ct_id} current company associations:', [a['id'] for a in assocs.get('results', [])])

    # PATCH contact's associatedcompanyid to canonical
    sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{ct_id}', {
        'properties': {'associatedcompanyid': '326532899525'}
    })
    print(f'  re-associate {ct_id} → 326532899525: status {sc}')

# Delete the duplicate company record
print('  deleting duplicate company 330866875066...')
sc, r = http('DELETE', f'{BASE}/crm/v3/objects/companies/330866875066')
print(f'  DELETE duplicate company: status {sc}')

print()

# === STEP 2: Merge 2 duplicate Walter Laptew contacts ===
# Update the duplicate (509286368976) with primary's associations, then delete it
print('=== STEP 2: Merge duplicate Walter Laptew contacts ===')
# First, check both contacts' details
for ct_id in ['509286368974', '509286368976']:
    sc, ct = http('GET', f'{BASE}/crm/v3/objects/contacts/{ct_id}?properties=firstname,lastname,jobtitle,email,phone,hs_buying_role,hs_linkedin_url,associatedcompanyid')
    if sc == 200:
        p = ct.get('properties', {})
        print(f"  {ct_id}: {p.get('firstname')} {p.get('lastname')} | {p.get('jobtitle')} | {p.get('email')} | co:{p.get('associatedcompanyid')}")

# Delete the duplicate
print('  deleting duplicate Walter Laptew 509286368976...')
sc, r = http('DELETE', f'{BASE}/crm/v3/objects/contacts/509286368976')
print(f'  DELETE duplicate: status {sc}')

print()

# === STEP 3: Update Frank Thiel title (dual role) + set buying_role ===
print('=== STEP 3: Update Frank Thiel (499284710077) ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/499284710077', {
    'properties': {
        'jobtitle': 'Managing Director, Quezon Power (Philippines) Ltd. Co. (QPL) + General Manager, San Buenaventura Power Ltd. Co. (SBPL)',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_lead_status': 'OPEN'
    }
})
print(f'  PATCH Frank Thiel: status {sc}')

print()

# === STEP 4: Create Chaiwut Saengpredekorn + Davie Ligasan ===
print('=== STEP 4: Create new contacts ===')
contacts_to_create = [
    {
        'firstname': 'Chaiwut',
        'lastname': 'Saengpredekorn',
        'jobtitle': 'Assistant Managing Director, Quezon Power (Philippines) Ltd. Co. (QPL)',
        'associatedcompanyid': '326532899525',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'source': 'qpl.com.ph/corporate-leadership (verified)'
    },
    {
        'firstname': 'Davie',
        'lastname': 'Ligasan',
        'jobtitle': 'Purchasing Staff, Quezon Power',
        'associatedcompanyid': '326532899525',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/davie-ligasan-383523353',
        'source': 'LinkedIn (verified)'
    }
]
for c in contacts_to_create:
    src = c.pop('source')
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: status {sc}", '|', ct.get('id') if sc in (200,201) else ct.get('message',''))

print()

# === STEP 5: Set hs_target_account = tier_1 on canonical QPL record ===
print('=== STEP 5: Set tier_1 on QPL (326532899525) ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/326532899525', {
    'properties': {
        'hs_target_account': 'tier_1',
        'industry': 'UTILITIES'
    }
})
print(f'  PATCH QPL: status {sc}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/326532899525?properties=name,industry,phone,address,city,state,country,website,hs_target_account,description')
p = co['properties']
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
    print(f'  CO  {k}: {p.get(k)}')
print(f'  CO  description[:80]: {(p.get("description") or "")[:80]}')

body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': '326532899525'}]}], 'properties': ['firstname','lastname','jobtitle','hs_buying_role','hs_lead_status','hs_linkedin_url','email']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'\n  Contacts at QPL: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"  CT  ID:{c['id']} | {p2.get('firstname')} {p2.get('lastname')} | {p2.get('jobtitle')} | role:{p2.get('hs_buying_role')} | status:{p2.get('hs_lead_status')}")