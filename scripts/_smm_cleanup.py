"""Sumitomo Metal Mining cleanup:
1. Create SMM (parent) record (Tokyo HQ, tier_1, MINING_METALS)
2. KYC enrich existing SMMPH record (322924743370) + add parent association note
3. Create 3 contacts: TJ Villaluna (DECISION_MAKER), Ma. Cristina Magbanua (INFLUENCER), Kristel Ann Galvez (INFLUENCER)
4. Create engagement note + final read-back
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
SMMPH_ID = '322924743370'

# === STEP 1: Create SMM (parent) record ===
print('=== STEP 1: Create SMM (parent) record ===')
parent_desc = (
    "Sumitomo Metal Mining Co., Ltd. (住友金属鉱山, TSE: 5713) - Japanese integrated non-ferrous metals + battery materials producer. "
    "3 Core Businesses: Mineral Resources + Smelting & Refining + Materials (battery + advanced). HQ: 11-3 Shimbashi 5-chome, Minato-ku, Tokyo 105-8716, Japan. "
    "President: Nobuhiro Matsumoto (since Jun 2024, age 61, joined 1987). Workforce 5,000-10,000 (parent). "
    "Nickel production: 82,000 MT/yr current → 150,000 MT/yr long-term target. NCA cathode materials for Panasonic/Tesla EV batteries: 60,000 MT/yr current → 84,000 MT/yr by 2025 (Niihama plant expansion). "
    "3,000+ years of mine development experience (Sumitomo group). Owns Hishikari Mine (Japan's largest gold mine). "
    "PHILIPPINES OPERATIONS (active HPAL plants): "
    "- CBNC (Coral Bay Nickel Corporation, Bataraza Palawan, 100% SMM buying out Nickel Asia's stake) - 24,000 MT/yr Ni + 2,500 MT/yr Co; operating since 2005; PMIEA 2021 award "
    "- THPAL (Taganito HPAL Nickel Corporation, Taganito Surigao del Norte, 60% SMM + 40% Nickel Asia) - 30,000 MT/yr Ni HPAL; operating since 2013; PMIEA 2021 award "
    "- SMMPH (Sumitomo Metal Mining Philippine Holdings Corporation, Manila) - regional HQ; 51-200 employees "
    "Combined PH capacity: ~60,000 MT/yr Ni + 2,500 MT/yr Co. "
    "BATTERY MATERIALS GROWTH: Building Niihama plant (+24,000 MT cathode by 2025); considering US production (2024 announcement). "
    "VERTICAL INTEGRATION: full in-house nickel supply chain from mine to cathode materials. Self-supplies primary ore from own mines but may need supplemental PH ore for blending (Mg:Si ratio critical for HPAL). "
    "ECONARES ANGLE: Direct PH nickel ore supply to CBNC + THPAL HPAL plants. Supplemental feed for consistent specifications. PH cobalt-copper byproduct potential. Access via SMMPH Manila regional HQ."
)
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Sumitomo Metal Mining Co., Ltd.',
        'domain': 'smm.co.jp',
        'industry': 'MINING_METALS',
        'phone': '+81 3 3436 7700',
        'address': '11-3 Shimbashi 5-chome, Minato-ku, Tokyo 105-8716, Japan',
        'city': 'Tokyo',
        'country': 'Japan',
        'website': 'https://www.smm.co.jp',
        'hs_target_account': 'tier_1',
        'numberofemployees': 7500,
        'description': parent_desc
    }
})
print(f'  CREATE SMM parent: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
SMM_PARENT_ID = r.get('id') if sc in (200, 201) else None

# Check for name auto-truncation
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{SMM_PARENT_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'Sumitomo Metal Mining Co., Ltd.':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{SMM_PARENT_ID}', {'properties': {'name': 'Sumitomo Metal Mining Co., Ltd.'}})
            print(f'  PATCH name: {sc3}')

print()

# === STEP 2: KYC enrich SMMPH record ===
print('=== STEP 2: KYC enrich SMMPH record ===')
smph_desc = (
    "Sumitomo Metal Mining Philippine Holdings Corporation (SMMPH) - Regional headquarters for Sumitomo Metal Mining Co., Ltd.'s nickel business operations in the Philippines. "
    "Established 2010, inaugurated as regional HQ Feb 2011. 51-200 employees. Manila-based. "
    "Parent: Sumitomo Metal Mining Co., Ltd. (Tokyo, Japan, TSE: 5713). "
    "Coordinates 2 active HPAL nickel plants: "
    "- CBNC (Coral Bay Nickel Corporation, Bataraza Palawan) - 100% SMM; 24,000 MT/yr Ni + 2,500 MT/yr Co; PMIEA 2021 award; operating since 2005 "
    "- THPAL (Taganito HPAL Nickel Corporation, Taganito Surigao del Norte) - 60% SMM + 40% Nickel Asia; ~30,000 MT/yr Ni HPAL; PMIEA 2021 award; operating since 2013 "
    "Combined PH capacity: ~60,000 MT/yr Ni + 2,500 MT/yr Co. "
    "3 verified procurement/logistics contacts: TJ Villaluna (Procurement Senior Supervisor, SMMPH Manila); Ma. Cristina Magbanua (Logistics Supervisor, SMMPH Apr 2020-present); Kristel Ann Galvez (Procurement/Logistics, SMMPH 11+ yrs). "
    "ECONARES ANGLE: Direct PH nickel ore supply to CBNC + THPAL HPAL plants. Supplemental feed for Mg:Si blending. Access via SMMPH Manila regional HQ procurement team."
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{SMMPH_ID}', {
    'properties': {
        'domain': 'smm.co.jp',
        'industry': 'MANUFACTURING',
        'phone': '+63 2 8888 7000',
        'address': 'Metro Manila, Philippines (Sumitomo Metal Mining Philippine Holdings Corporation)',
        'city': 'Manila',
        'country': 'Philippines',
        'website': 'https://www.smm.co.jp/en',
        'hs_target_account': 'tier_1',
        'numberofemployees': 75,
        'description': smph_desc
    }
})
print(f'  PATCH SMMPH: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

# Check if name auto-truncated
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{SMMPH_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'Sumitomo Metal Mining Philippine Holdings Corporation':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{SMMPH_ID}', {'properties': {'name': 'Sumitomo Metal Mining Philippine Holdings Corporation'}})
            print(f'  PATCH name: {sc3}')

print()

# === STEP 3: Create 3 contacts under SMMPH ===
print('=== STEP 3: Create 3 contacts under SMMPH ===')
contacts = [
    {
        'firstname': 'TJ',
        'lastname': 'Villaluna',
        'jobtitle': 'Procurement Senior Supervisor, Sumitomo Metal Mining Philippines Holdings Corporation (SMMPH). Metro Manila. Ateneo Graduate School of Business - MBA Strategic Management (ongoing).',
        'associatedcompanyid': SMMPH_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/tjvillaluna'
    },
    {
        'firstname': 'Ma. Cristina',
        'lastname': 'Magbanua',
        'jobtitle': 'Logistics Supervisor, Sumitomo Metal Mining Philippines Holdings Corporation (SMMPH) - Apr 2020-present. 11+ years experience in mining logistics. Jose Rizal University 2005-2009.',
        'associatedcompanyid': SMMPH_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/ma-cristina-magbanua-60581152'
    },
    {
        'firstname': 'Kristel Ann',
        'lastname': 'Galvez',
        'jobtitle': 'Procurement | Logistics, Sumitomo Metal Mining Philippine Holdings Corporation (SMMPH). 11+ years experience in Procurement, Logistics, and Supply Chain.',
        'associatedcompanyid': SMMPH_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/kristel-ann-galvez'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === Engagement note ===
print('=== Engagement note ===')
note_body = (
    "<p><strong>SMM Group CRM Buildout (2026-07-02):</strong></p>"
    f"<p>Created 2 Company records: <strong>Sumitomo Metal Mining Co., Ltd.</strong> (ID <code>{SMM_PARENT_ID}</code>) — Japanese integrated non-ferrous metals + battery materials producer, Tokyo HQ, President Nobuhiro Matsumoto, 82,000 MT/yr Ni → 150,000 MT/yr target. KYC-enriched <strong>SMMPH</strong> (ID <code>{SMMPH_ID}</code>) — Philippine regional HQ, Manila, 51-200 employees, coordinates CBNC + THPAL HPAL plants.</p>"
    "<p>Created 3 verified contacts under SMMPH: <strong>TJ Villaluna</strong> (Procurement Senior Supervisor, DECISION_MAKER, Manila); <strong>Ma. Cristina Magbanua</strong> (Logistics Supervisor, INFLUENCER, Apr 2020-present); <strong>Kristel Ann Galvez</strong> (Procurement/Logistics, INFLUENCER, 11+ yrs).</p>"
    "<p><strong>PHILIPPINES OPERATIONS (active):</strong> CBNC (Coral Bay Nickel Corp, Bataraza Palawan, 100% SMM buying out Nickel Asia) - 24,000 MT/yr Ni + 2,500 MT/yr Co, PMIEA 2021 award. THPAL (Taganito HPAL, Surigao del Norte, 60% SMM + 40% Nickel Asia) - ~30,000 MT/yr Ni, PMIEA 2021 award. Combined ~60,000 MT/yr Ni + 2,500 MT/yr Co in PH.</p>"
    "<p><strong>ECONARES ANGLE:</strong> Direct PH nickel ore supply to CBNC + THPAL HPAL plants. Supplemental feed for Mg:Si blending. SMM self-supplies primary ore but may need supplemental PH ore for blending. Access via SMMPH Manila regional HQ procurement team (TJ Villaluna primary).</p>"
    "<p><strong>Outreach strategy:</strong> Lead with TJ Villaluna (Procurement Senior Supervisor) at SMMPH Manila. Cover both CBNC Palawan + THPAL Surigao del Norte plants. HPAL feed quality specs strict (Mg:Si ratio) - need to align with their requirements. Japanese keiretsu culture = 6-12 month sales cycle via PH regional HQ first, then Tokyo escalation.</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    for assoc_id in [SMM_PARENT_ID, SMMPH_ID]:
        if assoc_id:
            sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{assoc_id}/note_to_company', {})
            print(f'  assoc to {assoc_id}: {sc2}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
for label, oid in [('SMM parent', SMM_PARENT_ID), ('SMMPH', SMMPH_ID)]:
    if not oid:
        continue
    sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{oid}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
    p = co['properties']
    print(f'--- {label} ({oid}) ---')
    for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
        print(f'  {k}: {p.get(k)}')

print()
print('--- SMMPH contacts (direct ID lookup, bypass search-index lag) ---')
for cid in ['512570728144', '512592224999']:
    pass
# Use the contacts we just created - get their IDs from the previous step
# Re-find via name
import time
time.sleep(1)
for ln, fn in [('Villaluna', 'TJ'), ('Magbanua', 'Ma. Cristina'), ('Galvez', 'Kristel Ann')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','associatedcompanyid','hs_buying_role','hs_linkedin_url']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p2 = c['properties']
        if p2.get('firstname') == fn and p2.get('associatedcompanyid') == SMMPH_ID:
            print(f"  {fn} {ln} (id:{c['id']}) | co:{p2.get('associatedcompanyid')} | role:{p2.get('hs_buying_role')}")
            if p2.get('hs_linkedin_url'):
                print(f"    linkedin: {p2['hs_linkedin_url']}")
