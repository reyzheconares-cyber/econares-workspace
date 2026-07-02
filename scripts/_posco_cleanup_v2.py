"""POSCO Holdings re-create + Intl fix."""
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
INTERNATIONAL_ID = '331643910896'  # already created

# Fix POSCO International first (state + phone mask issue)
print('=== Fix POSCO International: state + phone ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{INTERNATIONAL_ID}', {
    'properties': {
        'state': 'Seoul',
        'phone': '+82 2 759 4114'
    }
})
print(f'  PATCH: {sc}')

# Create POSCO Holdings
print()
print('=== Create POSCO Holdings (using MINING_METALS for steel) ===')
desc = (
    "POSCO Holdings, Inc. (KRX: 005490) - South Korean steel-to-materials conglomerate, parent of POSCO Group. "
    "Founded 1968 (Korean government, Pohang). HQ Seoul (registered), Pohang (steel operations). "
    "Chairman and CEO: Chang In-hwa (since Mar 2024, 2.33 years tenure). Strategic vision: '2 Core + New Engine' - steel + energy materials + new businesses; KRW 200T market cap target by 2030. "
    "2025 revenue: KRW 69.1T (US$50B). Steel segment: 17.2M MT/yr crude steel capacity, KRW 59.4T sales + KRW 2T operating profit. "
    "Battery materials (POSCO Future M): KRW 3.34T sales, KRW 440.9B operating loss (investing in EV supply chain). "
    "Key subsidiaries: POSCO (steel), POSCO International (trading), POSCO Future M (battery materials), POSCO-Pilbara Lithium Solution (21,500 t/yr lithium, Feb 2025), PT Krakatau POSCO (Indonesia integrated steel, 3M MT/yr). "
    "POSCO-Huayou JVs (China): Zhejiang POSCO-Huayou (30,000 MT/yr cathode, POSCO 60%/Huayou 40%) + Zhejiang Huayou-POSCO (30,000 MT/yr precursors, Huayou 60%/POSCO 40%). "
    "Workforce: 30,000+ globally. Conflict minerals compliance per SEC reporting (responsible minerals mgmt under Purchasing and Investment Division). "
    "PHILIPPINES NICKEL ANGLE: POSCO Future M has JV with MC Group (NPSI subsidiary) to produce MHP (mixed hydroxide precipitate) in PH. MC Group targets acquiring ~200M tons nickel ore by 2026. POSCO Future M targets 1M MT/yr cathode materials by 2030. "
    "ECONARES angle: PH saprolite/limonite nickel ore supply to NPSI/POSCO Future M JV; PH cobalt for cathode; lithium for POSCO-Pilbara."
)
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'POSCO Holdings, Inc.',
        'domain': 'posco.com',
        'industry': 'MINING_METALS',
        'phone': '+82 54 220 0114',
        'address': 'POSCO Tower, 165 Convensia-daero, Yeonsu-gu, Incheon, South Korea (HQ); Pohang Steelworks: 6261 Donghaean-ro, Nam-gu, Pohang',
        'city': 'Incheon',
        'country': 'South Korea',
        'website': 'https://www.posco.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 30000,
        'description': desc
    }
})
print(f'  CREATE: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
HOLDINGS_ID = r.get('id') if sc in (200, 201) else None

# Check name auto-truncation
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{HOLDINGS_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'POSCO Holdings, Inc.':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{HOLDINGS_ID}', {'properties': {'name': 'POSCO Holdings, Inc.'}})
            print(f'  PATCH name: {sc3}')

print()

# === Re-link 2 contacts to Holdings (they were created with the wrong company id, since Holdings never existed) ===
print('=== Re-associate 2 contacts to POSCO Holdings ===')
# Jungeun Yi and Seonyeob Chu were created earlier but linked to nothing (Holdings was missing)
# Search for them by name to find their IDs
for ln, fn in [('Yi', 'Jungeun'), ('Chu', 'Seonyeob')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','associatedcompanyid']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p2 = c['properties']
        if p2.get('firstname') == fn:
            # Re-associate to POSCO Holdings
            sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{c["id"]}', {
                'properties': {'associatedcompanyid': HOLDINGS_ID}
            })
            print(f'  re-associate {fn} {ln} (id:{c["id"]}) -> Holdings: {sc}')

print()

# Re-associate engagement note (was attached to International only)
print('=== Re-associate note to Holdings ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_note_body', 'operator': 'CONTAINS_TOKEN', 'value': 'POSCO Group CRM Buildout'}]}], 'properties': ['hs_note_body']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/notes/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
for n in d.get('results', []):
    note_id = n['id']
    sc, r = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{HOLDINGS_ID}/note_to_company', {})
    print(f'  assoc note {note_id} -> Holdings: {sc}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
for label, oid in [('POSCO Holdings', HOLDINGS_ID), ('POSCO International', INTERNATIONAL_ID)]:
    if not oid:
        continue
    sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{oid}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
    p = co['properties']
    print(f'--- {label} ({oid}) ---')
    for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
        print(f'  {k}: {p.get(k)}')

print()
print('--- Holdings contacts (direct ID lookup) ---')
# Search by name since associatedcompanyid has indexing delay
for ln, fn in [('Yi', 'Jungeun'), ('Chu', 'Seonyeob')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','associatedcompanyid','hs_buying_role','hs_linkedin_url']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p2 = c['properties']
        if p2.get('firstname') == fn:
            print(f"  {fn} {ln} (id:{c['id']}) | co:{p2.get('associatedcompanyid')} | role:{p2.get('hs_buying_role')}")
            if p2.get('hs_linkedin_url'):
                print(f"    linkedin: {p2['hs_linkedin_url']}")
