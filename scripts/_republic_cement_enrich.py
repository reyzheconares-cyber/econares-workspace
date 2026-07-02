"""Republic Cement / Fortune Cement enrichment:
1. Enrich Republic Cement Company record (320106199766) — add Fortune Cement brand intel
2. Enrich Danao Plant record (319761962702)
3. Create contact: Republic Cement Sales/Procurement channel
4. Create notes: sales brief, contact form, brand note
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
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
RCBM_ID = '320106199766'
DANAO_ID = '319761962702'

# ═══════════════════════════════════════════════════════════════════
# STEP 1: Enrich Republic Cement Company record
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 1: Enrich Republic Cement Company record ===')
rcbm_desc = (
    'Republic Cement & Building Materials Inc. (RCBM) - Largest cement producer in the Philippines (9.7-10.8 MT/yr capacity). '
    'Founded 1955. Backed by CRH (Dublin, Ireland) + Aboitiz Equity Ventures. '
    'Brands: REPUBLIC, FORTUNE, RapidSET, Kapit-Balay, MINDANAO, wallMASTER. '
    'Fortune Cement Corporation is a BRAND under RCBM (originally founded 1967, merged into Republic). '
    'Fortune Cement manufactured at Norzagaray, Bulacan plant (original Fortune facility; upgraded from 2,500 to 3,200 t/day kiln; P700M investment for 1M MT/yr). '
    '5 integrated plants + 1 grinding station: Norzagaray (Bulacan), Teresa (Rizal), Taysan (Batangas), Danao (Cebu), Iligan (Lanao del Norte). '
    'HQ: 32nd Street, BGC, Taguig City. Tel: (+632) 8885 4599 / Sales: (+632) 8885 4596. '
    'ecoloop program: pioneered alternative fuel co-processing in PH (biomass, PKS, RDF). '
    'ECONARES angle: Indonesian thermal coal supply (NOT vertically integrated for coal, unlike Semirara-linked firms) + PKS/biomass for ecoloop alternative fuel program. '
    '7 strategically located plants = multiple delivery points. CRH + Aboitiz = stable, well-capitalized counterparty.'
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{RCBM_ID}', {
    'properties': {
        'industry': 'GLASS_CERAMICS_CONCRETE',
        'phone': '+63 2 8885 4599',
        'address': '32nd Street, Bonifacio Global City, Taguig City, 1632, Philippines',
        'city': 'Taguig City',
        'state': 'Metro Manila',
        'country': 'Philippines',
        'website': 'https://www.republiccement.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 1000,
        'description': rcbm_desc
    }
})
print(f'  PATCH Republic Cement: {sc}')

# Check for name auto-truncation
sc2, co = http('GET', f'{BASE}/crm/v3/objects/companies/{RCBM_ID}?properties=name')
if sc2 == 200:
    actual = co['properties'].get('name')
    if actual != 'Republic Cement':
        print(f'  Name changed to: {actual} (keeping as-is)')
    else:
        print(f'  Name confirmed: {actual}')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 2: Enrich Danao Plant record
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 2: Enrich Republic Cement Danao Plant record ===')
danao_desc = (
    'Republic Cement Danao Plant - Cebu plant of Republic Cement Group. '
    'Location: Barangay Dungo-an, Danao City, Cebu. '
    'Part of Republic Cement & Building Materials Inc. (CRH + Aboitiz). '
    'Brands produced: REPUBLIC, FORTUNE cement. '
    'ECONARES angle: Visayas delivery point for Indonesian coal/PKS. Close to Cebu port — good Indonesian logistics.'
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{DANAO_ID}', {
    'properties': {
        'industry': 'GLASS_CERAMICS_CONCRETE',
        'phone': '+63 2 8885 4599',
        'address': 'Barangay Dungo-an, Danao City, Cebu, Philippines',
        'city': 'Danao City',
        'state': 'Cebu',
        'country': 'Philippines',
        'website': 'https://www.republiccement.com',
        'hs_target_account': 'tier_2',
        'numberofemployees': 200,
        'description': danao_desc
    }
})
print(f'  PATCH Danao Plant: {sc}')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 3: Create contact — Republic Cement Sales/Procurement
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 3: Create contact ===')
contact_props = {
    'firstname': 'Republic Cement',
    'lastname': 'Sales & Procurement',
    'email': 'sales@republiccement.com',
    'jobtitle': 'Sales Inquiries & Product Concerns — Republic Cement & Building Materials Inc. (RCBM). Tel: (+632) 8885 4596. General: (+632) 8885 4599. Brands: REPUBLIC, FORTUNE, RapidSET, Kapit-Balay, MINDANAO, wallMASTER.',
    'associatedcompanyid': RCBM_ID,
    'hs_lead_status': 'NEW',
    'lifecyclestage': 'lead',
    'hs_buying_role': 'DECISION_MAKER',
    'hs_linkedin_url': 'https://www.linkedin.com/company/republiccement'
}
sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': contact_props})
print(f'  CREATE contact: {sc} | {ct.get("id") if sc in (200,201) else ct.get("message","")[:200]}')
CONTACT_ID = ct.get('id') if sc in (200, 201) else None

# Check for name auto-truncation
if CONTACT_ID:
    sc2, c2 = http('GET', f'{BASE}/crm/v3/objects/contacts/{CONTACT_ID}?properties=firstname,lastname')
    if sc2 == 200:
        fn = c2['properties'].get('firstname')
        ln = c2['properties'].get('lastname')
        print(f'  Contact name: {fn} {ln}')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 4: Create notes — sales brief, contact form, brand note
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 4: Create notes ===')

# Note 1: Sales & Strategic Brief
sales_note = (
    '<p><strong>CALL BRIEF — Republic Cement & Building Materials Inc. (RCBM)</strong></p>'
    '<p><strong>FORTUNE CEMENT IS A BRAND UNDER RCBM — not a standalone entity.</strong></p>'
    '<p><strong>BUYING SIGNALS:</strong></p><ul>'
    '<li>Largest cement producer in PH: 9.7-10.8 MT/yr capacity (5 plants + 1 grinding station)</li>'
    '<li>NOT vertically integrated for coal — no Semirara lock-in (unlike SMC-linked firms)</li>'
    '<li>ecoloop program: pioneered alternative fuel co-processing in PH (biomass, PKS, RDF)</li>'
    '<li>Fortune Cement brand at Norzagaray plant: P700M investment, upgrading to 1M MT/yr</li>'
    '<li>7 strategically located plants = multiple delivery points</li>'
    '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
    '<li>Ownership: CRH (Dublin, Ireland) + Aboitiz Equity Ventures</li>'
    '<li>CRH = global building materials giant; Aboitiz = top PH conglomerate</li>'
    '<li>Multinational = procurement may be centralized at group level</li>'
    '<li>ecoloop already established — may have existing alt fuel suppliers</li>'
    '<li>Brands: REPUBLIC, FORTUNE, RapidSET, Kapit-Balay, MINDANAO, wallMASTER</li>'
    '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
    '<li>Indonesian thermal coal: ★★★★ STRONG — no Semirara lock-in; largest PH cement producer</li>'
    '<li>Indonesian PKS/biomass: ★★★★★ PRIMARY — ecoloop alternative fuel program</li>'
    '<li>Coke breeze: ★★ Possible — cement kilns can accept coke</li>'
    '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
    '<li>Lead with Indonesian thermal coal + PKS/biomass for ecoloop program</li>'
    '<li>Access via sales channel: (+632) 8885 4596 or sales@republiccement.com</li>'
    '<li>LinkedIn: linkedin.com/company/republiccement</li>'
    '<li>Plant-level approach: Norzagaray (Fortune Cement), Teresa, Taysan, Danao, Iligan</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': sales_note, 'hs_timestamp': ts}
})
note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Sales brief note: {sc} | {note_id}')
if note_id:
    sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{RCBM_ID}/note_to_company', {})
    print(f'    assoc to RCBM: {sc2}')

# Note 2: Contact form
cf_body = '<p><strong>Online Contact Form:</strong> <a href="https://www.republiccement.com/contact">https://www.republiccement.com/contact</a></p><p><strong>Sales Inquiries:</strong> (+632) 8885 4596</p><p><strong>General Inquiries:</strong> (+632) 8885 4599</p><p><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/company/republiccement">linkedin.com/company/republiccement</a></p>'
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': cf_body, 'hs_timestamp': ts}
})
note_id2 = nr.get('id') if sc in (200, 201) else None
print(f'  Contact form note: {sc} | {note_id2}')
if note_id2:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id2}/associations/companies/{RCBM_ID}/note_to_company', {})

# Note 3: Fortune Cement brand note
brand_note = (
    '<p><strong>FORTUNE CEMENT — Brand Note (under Republic Cement Group)</strong></p>'
    '<ul>'
    '<li><strong>Legal entity:</strong> Fortune Cement Corporation is a BRAND under Republic Cement & Building Materials Inc. (RCBM). NOT a standalone entity.</li>'
    '<li><strong>History:</strong> Originally founded 1967 as Fortune Cement Corporation. Merged with Continental Operating Corp. and Premier Cement Corp. Later acquired by CRH + Aboitiz and rebranded as Republic Cement Group.</li>'
    '<li><strong>Manufactured at:</strong> Norzagaray, Bulacan plant (original Fortune Cement facility)</li>'
    '<li><strong>Capacity:</strong> Kiln upgraded from 2,500 to 3,200 t/day; P700M investment for 1M MT/yr; sales volume target: 30M bags/year (from 26M)</li>'
    '<li><strong>Cement type:</strong> OPC and Portland Pozzolan cement</li>'
    '<li><strong>Other RCBM brands:</strong> REPUBLIC, RapidSET, Kapit-Balay, MINDANAO, wallMASTER</li>'
    '<li><strong>ECONARES angle:</strong> Approach via Republic Cement channel. Norzagaray plant = major coal/PKS consumer. Indonesian thermal coal + PKS/biomass for ecoloop program.</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': brand_note, 'hs_timestamp': ts}
})
note_id3 = nr.get('id') if sc in (200, 201) else None
print(f'  Brand note: {sc} | {note_id3}')
if note_id3:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id3}/associations/companies/{RCBM_ID}/note_to_company', {})

# Note 4: Contact brief (if contact was created)
if CONTACT_ID:
    contact_note = (
        '<p><strong>CONTACT BRIEF — Republic Cement Sales & Procurement</strong></p>'
        '<ul>'
        '<li><strong>Channel:</strong> Republic Cement & Building Materials Inc. (RCBM) — official sales/procurement channel</li>'
        '<li><strong>Sales phone:</strong> (+632) 8885 4596</li>'
        '<li><strong>General phone:</strong> (+632) 8885 4599</li>'
        '<li><strong>Email:</strong> sales@republiccement.com (derived from website)</li>'
        '<li><strong>LinkedIn:</strong> linkedin.com/company/republiccement (705 associated members)</li>'
        '<li><strong>Website:</strong> republiccement.com/contact</li>'
        '<li><strong>Priority:</strong> PRIMARY — official channel for Republic Cement Group (including Fortune Cement brand)</li>'
        '<li><strong>Approach:</strong> Lead with Indonesian thermal coal + PKS/biomass for ecoloop alternative fuel program. Position as non-Semirara coal supplier (no vertical integration constraint).</li>'
        '<li><strong>Plants:</strong> Norzagaray (Bulacan) = Fortune Cement original; Teresa (Rizal); Taysan (Batangas); Danao (Cebu); Iligan (Lanao del Norte)</li>'
        '</ul>'
    )
    sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {'hs_note_body': contact_note, 'hs_timestamp': ts}
    })
    note_id4 = nr.get('id') if sc in (200, 201) else None
    print(f'  Contact brief note: {sc} | {note_id4}')
    if note_id4:
        http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id4}/associations/contacts/{CONTACT_ID}/note_to_contact', {})

print()

# ═══════════════════════════════════════════════════════════════════
# FINAL VERIFICATION
# ═══════════════════════════════════════════════════════════════════
print('=== FINAL VERIFICATION ===')
print()
print('--- Republic Cement ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{RCBM_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account,numberofemployees,description')
p = co.get('properties', {})
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account','numberofemployees']:
    print(f'  {k}: {p.get(k)}')
desc = p.get('description') or ''
print(f'  description: {len(desc)} chars')

print()
print('--- Danao Plant ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{DANAO_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
p = co.get('properties', {})
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
    print(f'  {k}: {p.get(k)}')

if CONTACT_ID:
    print()
    print('--- Contact ---')
    sc, c = http('GET', f'{BASE}/crm/v3/objects/contacts/{CONTACT_ID}?properties=firstname,lastname,email,jobtitle,hs_buying_role,hs_lead_status,hs_linkedin_url,associatedcompanyid')
    p = c.get('properties', {})
    for k in ['firstname','lastname','email','jobtitle','hs_buying_role','hs_lead_status','hs_linkedin_url','associatedcompanyid']:
        print(f'  {k}: {p.get(k)}')