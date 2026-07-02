"""Huayou Cobalt cleanup:
1. KYC enrich existing record (325140716245)
2. Create 2 contacts: Xingwei Liang (DECISION_MAKER), Hongliang Chen (DECISION_MAKER)
3. Create engagement note linking actions
4. Final read-back verification
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
HUAYOU_ID = '325140716245'

# === STEP 1: KYC enrich ===
print('=== STEP 1: KYC enrich Huayou Cobalt ===')
desc = (
    "Zhejiang Huayou Cobalt Co., Ltd. (华友钴业, SH603799) - PUBLIC-LISTED Chinese new energy materials conglomerate. "
    "Founded 2002; HQ Tongxiang, Zhejiang. CEO Hongliang Chen (since Jul 2016, 9.92 yrs tenure). "
    "Ranked 278th Fortune China 500 (2025); 280th Fortune China 500 Private (2024). 10,001+ employees. "
    "5 business sectors: new energy industry, new material industry, Indonesia nickel industry, Africa resource industry, recycling industry. "
    "Vertical integration: cobalt + nickel + lithium resources (DRC mines) -> non-ferrous smelting -> lithium battery materials -> recycling. "
    "Active Indonesia operations: PT Huayue Nickel Cobalt (IMIP Morowali, RMI-Compliant 2024) + PT Huafei Nickel Cobalt (IWIP Halmahera, production Q1 2024). "
    "POSCO JVs: Zhejiang POSCO-Huayou (cathode 30,000 MT/yr, POSCO 60% / Huayou 40%) + Zhejiang Huayou-POSCO (precursors 30,000 MT/yr, Huayou 60% / POSCO 40%). "
    "30+ subsidiaries globally incl. CDM Company (trading), Huayou Hong Kong, Huayou Mining HK, MIKAS, Guangxi Huayou. "
    "CONTEXT: Indonesia smelters (incl. Huayou's Huafei + Huayue) are NOW importing Philippine nickel ore - 51.3% YoY import growth in 2025 (15.84M MT). "
    "ECONARES angle: PH saprolite/limonite nickel ore supply to Huafei/Huayue for HPAL feed. PH cobalt-copper angle via CDM (DRC procurement)."
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{HUAYOU_ID}', {
    'properties': {
        'domain': 'huayou.com',
        'industry': 'CHEMICALS',
        'phone': '+86 0573 8858 1888',
        'address': 'No. 79 Wuzhen East Road, Tongxiang Economic Development Zone, Tongxiang, Zhejiang Province, China',
        'city': 'Tongxiang',
        'state': 'Zhejiang',
        'country': 'China',
        'website': 'https://www.huayou.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 10000,
        'description': desc
    }
})
print(f'  PATCH: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()

# === STEP 2: Create 2 contacts ===
print('=== STEP 2: Create 2 contacts ===')
contacts = [
    {
        'firstname': 'Xingwei',
        'lastname': 'Liang',
        'jobtitle': 'Commercial Manager (Commodity Sales & Procurement) - CDM (Huayou) — Sep 2025-present, Lubumbashi DRC. Procurement + sales of bulk auxiliary materials, chemical products, copper cathodes. Import/export trade process + market analysis. Imperial College London.',
        'associatedcompanyid': HUAYOU_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://cd.linkedin.com/in/xingwei-liang'
    },
    {
        'firstname': 'Hongliang',
        'lastname': 'Chen',
        'jobtitle': 'CEO, Zhejiang Huayou Cobalt Co., Ltd. (SH603799) — since Jul 2016, 9.92 years tenure, 0.025% equity stake. Drives full Huayou Group strategy across 5 business sectors.',
        'associatedcompanyid': HUAYOU_ID,
        'hs_lead_status': 'OPEN',
        'lifecyclestage': 'opportunity',
        'hs_buying_role': 'DECISION_MAKER'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === STEP 3: Engagement note ===
print('=== STEP 3: Create engagement note ===')
note_body = (
    "<p><strong>Huayou Cobalt CRM Enrichment (2026-07-02):</strong></p>"
    f"<p>KYC-enriched Zhejiang Huayou Cobalt Company record (ID <code>{HUAYOU_ID}</code>) — added industry (CHEMICALS), HQ address (Tongxiang Zhejiang), phone, website, tier_1 flag, 10,000+ employees, and rich description with Indonesia + POSCO JV + PH nickel ore angle.</p>"
    "<p>Created 2 verified contacts: <strong>Xingwei Liang</strong> (Commercial Manager, CDM/Huayou — DRC procurement, handles bulk auxiliary materials + copper cathodes, Imperial College London) and <strong>Hongliang Chen</strong> (CEO, since Jul 2016, 9.92 yrs tenure, 0.025% equity).</p>"
    "<p><strong>Outreach strategy:</strong> Xingwei Liang is the direct match for PH nickel ore angle (procurement role at CDM). Hongliang Chen for group-level strategic partnership (long-term, multi-commodity). NOTE: CDM is DRC-focused — for Indonesia nickel ore angle (Huafei/Huayue HPAL plants), recommend finding a dedicated Indonesia-procurement contact as follow-up.</p>"
    "<p><strong>Related context:</strong> Indonesia smelters (incl. Huayou's Huafei + Huayue at IMIP + IWIP) are NOW importing Philippine nickel ore — 51.3% YoY import growth in 2025 (15.84M MT). PH saprolite/limonite for HPAL feed = direct opportunity. POSCO-Huayou JVs open cathode/precursor precursor angle.</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{HUAYOU_ID}/note_to_company', {})
    print(f'  assoc to Huayou: {sc2}')

print()

# === STEP 4: Final read-back ===
print('=== STEP 4: Final read-back ===')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{HUAYOU_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
p = co['properties']
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
    print(f'  {k}: {p.get(k)}')

print()
print('--- Contacts (search by lastname to avoid indexing delay) ---')
for ln, fn in [('Liang', 'Xingwei'), ('Chen', 'Hongliang')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role','hs_lead_status','hs_linkedin_url','associatedcompanyid']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p2 = c['properties']
        if p2.get('firstname') == fn and p2.get('associatedcompanyid') == HUAYOU_ID:
            print(f"  ID:{c['id']} | {p2.get('firstname')} {p2.get('lastname')} | {p2.get('jobtitle')[:60]}... | role:{p2.get('hs_buying_role')} | status:{p2.get('hs_lead_status')}")
            if p2.get('hs_linkedin_url'):
                print(f"    linkedin: {p2['hs_linkedin_url']}")
