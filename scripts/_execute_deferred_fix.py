"""
Fix script — correct industry enum + drop invalid 'source' field.
Re-validate pre-flight first.
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

# === STEP 1 FIX: CEMEX → Concreat (industry = GLASS_CERAMICS_CONCRETE for cement) ===
print('=== STEP 1 FIX: Concreat Holdings rename ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/320080163556', {
    'properties': {
        'name': 'Concreat Holdings Philippines, Inc.',
        'domain': 'chp.com.ph',
        'industry': 'GLASS_CERAMICS_CONCRETE',
        'phone': '+63 2 8856-2888',
        'address': '29th Floor, Petron Mega Plaza, 358 Senator Gil Puyat Avenue, Makati City',
        'city': 'Makati City',
        'state': 'NCR',
        'country': 'Philippines',
        'hs_target_account': 'tier_1',
        'description': 'Concreat Holdings Philippines, Inc. (formerly CEMEX Holdings Philippines, Inc. / CHP). 51% owned by DMCI Holdings + Semirara Mining + Dacon = 89.86% controlling stake (acquisition closed Dec 2, 2024). Plants: APO Cement Corporation (Naga, Cebu) + Solid Cement Corporation (Antipolo, Rizal). Combined capacity 7.2M tons/yr. Brands: APO, Rizal, Island. Vertical coal integration via Semirara — primary opportunity is alternative fuels/biomass/RDF, not coal.'
    }
})
print(f'  PATCH Concreat: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

# APO Cement enrichment
sc2, r2 = http('PATCH', f'{BASE}/crm/v3/objects/companies/321897429737', {
    'properties': {
        'industry': 'GLASS_CERAMICS_CONCRETE',
        'hs_target_account': 'tier_1',
        'phone': '+63 32 489-9000',
        'city': 'Naga',
        'state': 'Cebu',
        'website': 'apocement.com.ph'
    }
})
print(f'  PATCH APO Cement: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:200]}')

print()

# === STEP 2 FIX: Eagle Cement (industry = GLASS_CERAMICS_CONCRETE) ===
print('=== STEP 2 FIX: Eagle Cement ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Eagle Cement Corporation',
        'domain': 'eaglecement.com.ph',
        'industry': 'GLASS_CERAMICS_CONCRETE',
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
print(f'  create Eagle Cement: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
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
    print(f'  create Jimeno: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:200]}')

print()

# === STEP 3 FIX: Northern Cement (industry = GLASS_CERAMICS_CONCRETE) ===
print('=== STEP 3 FIX: Northern Cement ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Northern Cement Corporation',
        'domain': 'ncc.com.ph',
        'industry': 'GLASS_CERAMICS_CONCRETE',
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
print(f'  create Northern Cement: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
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
            'hs_buying_role': 'DECISION_MAKER'
        }
    })
    print(f'  create Ramon Ang: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:200]}')
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
    print(f'  create Van Jayro Plata: {sc3} | {r3.get("id") if sc3 in (200,201) else r3.get("message","")[:200]}')

print()

# === STEP 4 FIX: SteelAsia (industry = BUILDING_MATERIALS for steel rebar) ===
print('=== STEP 4 FIX: SteelAsia ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'SteelAsia Manufacturing Corporation',
        'domain': 'steelasia.com',
        'industry': 'BUILDING_MATERIALS',
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
print(f'  create SteelAsia: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
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
            'hs_buying_role': 'DECISION_MAKER'
        }
    })
    print(f'  create Benjamin Yao: {sc2} | {r2.get("id") if sc2 in (200,201) else r2.get("message","")[:200]}')
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
    print(f'  create Ryan Hernandez: {sc3} | {r3.get("id") if sc3 in (200,201) else r3.get("message","")[:200]}')
    sc4, r4 = http('POST', f'{BASE}/crm/v3/objects/contacts', {
        'properties': {
            'firstname': 'Kathleen',
            'lastname': 'Mayhay-Mendoza',
            'jobtitle': 'Procurement Manager',
            'associatedcompanyid': steel_id,
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            'hs_buying_role': 'DECISION_MAKER'
        }
    })
    print(f'  create Kathleen Mendoza: {sc4} | {r4.get("id") if sc4 in (200,201) else r4.get("message","")[:200]}')

print()

# === STEP 5 FIX: PT Vale — Bernardus contact failed due to bad 'source' field; re-create without it ===
print('=== STEP 5 FIX: PT Vale Bernardus Irmanto ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/contacts', {
    'properties': {
        'firstname': 'Bernardus',
        'lastname': 'Irmanto',
        'jobtitle': 'President Director & CEO (since 2025)',
        'associatedcompanyid': '331684054763',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER'
    }
})
print(f'  create Bernardus: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()

# === STEP 6 FIX: Delong Dwi failed (likely also bad 'source' field) ===
print('=== STEP 6 FIX: Delong Dwi ===')
sc, r = http('POST', f'{BASE}/crm/v3/objects/contacts', {
    'properties': {
        'firstname': 'Dwi',
        'lastname': 'Riza',
        'jobtitle': 'Senior Purchasing Specialist (commodity/raw materials)',
        'associatedcompanyid': '321962321599',
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER'
    }
})
print(f'  create Dwi: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK SUMMARY ===')
for kw in ['Concreat','Eagle Cement','Northern Cement','SteelAsia','PT Vale','Delong']:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'CONTAINS_TOKEN', 'value': kw}]}], 'properties': ['name','industry','city','hs_target_account']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p = c['properties']
        print(f"  {p.get('name')} | ID:{c['id']} | industry:{p.get('industry')} | tier:{p.get('hs_target_account')} | city:{p.get('city')}")