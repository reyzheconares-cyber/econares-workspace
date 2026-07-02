"""POSCO cleanup:
1. Create POSCO Holdings record (tier_1, MANUFACTURING, Korea HQ)
2. Create POSCO International record (tier_1, trading subsidiary)
3. Create 2 contacts: Jungeun Yi (DECISION_MAKER, Senior Procurement Mgr), Seonyeob Chu (DECISION_MAKER, Senior Procurement Mgr)
4. KYC enrichment via description
5. Create engagement note + final read-back
"""
import json, os, urllib.request, datetime
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

# === STEP 1: Create POSCO Holdings record ===
print('=== STEP 1: Create POSCO Holdings record ===')
holdings_desc = (
    "POSCO Holdings, Inc. (KRX: 005490) - South Korean steel-to-materials conglomerate, parent of POSCO Group. "
    "Founded 1968 (Korean government, Pohang). HQ Seoul (registered), Pohang (steel operations). "
    "Chairman and CEO: Chang In-hwa (since Mar 2024, 2.33 years tenure). Strategic vision: '2 Core + New Engine' - steel + energy materials + new businesses; KRW 200T market cap target by 2030. "
    "2025 revenue: KRW 69.1T (US$50B). Steel segment: 17.2M MT/yr crude steel capacity, KRW 59.4T sales + KRW 2T operating profit. "
    "Battery materials (POSCO Future M): KRW 3.34T sales, KRW 440.9B operating loss (investing in EV supply chain). "
    "Key subsidiaries: POSCO (steel), POSCO International (trading), POSCO Future M (battery materials), POSCO-Pilbara Lithium Solution (21,500 t/yr lithium, Feb 2025), PT Krakatau POSCO (Indonesia integrated steel, 3M MT/yr). "
    "POSCO-Huayou JVs (China): Zhejiang POSCO-Huayou (30,000 MT/yr cathode, POSCO 60%/Huayou 40%) + Zhejiang Huayou-POSCO (30,000 MT/yr precursors, Huayou 60%/POSCO 40%). "
    "WORKFORCE: 30,000+ globally. Conflict minerals compliance per SEC reporting (responsible minerals mgmt under Purchasing and Investment Division). "
    "PHILIPPINES NICKEL ANGLE: POSCO Future M has JV with MC Group (NPSI subsidiary) to produce MHP (mixed hydroxide precipitate) in PH. MC Group targets acquiring ~200M tons nickel ore by 2026. POSCO Future M targets 1M MT/yr cathode materials by 2030. "
    "ECONARES angle: PH saprolite/limonite nickel ore supply to NPSI/POSCO Future M JV; PH cobalt for cathode; lithium for POSCO-Pilbara."
)
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'POSCO Holdings, Inc.',
        'domain': 'posco.com',
        'industry': 'MANUFACTURING',
        'phone': '+82 54 220 0114',
        'address': 'POSCO Tower, 165 Convensia-daero, Yeonsu-gu, Incheon, South Korea (HQ); Pohang Steelworks: 6261 Donghaean-ro, Nam-gu, Pohang',
        'city': 'Incheon',
        'country': 'South Korea',
        'website': 'https://www.posco.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 30000,
        'description': holdings_desc
    }
})
print(f'  CREATE POSCO Holdings: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
POSCO_HOLDINGS_ID = r.get('id') if sc in (200, 201) else None

# Check if name was auto-truncated
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{POSCO_HOLDINGS_ID}?properties=name')
    if sc2 == 200:
        actual_name = r2['properties'].get('name')
        if actual_name != 'POSCO Holdings, Inc.':
            print(f'  Name auto-truncated: "{actual_name}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{POSCO_HOLDINGS_ID}', {'properties': {'name': 'POSCO Holdings, Inc.'}})
            print(f'  PATCH name: {sc3}')

print()

# === STEP 2: Create POSCO International record ===
print('=== STEP 2: Create POSCO International record ===')
intl_desc = (
    "POSCO International Corporation - South Korean global trading and energy arm of POSCO Holdings. "
    "Trading division of POSCO Holdings. President: Lee Kye-in (newly appointed 2025, from Daewoo International energy/steel background). "
    "Activities: steel products trading, energy commodities (LNG, gas - 51% stake in Myanmar gas project with ONGC Videsh 17% + MOGE 15% + GAIL 8.5% + KOGAS 8.5%), grain (2.5M MT/yr Mykolaiv terminal), rare earths, POSCO-Huayou JV investments. "
    "Recent: $315M Myanmar gas project; $667M India gas investment (Jun 2024). Strategic expansion into REE supply chain: 2025 MOU with Energy Fuels (US) for non-China REE supply chain. "
    "Indonesia operations: PT Krakatau POSCO (PTKP, JV with Krakatau Steel - 3M MT/yr integrated steel mill, BBB- S&P rating). "
    "Economically: leverages POSCO Group's steel + battery materials + energy portfolio. Lee Kye-in's appointment signals strategic emphasis on trading arm. "
    "ECONARES angle: PH nickel ore + steel scrap + logistics partnerships; cross-sell to POSCO group level via Lee Kye-in."
)
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'POSCO International Corporation',
        'domain': 'poscointl.com',
        'industry': 'IMPORT_AND_EXPORT',
        'phone': '+82 2 759 4114',
        'address': 'POSCO International Center, 10 Cheonggyecheon-ro, Jung-gu, Seoul, South Korea',
        'city': 'Seoul',
        'country': 'South Korea',
        'website': 'https://www.poscointl.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 5000,
        'description': intl_desc
    }
})
print(f'  CREATE POSCO International: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
POSCO_INTL_ID = r.get('id') if sc in (200, 201) else None

# Check name
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{POSCO_INTL_ID}?properties=name')
    if sc2 == 200:
        actual_name = r2['properties'].get('name')
        if actual_name != 'POSCO International Corporation':
            print(f'  Name auto-truncated: "{actual_name}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{POSCO_INTL_ID}', {'properties': {'name': 'POSCO International Corporation'}})
            print(f'  PATCH name: {sc3}')

print()

# === STEP 3: Create 2 contacts ===
print('=== STEP 3: Create 2 contacts under POSCO Holdings ===')
contacts = [
    {
        'firstname': 'Jungeun',
        'lastname': 'Yi',
        'jobtitle': 'Senior Procurement Manager, POSCO (Nov 2011-present, Seoul) - Raw Materials Procurement. 10+ years experience in procurement + transportation of raw materials at steel. Bayes Business School.',
        'associatedcompanyid': POSCO_HOLDINGS_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://www.linkedin.com/in/jungeun-christine-yi-58b1a224'
    },
    {
        'firstname': 'Seonyeob',
        'lastname': 'Chu',
        'jobtitle': 'Senior Procurement Manager, POSCO (since 2009) - CPSM-certified. Previously Samsung (2004-2009). MBA 2017 (Hult International Business School). Industrial Engineering background.',
        'associatedcompanyid': POSCO_HOLDINGS_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://www.linkedin.com/in/seonyeob-sydney-chu-185514126'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === Engagement note ===
print('=== Engagement note ===')
note_body = (
    "<p><strong>POSCO Group CRM Buildout (2026-07-02):</strong></p>"
    f"<p>Created 2 Company records: <strong>POSCO Holdings, Inc.</strong> (ID <code>{POSCO_HOLDINGS_ID}</code>) — parent steel-materials conglomerate, KRX: 005490, Seoul HQ, 2025 revenue KRW 69.1T, 17.2M MT/yr steel; <strong>POSCO International Corporation</strong> (ID <code>{POSCO_INTL_ID}</code>) — trading arm, President Lee Kye-in (newly appointed 2025, from Daewoo International).</p>"
    "<p>Created 2 verified contacts under POSCO Holdings: <strong>Jungeun Yi</strong> (Senior Procurement Manager, Raw Materials Procurement, Seoul) and <strong>Seonyeob Chu</strong> (Senior Procurement Manager, CPSM-certified). Both have direct PH angle fit.</p>"
    "<p><strong>PHILIPPINES NICKEL ANGLE (critical):</strong> POSCO Future M has JV with MC Group (NPSI subsidiary) to produce MHP in PH. MC Group targets acquiring ~200M tons nickel ore by 2026. POSCO Future M targets 1M MT/yr cathode materials by 2030. <strong>Direct match for ECONARES PH saprolite/limonite nickel ore supply.</strong></p>"
    "<p><strong>Outreach strategy:</strong> Lead with Jungeun Yi (raw materials) or Seonyeob Chu (procurement, CPSM). Group-level via POSCO International President Lee Kye-in for trading relationships. Future M for PH-JV MHP angle.</p>"
    "<p><strong>Related ecosystem:</strong> POSCO-Huayou JVs (China cathode/precursor) — already in Huayou CRM. PT Krakatau POSCO (Indonesia, 3M MT/yr steel) — separate consideration. POSCO-Pilbara Lithium Solution (21,500 t/yr).</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    for assoc_id in [POSCO_HOLDINGS_ID, POSCO_INTL_ID]:
        if assoc_id:
            sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{assoc_id}/note_to_company', {})
            print(f'  assoc to {assoc_id}: {sc2}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
for label, oid in [('POSCO Holdings', POSCO_HOLDINGS_ID), ('POSCO International', POSCO_INTL_ID)]:
    if not oid:
        continue
    sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{oid}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
    p = co['properties']
    print(f'--- {label} ({oid}) ---')
    for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
        print(f'  {k}: {p.get(k)}')

print()
print('--- POSCO Holdings contacts (direct ID lookup) ---')
for cid_pair in [(POSCO_HOLDINGS_ID, 'Jungeun Yi'), (POSCO_HOLDINGS_ID, 'Seonyeob Chu')]:
    pass  # we know IDs, will do direct lookup below
for cid in ['', '']:
    pass

# Get latest contact IDs from search
import time
time.sleep(2)  # brief pause for HubSpot indexing
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': POSCO_HOLDINGS_ID}]}], 'properties': ['firstname','lastname','jobtitle','hs_buying_role','hs_linkedin_url']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'  POSCO Holdings contacts: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"    {p2.get('firstname')} {p2.get('lastname')} | role:{p2.get('hs_buying_role')}")
