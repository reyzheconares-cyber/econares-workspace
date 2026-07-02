"""Rose Calba / PCPC / Solaris enrichment:
1. Update Rose Calba contact — fix status, add verification note
2. Enrich Solaris company record — tier, industry, description
3. Enrich PCPC contacts — add notes, fix statuses
4. Create engagement notes for all
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

# ═══════════════════════════════════════════════════════════════════
# STEP 1: Update Rose Calba contact
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 1: Update Rose Calba contact ===')
ROSE_ID = '481007634163'
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{ROSE_ID}', {
    'properties': {
        'hs_buying_role': 'INFLUENCER',
        'hs_lead_status': 'OPEN',
        'lifecyclestage': 'lead',
        'jobtitle': 'Procurement Officer, Solaris Inc. (Jin Navitas group — sister company of PCPC). NOT a PCPC employee. Solaris handles solar/renewable projects; PCPC handles coal power.',
    }
})
print(f'  PATCH Rose Calba: {sc}')

# Add verification/analysis note
rose_note = (
    '<p><strong>ROSE CALBA — Contact Analysis (2026-07-02)</strong></p>'
    '<p><strong>Status:</strong> VERIFIED contact at Solaris Inc. (NOT PCPC)</p>'
    '<ul>'
    '<li><strong>Company:</strong> Solaris Inc. (solaris.com.ph) — Jin Navitas Resource Inc. group</li>'
    '<li><strong>Role:</strong> Procurement Officer at Solaris</li>'
    '<li><strong>Email:</strong> rcalba@solaris.com.ph — derived from phone call to +632 8584 6706 (A Brown Co. office / Solaris-JNCC)</li>'
    '<li><strong>LinkedIn:</strong> NOT FOUND in any public directory (LinkedIn, Solaris website, Facebook, RocketReach)</li>'
    '<li><strong>Email verification:</strong> MAY BE OUTDATED OR INCORRECT — not found in any public search. Recommend phone verification before outreach.</li>'
    '<li><strong>Relationship to PCPC:</strong> Sister company under Jin Navitas group. Solaris handles solar/renewable projects; PCPC handles coal power. NOT a direct PCPC procurement contact.</li>'
    '</ul>'
    '<p><strong>OUTREACH ACTIVITY:</strong> ZERO — no emails, calls, or meetings recorded. 3 empty tasks (May 4, 8, 12 2026) — likely automated.</p>'
    '<p><strong>RECOMMENDATION:</strong></p>'
    '<ul>'
    '<li>Phone-verify email before outreach: +632 8584 6706</li>'
    '<li>If verified: use for Solaris renewable project logistics/supply angle (NOT coal)</li>'
    '<li>For PCPC coal: use Liza Sigua (Purchasing Manager) or Pia Alipio (Supply Chain Head) — both IN_PROGRESS</li>'
    '<li>Rose is YELLOW priority — solar project logistics only</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': rose_note, 'hs_timestamp': ts}
})
note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Rose analysis note: {sc} | {note_id}')
if note_id:
    sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/contacts/{ROSE_ID}/note_to_contact', {})
    print(f'    assoc to contact: {sc2}')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 2: Enrich Solaris company record
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 2: Enrich Solaris company record ===')
SOLARIS_ID = '321452895955'
solaris_desc = (
    'Solaris Inc. (Jin Navitas Solaris) — Solar/renewable energy subsidiary of Jin Navitas Resource Inc. (JNRI). '
    'Part of the Jin Navitas group alongside PCPC (coal power) and JNEC (retail electricity). '
    'Key project: 62 MWp Ajuy-1 solar project in Iloilo (PHP 2.37B, EPC: China Energy Engineering Group NEPC). '
    'Target completion: End 2025 / Early 2026. '
    'Also: Ning*Ning rooftop solar (Naic, Cavite). '
    'Leadership: Jacinto Ray D. Ng III (AVP Business Development, also at PCPC). '
    'Rose Calba (Procurement Officer) — contact obtained via phone call to A Brown Co. office. '
    'ECONARES angle: Solaris handles solar/renewable — NOT coal. Low priority for ECONARES commodity supply. '
    'Post-construction O&M may need diesel for backup generators — minor opportunity.'
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{SOLARIS_ID}', {
    'properties': {
        'industry': 'RENEWABLES_ENVIRONMENT',
        'phone': '+632 8584 6706',
        'city': 'Manila',
        'country': 'Philippines',
        'website': 'https://www.solaris.com.ph',
        'hs_target_account': 'tier_3',
        'numberofemployees': 50,
        'description': solaris_desc
    }
})
print(f'  PATCH Solaris: {sc}')

# Verify
sc2, co = http('GET', f'{BASE}/crm/v3/objects/companies/{SOLARIS_ID}?properties=name,industry,phone,city,country,website,hs_target_account,numberofemployees,description')
if sc2 == 200:
    p = co['properties']
    print(f'  name: {p.get("name")}')
    print(f'  industry: {p.get("industry")}')
    print(f'  tier: {p.get("hs_target_account")}')
    print(f'  desc: {len(p.get("description") or "")} chars')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 3: Enrich PCPC contacts
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 3: Enrich PCPC contacts ===')

# Fix Alfie Miras — he's now CEO of Solaris, not PCPC
miras_note = (
    '<p><strong>CONTACT BRIEF — Jose Alfonso C. Miras (Alfie)</strong></p>'
    '<ul>'
    '<li><strong>Current Role:</strong> President & CEO, PCPC AND Jin Navitas Electric Corp (JNEC)</li>'
    '<li><strong>Previous:</strong> VP, Business Development & Market Operations at PCPC</li>'
    '<li><strong>Promoted:</strong> ~June 2025 after Nicandro Fucoy departed</li>'
    '<li><strong>Email:</strong> amiras@pcpc.ph (likely — PCPC uses [first_initial][lastname]@pcpc.ph format)</li>'
    '<li><strong>Also:</strong> President & CEO of Solaris (sister company)</li>'
    '<li><strong>Priority:</strong> RED — CEO-level; referral preferred via Nicandro Fucoy</li>'
    '<li><strong>Approach:</strong> Use for strategic/BD discussions; coal procurement via Liza Sigua</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': miras_note, 'hs_timestamp': ts}
})
miras_note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Miras note: {sc} | {miras_note_id}')
if miras_note_id:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{miras_note_id}/associations/contacts/481000577735/note_to_contact', {})

# Fix Liza Sigua — she's the PRIMARY coal buyer
sigua_note = (
    '<p><strong>CONTACT BRIEF — Liza Sigua</strong></p>'
    '<ul>'
    '<li><strong>Role:</strong> Manager, Purchasing, PCPC</li>'
    '<li><strong>Email:</strong> lsigua@pcpc.ph (derived from confirmed PCPC email format)</li>'
    '<li><strong>ZoomInfo:</strong> Still with PCPC as Purchasing Manager (updated April 2025)</li>'
    '<li><strong>Priority:</strong> RED — PRIMARY coal buyer/procurement head at PCPC for Unit 1 operations</li>'
    '<li><strong>Approach:</strong> Direct outreach with coal spec sheet and FOB Indonesian origin pricing. Phone preferred.</li>'
    '<li><strong>Status:</strong> IN_PROGRESS — active outreach</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': sigua_note, 'hs_timestamp': ts}
})
sigua_note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Sigua note: {sc} | {sigua_note_id}')
if sigua_note_id:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{sigua_note_id}/associations/contacts/481005002437/note_to_contact', {})

# Fix Pia Alipio — Supply Chain Head
alipio_note = (
    '<p><strong>CONTACT BRIEF — Pia Alipio (Ma. Paz Dolores M. Alipio)</strong></p>'
    '<ul>'
    '<li><strong>Role:</strong> AVP Supply Chain / Supply Chain Head, PCPC</li>'
    '<li><strong>Email:</strong> p.alipio@pcpc.ph</li>'
    '<li><strong>Priority:</strong> RED — alternate coal procurement contact</li>'
    '<li><strong>Approach:</strong> Use as backup if Liza Sigua unresponsive; same coal angle</li>'
    '<li><strong>Status:</strong> IN_PROGRESS — active outreach</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': alipio_note, 'hs_timestamp': ts}
})
alipio_note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Alipio note: {sc} | {alipio_note_id}')
if alipio_note_id:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{alipio_note_id}/associations/contacts/483002066641/note_to_contact', {})

# Fix PCPC Corporate Communications
corpcomms_note = (
    '<p><strong>CONTACT BRIEF — PCPC Corporate Communications</strong></p>'
    '<ul>'
    '<li><strong>Email:</strong> corpcomms@pcpc.ph</li>'
    '<li><strong>Status:</strong> BOUNCED — email not deliverable</li>'
    '<li><strong>Priority:</strong> LOW — general inquiries only; not procurement</li>'
    '<li><strong>Recommendation:</strong> Do not use for outreach. Use Liza Sigua or Pia Alipio instead.</li>'
    '</ul>'
)
sc, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': corpcomms_note, 'hs_timestamp': ts}
})
corpcomms_note_id = nr.get('id') if sc in (200, 201) else None
print(f'  Corpcomms note: {sc} | {corpcomms_note_id}')
if corpcomms_note_id:
    http('PUT', f'{BASE}/crm/v3/objects/notes/{corpcomms_note_id}/associations/contacts/485891997387/note_to_contact', {})

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 4: Enrich PCPC company record
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 4: Enrich PCPC company record ===')
PCPC_ID = '322716960491'
pcpc_desc = (
    'Palm Concepcion Power Corporation (PCPC) — 135 MW CFBC coal-fired power plant in Concepcion, Iloilo, Philippines. '
    'Unit 1: Operating since 2016. Unit 2: Pre-construction, COD pushed to June 2028. '
    'ACQUIRED July 14, 2025 by ACEN Corporation (Aboitiz Group) + Jin Navitas Resource Inc. (JNRI). '
    'Previous structure: PTCHC (A Brown) 39.54% + JNRI 30% + Oriental Knight Ltd. '
    'Part of Jin Navitas group: PCPC (coal) + JNEC (retail electricity) + Solaris (solar/renewables). '
    'Key contacts: Liza Sigua (Purchasing Manager, PRIMARY coal buyer), Pia Alipio (AVP Supply Chain), Jose Alfonso C. Miras (President & CEO). '
    'Email format: [first_initial][lastname]@pcpc.ph. '
    'Bounced emails: purchasing@pcpc.ph, corpcomms@pcpc.ph. '
    'ECONARES angle: Unit 1 operating — regular coal buyer. FOB or CIF Concepcion, Iloilo. CFBC grade — flexible, accepts higher-ash coal (up to 18-20%).'
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{PCPC_ID}', {
    'properties': {
        'industry': 'UTILITIES',
        'phone': '+63 33 523 8888',
        'address': 'Concepcion, Iloilo, Philippines',
        'city': 'Concepcion',
        'state': 'Iloilo',
        'country': 'Philippines',
        'website': 'https://www.pcpc.ph',
        'hs_target_account': 'tier_1',
        'numberofemployees': 100,
        'description': pcpc_desc
    }
})
print(f'  PATCH PCPC: {sc}')

# Verify
sc2, co = http('GET', f'{BASE}/crm/v3/objects/companies/{PCPC_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account,numberofemployees,description')
if sc2 == 200:
    p = co['properties']
    print(f'  name: {p.get("name")}')
    print(f'  industry: {p.get("industry")}')
    print(f'  tier: {p.get("hs_target_account")}')
    print(f'  desc: {len(p.get("description") or "")} chars')

print()

# ═══════════════════════════════════════════════════════════════════
# STEP 5: Final verification
# ═══════════════════════════════════════════════════════════════════
print('=== STEP 5: Final verification ===')
print()
print('--- Rose Calba ---')
sc, c = http('GET', f'{BASE}/crm/v3/objects/contacts/{ROSE_ID}?properties=firstname,lastname,email,jobtitle,hs_buying_role,hs_lead_status,lifecyclestage,associatedcompanyid')
p = c.get('properties', {})
print(f'  name: {p.get("firstname")} {p.get("lastname")}')
print(f'  email: {p.get("email")}')
print(f'  jobtitle: {p.get("jobtitle")}')
print(f'  buying_role: {p.get("hs_buying_role")}')
print(f'  lead_status: {p.get("hs_lead_status")}')
print(f'  lifecycle: {p.get("lifecyclestage")}')
print(f'  company: {p.get("associatedcompanyid")}')

print()
print('--- Solaris ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{SOLARIS_ID}?properties=name,industry,hs_target_account,city,country')
p = co.get('properties', {})
print(f'  name: {p.get("name")}')
print(f'  industry: {p.get("industry")}')
print(f'  tier: {p.get("hs_target_account")}')

print()
print('--- PCPC ---')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{PCPC_ID}?properties=name,industry,hs_target_account,city,state,country')
p = co.get('properties', {})
print(f'  name: {p.get("name")}')
print(f'  industry: {p.get("industry")}')
print(f'  tier: {p.get("hs_target_account")}')
print(f'  location: {p.get("city")}, {p.get("state")}, {p.get("country")}')

print()
print('--- PCPC Contacts ---')
for cid in ['481000577735', '481005002437', '483002066641', '485891997387']:
    sc, c = http('GET', f'{BASE}/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,jobtitle,hs_lead_status,lifecyclestage')
    p = c.get('properties', {})
    print(f'  {cid}: {p.get("firstname")} {p.get("lastname")} | {p.get("email")} | {p.get("jobtitle")} | status:{p.get("hs_lead_status")} | stage:{p.get("lifecyclestage")}')