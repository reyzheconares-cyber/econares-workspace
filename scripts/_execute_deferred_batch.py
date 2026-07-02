"""
Parallel batch execution of deferred HubSpot tasks:
1. CEMEX Philippines → Concreat Holdings rename + KYC enrichment (existing 2 records)
2. Eagle Cement — create Company record + Ronaldo Jimeno contact
3. Northern Cement — create Company record + Ramon S. Ang + Van Jayro Plata
4. SteelAsia — create Company record + Benjamin Yao + Ryan James Hernandez + Kathleen Mayhay-Mendoza
5. PT Vale Indonesia — create Company record (monitoring) + Bernardus Irmanto + Ramliah Frenova
6. PT Gunbuster / Delong — KYC enrich 2 existing Delong records + create Theo + Dwi under Indonesia Ops
7. PSC Batangas validation — read-only check (confirm no PSC-Batangas entity exists)

Pre-flight + writes + read-back. KYC-first rule: only fill blanks; never overwrite verified data.
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

# === Pre-flight: verify all source records exist before any write ===
print('=== PRE-FLIGHT ===')
for label, oid, kind in [
    ('CEMEX Philippines', '320080163556', 'company'),
    ('APO Cement', '321897429737', 'company'),
    ('Delong China parent', '318104838865', 'company'),
    ('Delong Indonesia Ops', '321962321599', 'company'),
    ('QPL (sanity check)', '326532899525', 'company'),
]:
    sc, r = http('GET', f'{BASE}/crm/v3/objects/{kind}s/{oid}?properties=name')
    if sc == 200:
        print(f'  OK {label} ({oid}): {r["properties"].get("name")}')
    else:
        print(f'  MISSING {label} ({oid}): {sc}')

print()

# ===================================================================
# STEP 1: CEMEX Philippines rename + KYC enrichment (existing 320080163556)
# ===================================================================
print('=== STEP 1: CEMEX → Concreat Holdings rename + KYC ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/320080163556', {
    'properties': {
        'name': 'Concreat Holdings Philippines, Inc.',
        'domain': 'chp.com.ph',
        'industry': 'MANUFACTURING',
        'phone': '+63 2 8856-2888',
        'address': '29th Floor, Petron Mega Plaza, 358 Senator Gil Puyat Avenue, Makati City',
        'city': 'Makati City',
        'state': 'NCR',
        'country': 'Philippines',
        'hs_target_account': 'tier_1',
        'description': 'Concreat Holdings Philippines, Inc. (formerly CEMEX Holdings Philippines, Inc. / CHP). 51% owned by DMCI Holdings + Semirara Mining + Dacon = 89.86% controlling stake (acquisition closed Dec 2, 2024). Plants: APO Cement Corporation (Naga, Cebu) + Solid Cement Corporation (Antipolo, Rizal). Combined capacity 7.2M tons/yr. Brands: APO, Rizal, Island. Vertical coal integration via Semirara — primary opportunity is alternative fuels/biomass/RDF, not coal.'
    }
})
print(f'  PATCH Concreat: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:120]}')

# Also fix APO Cement industry
sc2, r2 = http('PATCH', f'{BASE}/crm/v3/objects/companies/321897429737', {
    'properties': {
        'industry': 'MANUFACTURING',
        'hs_target_account': 'tier_1',
        'phone': '+63 32 489-9000',
        'city': 'Naga',
        'state': 'Cebu',
        'website': 'apocement.com.ph'
    }
})
print(f'  PATCH APO Cement: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:120]}')

# Set buying roles on existing CEMEX/Concreat contacts
for cid, role, status in [
    ('477138643696', 'DECISION_MAKER', 'OPEN'),  # Rey Tolosa - VP Procurement
    ('476653187805', 'INFLUENCER', 'NEW'),  # Albarr Abusaman
    ('478270415572', 'INFLUENCER', 'NEW'),  # Bong Acacio - AFM
    ('478250983129', 'INFLUENCER', 'NEW'),  # Chai Sibal - AFM
]:
    sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{cid}', {
        'properties': {'hs_buying_role': role, 'hs_lead_status': status}
    })
    print(f'  PATCH contact {cid}: {sc3}')

print()

# ===================================================================
# STEP 2: Eagle Cement — create Company + Ronaldo Jimeno contact
# ===================================================================
print('=== STEP 2: Eagle Cement ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Eagle Cement Corporation',
        'domain': 'eaglecement.com.ph',
        'industry': 'MANUFACTURING',
        'phone': '+63 44 769-2888',
        'address': 'Barangay Akle, San Ildefonso, Bulacan',
        'city': 'San Ildefonso',
        'state': 'Bulacan',
        'country': 'Philippines',
        'website': 'https://www.eaglecement.com.ph',
        'hs_target_account': 'tier_1',
        'numberofemployees': 1000,
        'description': 'Eagle Cement Corporation (PSE: EAGLE) — largest single-site cement plant in Philippines (8.6M MT/yr capacity at Bulacan; plus Lemery Batangas beam plant). 88.5% owned by San Miguel Corporation (SMC) since Dec 2022 acquisition (P97B). Chairman/CEO Benjamin Yao. Active alternative fuels program (per EIA 2022). Primary opportunity: biomass/PKS/RDF; secondary: logistics.'
    }
})
print(f'  create Eagle Cement: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:120]}')
if sc in (200, 201):
    eagle_id = r['id']
    sc2, r2 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Ronaldo',
            'lastname': 'Jimeno',
            'jobtitle': 'Procurement Manager',
            'associatedcompanyid': eagle_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'DECISION_MAKER',
            'hs_linkedin_url': 'https://ph.linkedin.com/in/ronaldo-jimeno-38b71717'
        }
    })
    print(f'  create Jimeno: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:120]}')

print()

# ===================================================================
# STEP 3: Northern Cement — create Company + Ramon S. Ang + Van Jayro Plata
# ===================================================================
print('=== STEP 3: Northern Cement ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Northern Cement Corporation',
        'domain': 'ncc.com.ph',
        'industry': 'MANUFACTURING',
        'phone': '+63 2 8849-3000',
        'address': '3rd Floor Archen Building, 155 EDSA, Barangay Wack-Wack, Mandaluyong City 1555',
        'city': 'Mandaluyong City',
        'state': 'NCR',
        'country': 'Philippines',
        'website': 'https://ncc.com.ph',
        'hs_target_account': 'tier_1',
        'description': 'Northern Cement Corporation (NCC) — 100% owned by SMEII (San Miguel Equity Investments Inc.); Ramon S. Ang serves as President & CEO (also Chairman of SMC + Eagle Cement). Plant: Labayug, Sison, Pangasinan. New 5,000 t/d LOESCHE production line added (existing 2,500 t/d). Plant phone: (075) 541 8030. Email pattern: @ncc.sanmiguel.com.ph. Vertical coal integration via SMC/Semirara.'
    }
})
print(f'  create Northern Cement: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:120]}')
if sc in (200, 201):
    ncc_id = r['id']
    sc2, r2 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Ramon',
            'lastname': 'Ang',
            'jobtitle': 'President & CEO, Northern Cement Corporation (also Chairman of SMC + Eagle Cement)',
            'associatedcompanyid': ncc_id,
            'hs_lead_status': 'OPEN',
            'lifecyclestage': 'opportunity',
            'hs_buying_role': 'DECISION_MAKER',
            'source': 'MPIC board page, Wikipedia'
        }
    })
    print(f'  create Ramon Ang: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:120]}')
    sc3, r3 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Van Jayro',
            'lastname': 'Plata',
            'jobtitle': 'Process Control Engineer',
            'associatedcompanyid': ncc_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'INFLUENCER',
            'hs_linkedin_url': 'https://ph.linkedin.com/in/van-jayro-plata-41a7911a4'
        }
    })
    print(f'  create Van Jayro Plata: {sc3} | {r3.get("id") if sc3 in (200,201) else r3.get("message","")[:120]}')

print()

# ===================================================================
# STEP 4: SteelAsia Manufacturing — create Company + 3 contacts
# ===================================================================
print('=== STEP 4: SteelAsia Manufacturing ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'SteelAsia Manufacturing Corporation',
        'domain': 'steelasia.com',
        'industry': 'MANUFACTURING',
        'phone': '+63 2 8888-5999',
        'address': '25th Floor, Ore Central Tower, 31st Street corner 9th Avenue, Bonifacio Global City, Taguig, Metro Manila',
        'city': 'Taguig',
        'state': 'NCR',
        'country': 'Philippines',
        'website': 'https://www.steelasia.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 2000,
        'description': 'SteelAsia Manufacturing Corporation (SAMC) — Philippine flagship reinforcing steel bar (rebar) producer. ~50% rebar market share. Founded 1965. Chairman/President/CEO: Benjamin Yao. Current capacity 2.5M MT/yr → expanding to 4.8M MT/yr by 2028 (₱75B expansion incl. P30B Candelaria Quezon plant commissioning 2027). Plants: Meycauayan Bulacan, Calaca Batangas, Carcar Cebu, Davao, Villanueva MisOr, Lemery Batangas, +new Candelaria Quezon 2027.'
    }
})
print(f'  create SteelAsia: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:120]}')
if sc in (200, 201):
    steel_id = r['id']
    sc2, r2 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Benjamin',
            'lastname': 'Yao',
            'jobtitle': 'Chairman, President & CEO',
            'associatedcompanyid': steel_id,
            'hs_lead_status': 'OPEN',
            'lifecyclestage': 'opportunity',
            'hs_buying_role': 'DECISION_MAKER',
            'source': 'ZoomInfo, PNA references'
        }
    })
    print(f'  create Benjamin Yao: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:120]}')
    sc3, r3 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Ryan James',
            'lastname': 'Hernandez',
            'jobtitle': 'Procurement Lead',
            'associatedcompanyid': steel_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'INFLUENCER',
            'hs_linkedin_url': 'https://ph.linkedin.com/in/ryanjameshernandez14'
        }
    })
    print(f'  create Ryan Hernandez: {sc3} | {r3.get("id") if sc3 in (200,201) else r3.get("message","")[:120]}')
    sc4, r4 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Kathleen',
            'lastname': 'Mayhay-Mendoza',
            'jobtitle': 'Procurement Manager',
            'associatedcompanyid': steel_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'DECISION_MAKER',
            'source': 'RocketReach verified'
        }
    })
    print(f'  create Kathleen Mendoza: {sc4} | {r4.get("id") if sc4 in (200,201) else r4.get("message","")[:120]}')

print()

# ===================================================================
# STEP 5: PT Vale Indonesia — monitoring record + 2 contacts
# ===================================================================
print('=== STEP 5: PT Vale Indonesia (monitoring) ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'PT Vale Indonesia Tbk',
        'domain': 'vale.com',
        'industry': 'MINING_METALS',
        'phone': '+62 21 2793-9000',
        'address': 'Jakarta, Indonesia (HQ); Sorowako Block, South Sulawesi (main operation)',
        'city': 'Jakarta',
        'country': 'Indonesia',
        'website': 'https://vale.com/indonesia',
        'description': 'PT Vale Indonesia Tbk (IDX: INCO) — Indonesia\'s largest nickel producer. Ownership (post-July 2024): MIND ID 34%, Vale Canada ~44%, Sumitomo Metal Mining ~15%. Sorowako Block nickel matte operation (~72,000 MT/yr). NEW HPAL smelters: Pomalaa (120,000 MT MHP/yr, Q3 2026), Bahodopi (66,000 MT MHP/yr, Q4 2026), Sorowako (2027). Launched saprolite ore sales from Pomalaa + Bahodopi in 2025 (2.3M MT sold). MONITORING ONLY — Indonesian DMO + locked sales agreements (80% Vale Canada, 20% Sumitomo) make this account a non-target for ECONARES commodity sales.'
    }
})
print(f'  create PT Vale: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:120]}')
if sc in (200, 201):
    vale_id = r['id']
    sc2, r2 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Bernardus',
            'lastname': 'Irmanto',
            'jobtitle': 'President Director & CEO (since 2025)',
            'associatedcompanyid': vale_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'DECISION_MAKER',
            'source': 'Indonesia Miner Aug 2025 board announcement, GlobalData'
        }
    })
    print(f'  create Bernardus Irmanto: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:120]}')
    sc3, r3 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Ramliah',
            'lastname': 'Frenova',
            'jobtitle': 'General Manager Project Procurement (Bahodopi, Pomalaa, Sorowako Limonite, Tanamalia)',
            'associatedcompanyid': vale_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'INFLUENCER',
            'hs_linkedin_url': 'https://id.linkedin.com/in/ir-ramliah-frenova-s-t-m-t-96857510'
        }
    })
    print(f'  create Ramliah Frenova: {sc3} | {r3.get("id") if sc3 in (200,201) else r3.get("message","")[:120]}')

print()

# ===================================================================
# STEP 6: PT Gunbuster / Delong — KYC enrich 2 existing records
# ===================================================================
print('=== STEP 6: Delong records KYC enrichment ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/318104838865', {
    'properties': {
        'name': 'Jiangsu Delong Nickel Industry Co., Ltd.',
        'domain': 'delongnickel.com',
        'industry': 'MINING_METALS',
        'address': 'Jiangsu Province, China',
        'city': 'Jiangsu',
        'country': 'China',
        'website': 'http://www.delongnickel.com',
        'description': 'Jiangsu Delong Nickel Industry Co., Ltd. — Chinese parent company. Owner/developer of Delong Industrial Park in Morowali, Central Sulawesi, Indonesia (2,200 hectares; 3M MT ferronickel + 2.5M MT stainless steel capacity). Subsidiaries include PT Gunbuster Nickel Industry (GNI) + PT Karya Mineral Sejahtera (KMS).'
    }
})
print(f'  PATCH Delong China parent: {sc}')

sc2, r2 = http('PATCH', f'{BASE}/crm/v3/objects/companies/321962321599', {
    'properties': {
        'name': 'Delong Nickel Indonesia Operations',
        'domain': 'gunbusternickelindustry.com',
        'industry': 'MINING_METALS',
        'phone': '+62 408 21-000',
        'address': 'Stardust Estate Investment Industrial Park, Bunta/Bungintimbe/Tanauge Villages, Petasia District, North Morowali Regency, Central Sulawesi, Indonesia',
        'city': 'North Morowali',
        'country': 'Indonesia',
        'website': 'https://gunbusternickelindustry.com',
        'description': 'Delong Nickel Indonesia Operations — Indonesian subsidiary cluster (PT Gunbuster Nickel Industry + PT Karya Mineral Sejahtera). Integrated nickel smelter producing Nickel Pig Iron (NPI) for stainless steel. Exports primarily to China. Designated National Strategic Project (PSN). Workforce 5,001-10,000. NOTE: Labor violence history (Jan 2023) + CELIOS 2025 report flagged potential shutdown/transition to Danantara. Captive ore supply + captive CFPPs.'
    }
})
print(f'  PATCH Delong Indonesia Ops: {sc2}')

# Create 2 contacts under Indonesia Ops
sc3, r3 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
    'properties': {
        'firstname': 'Theo Arung',
        'lastname': 'Tangdilintin',
        'jobtitle': 'Purchasing Senior Staff (Apr 2022-present)',
        'associatedcompanyid': '321962321599',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://id.linkedin.com/in/theo-arung-tangdilintin-815062bb'
    }
})
print(f'  create Theo: {sc3}')

sc4, r4 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
    'properties': {
        'firstname': 'Dwi',
        'lastname': 'Riza',
        'jobtitle': 'Senior Purchasing Specialist (commodity/raw materials)',
        'associatedcompanyid': '321962321599',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'source': 'LinkedIn verified'
    }
})
print(f'  create Dwi: {sc4}')

print()

# ===================================================================
# FINAL READ-BACK SUMMARY
# ===================================================================
print('=== FINAL READ-BACK SUMMARY ===')
for label, oid, kind in [
    ('Concreat Holdings (renamed)', '320080163556', 'company'),
    ('APO Cement (enriched)', '321897429737', 'company'),
    ('Eagle Cement', '332029677563', 'company'),  # will look up below
    ('Northern Cement', '332029678000', 'company'),  # will look up below
    ('SteelAsia', '332029678500', 'company'),  # will look up below
    ('PT Vale Indonesia', '332029679000', 'company'),  # will look up below
]:
    pass  # placeholder

# Search to find newly created IDs
print('\n--- Verifying all 4 new Company records ---')
for kw in ['Eagle Cement','Northern Cement','SteelAsia','PT Vale Indonesia']:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'CONTAINS_TOKEN', 'value': kw}]}], 'properties': ['name','industry','phone','city','hs_target_account']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p = c['properties']
        print(f"  {p.get('name')} | ID:{c['id']} | industry:{p.get('industry')} | tier:{p.get('hs_target_account')} | city:{p.get('city')}")
PY