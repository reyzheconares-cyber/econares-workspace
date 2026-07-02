"""Jinchuan Group cleanup:
1. Audit existing JCI record (324207665867)
2. KYC enrich JCI + add parent association note
3. Create Jinchuan Group (parent) record
4. Create 3 contacts: Cook Liu (DECISION_MAKER), Gao Tianpeng (DECISION_MAKER), Cheng Yonghong (DECISION_MAKER)
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
JCI_ID = '324207665867'

# === STEP 1: Audit JCI record ===
print('=== STEP 1: Audit existing JCI record ===')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{JCI_ID}?properties=name,domain,industry,description,phone,address,city,state,country,website,hs_target_account')
if sc == 200:
    p = co.get('properties', {})
    for k in ['name','domain','industry','phone','address','city','state','country','website','hs_target_account']:
        v = p.get(k)
        if v: print(f'  {k}: {v}')
    print(f'  description[:80]: {(p.get("description") or "")[:80]}')
else:
    print(f'  JCI not found: {sc}')

# Check current contacts
print()
print('--- JCI contacts ---')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': JCI_ID}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'  total: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"    ID:{c['id']} | {p2.get('firstname')} {p2.get('lastname')} | {p2.get('jobtitle')}")

print()

# === STEP 2: KYC enrich JCI record ===
print('=== STEP 2: KYC enrich JCI record ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{JCI_ID}', {
    'properties': {
        'industry': 'MINING_METALS',
        'phone': '+852 2828 9288',
        'address': 'Unit 3701, 37/F, AIA Central, 1 Connaught Road Central, Central, Hong Kong',
        'city': 'Hong Kong',
        'country': 'Hong Kong',
        'website': 'https://www.jinchuan-intl.com',
        'hs_target_account': 'tier_1',
        'description': "Jinchuan International Resources Co. Ltd (JCI; HKEX: 2362) - Hong Kong-listed subsidiary of state-owned Jinchuan Group Co., Ltd. (Gansu Provincial Government, PRC). 60.73% owned by Jinchuan Group (HK). 10 non-ferrous metal mines globally: 1.06M MT nickel + 8.8M MT copper + 510,000 MT cobalt + 413 MT PGM. Indonesia operations: WP&RKA Laterite Nickel Mine (Obi Island, North Maluku; 60% WP + 40% RKA) - 2.2M MT/yr nickel laterite ore export sales target; PT KRS Ferronikel Indonesia (55,000 MT/yr); PT Usmi Nickel Matte (50,000 MT Ni/yr). 150 MW captive CFPP. Africa: Zambia (Munali Nickel, 85% Metorex), Mexico (Bahuerachi Copper), South Africa (Metorex 85% + ZCCM 15% Ruashi/Selkirk). CONTEXT: Indonesia smelters (incl. JCI WP&RKA) are NOW importing Philippine nickel ore - 51.3% YoY import growth in 2025 (15.84M MT). ECONARES angle: PH saprolite/limonite nickel ore for WP&RKA Si:Mg blending."
    }
})
print(f'  PATCH JCI: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()

# === STEP 3: Create Jinchuan Group (parent) record ===
print('=== STEP 3: Create Jinchuan Group (parent) record ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Jinchuan Group Co., Ltd.',
        'domain': 'jnmc.com',
        'industry': 'MINING_METALS',
        'phone': '+86 0935 881 1111',
        'address': 'No. 1 Jinchuan Road, Jinchang City, Gansu Province, China',
        'city': 'Jinchang',
        'state': 'Gansu',
        'country': 'China',
        'website': 'http://en.jnmc.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 50000,
        'description': "Jinchuan Group Co., Ltd. (金川集团) - STATE-OWNED Chinese mining conglomerate (under Gansu Provincial Government). Founded 1959. Annual production: 200,000 MT nickel, 1,000,000 MT copper, 15,000 MT cobalt, 10 MT PGM. Known as China's 'Nickel City' (世界镍都). Owns 10+ non-ferrous metal mines globally via JCI (HKEX: 2362) subsidiary. Chairman: Ruan Ying (Party Secretary). Indonesia operations via WP&RKA (Obi Island, North Maluku) + KRS + Usmi. International trading arm: Jinchuan Group Shanghai Metal Resources Co., Ltd. Annual output 400,000 MT ferronickel + 50,000 MT nickel matte from Indonesia. Owns world's 3rd largest copper-nickel sulfide ore deposit (Jinchang). CONTEXT: Indonesia quota cuts 2025 → Jinchuan imports Philippine nickel ore for Si:Mg blending. ECONARES primary opportunity: PH saprolite/limonite nickel ore to WP&RKA."
    }
})
print(f'  CREATE Jinchuan Group: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

PARENT_ID = r.get('id') if sc in (200, 201) else None

print()

# === STEP 4: Create 3 contacts under parent ===
print('=== STEP 4: Create 3 contacts (under parent) ===')
contacts = [
    {
        'firstname': 'Cook',
        'lastname': 'Liu',
        'jobtitle': 'Commodity Trader (Trade Supervisor) — Jinchuan Group Shanghai Metal Resources Co., Ltd. (Sep 2025-present). Networks with Rio Tinto, Trafigura, Nornickel, CODELCO, Jiangxi Copper. Negotiates long-term + spot contracts of copper cathode.',
        'associatedcompanyid': PARENT_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://au.linkedin.com/in/qifanliu'
    },
    {
        'firstname': 'Gao',
        'lastname': 'Tianpeng',
        'jobtitle': 'CEO & Executive Director, Jinchuan International (HKEX: 2362). Age 54, BEng + EMBA. Since Aug 2017. In JCG since 1994 overseeing cost mgmt, financial mgmt, international trading, risk mgmt, FX, capital ops.',
        'associatedcompanyid': PARENT_ID,
        'hs_lead_status': 'OPEN',
        'lifecyclestage': 'opportunity',
        'hs_buying_role': 'DECISION_MAKER'
    },
    {
        'firstname': 'Cheng',
        'lastname': 'Yonghong',
        'jobtitle': 'Executive Chairman, Jinchuan International (HKEX: 2362). Joined Group as director of Metorex Aug 2017. GM of Ruashi SAS Apr 2015-Mar 2020. Chairman + CEO of Metorex Mar 2020-Sep 2024. Head of International Business of JCG.',
        'associatedcompanyid': PARENT_ID,
        'hs_lead_status': 'OPEN',
        'lifecyclestage': 'opportunity',
        'hs_buying_role': 'DECISION_MAKER'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === STEP 5: Note linking JCI to parent ===
print('=== STEP 5: Create engagement note (JCI → Parent link) ===')
import datetime
note_body = (
    "<p><strong>Jinchuan Group CRM Cleanup (2026-07-02):</strong></p>"
    f"<p>Created parent record <strong>Jinchuan Group Co., Ltd.</strong> (ID <code>{PARENT_ID}</code>) — state-owned parent in Jinchang, Gansu, China. KYC-enriched existing JCI subsidiary record (ID <code>{JCI_ID}</code>) with HKEX: 2362 details, Indonesian operations (WP&amp;RKA, KRS, Usmi), Zambia/Mexico/South Africa mines via Metorex.</p>"
    "<p>Created 3 verified contacts: <strong>Cook Liu</strong> (Commodity Trader, Jinchuan Group Shanghai Metal Resources — primary outreach target for PH nickel ore); <strong>Gao Tianpeng</strong> (CEO, JCI); <strong>Cheng Yonghong</strong> (Executive Chairman, JCI).</p>"
    "<p><strong>Outreach strategy:</strong> Lead with <em>Cook Liu</em> (Commodity Trader, Shanghai office) — direct angle on Philippine saprolite/limonite nickel ore supply to WP&amp;RKA (Obi Island, North Maluku) for Si:Mg blending. Cook negotiates long-term + spot contracts and networks with Rio Tinto/Trafigura/Nornickel/CODELCO — direct match for ECONARES' PH nickel ore angle.</p>"
    "<p>Note: All 3 contacts linked to parent record (not JCI) — recommend re-associating Cook Liu to JCI if primary relationship is via HKEX-listed entity.</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    for assoc_type, assoc_id in [('companies', PARENT_ID), ('companies', JCI_ID)]:
        sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/{assoc_type}/{assoc_id}/note_to_company', {})
        print(f'  assoc {assoc_type}/{assoc_id}: {sc2}')

print()

# === STEP 6: Final read-back ===
print('=== STEP 6: Final read-back ===')
print('--- Jinchuan Group (parent) ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{PARENT_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
p = co['properties']
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
    print(f'  {k}: {p.get(k)}')

print()
print('--- JCI ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{JCI_ID}?properties=name,industry,phone,city,country,website,hs_target_account')
p = co['properties']
for k in ['name','industry','phone','city','country','website','hs_target_account']:
    print(f'  {k}: {p.get(k)}')

print()
print('--- Parent contacts ---')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': PARENT_ID}]}], 'properties': ['firstname','lastname','jobtitle','hs_buying_role','hs_linkedin_url']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'  total: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"    {p2.get('firstname')} {p2.get('lastname')} | role:{p2.get('hs_buying_role')}")
    if p2.get('hs_linkedin_url'):
        print(f"      linkedin: {p2['hs_linkedin_url']}")
