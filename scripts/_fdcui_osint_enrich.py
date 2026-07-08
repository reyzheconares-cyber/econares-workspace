"""FDCUI Roderick Fernandez OSINT enrichment + new Sabrina Alegrado contact + deal notes."""
import json, urllib.request, datetime

ENV_PATH = r'C:\Users\reyma\.hermes\.env'
T = None
with open(ENV_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN='):
            T = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

BASE = 'https://api.hubapi.com'

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return resp.status, (json.loads(resp.read().decode()) if resp.length else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:300]

now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
today = datetime.date.today().isoformat()

RODERICK = '514137483968'
FDCUI_COMPANY = '329640754913'
DEAL_BASE = '331864002293'
DEAL_EXPANSION = '331885143770'

# === Step 1: Update Roderick's contact (enrich jobtitle + LinkedIn) ===
print('=== Step 1: Update Roderick contact ===')
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{RODERICK}', {
    'properties': {
        'jobtitle': 'Vice President, Project Development — FDC Utilities, Inc.; also President — FDC Renewables Energy Solutions (FDC RES). Historical Senior Manager handling Fuel Procurement Process for FDC Misamis (per ERC filings).',
        'hs_linkedin_url': 'https://www.linkedin.com/in/roderick-fernandez-1236b3143',
        'hs_buying_role': 'DECISION_MAKER'  # VP-level = decision maker
    }
})
print(f'  PATCH: HTTP {sc}')

# === Step 2: Create Sabrina Jeanne Alegrado contact ===
print()
print('=== Step 2: Create Sabrina Alegrado contact ===')
sabrina = {
    'properties': {
        'firstname': 'Sabrina Jeanne',
        'lastname': 'Alegrado',
        'email': 'sabrina.alegrado@fdcutilities.com',
        'jobtitle': 'Senior FDCUI contact (per ContactOut 2026-07-08). Potential secondary route into FDCUI organization since primary email to Roderick Fernandez (roderick.fernandez@fdcui.com.ph) is bouncing.',
        'hs_buying_role': 'INFLUENCER',
        'hs_lead_status': 'NEW',
        'associatedcompanyid': FDCUI_COMPANY
    }
}
sc, d = http('POST', f'{BASE}/crm/v3/objects/contacts', sabrina)
sabrina_id = None
if sc in (200, 201):
    sabrina_id = d.get('id') if isinstance(d, dict) else None
    print(f'  CREATE: HTTP {sc} | id={sabrina_id}')
else:
    print(f'  CREATE: HTTP {sc} | {d}')

# Restore truncated jobtitle for Sabrina
if sabrina_id:
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{sabrina_id}', {
        'properties': {
            'jobtitle': 'Senior FDCUI contact (per ContactOut 2026-07-08). Secondary route into FDCUI organization since primary email to Roderick Fernandez (roderick.fernandez@fdcui.com.ph) is bouncing due to fdcui.com.ph server timeouts.'
        }
    })
    print(f'  PATCH jobtitle (restored): HTTP {sc}')

# === Step 3: Add comprehensive OSINT note to Roderick ===
print()
print('=== Step 3: Add OSINT enrichment note to Roderick ===')
osint_note = (
    f'**OSINT ENRICHMENT - 2026-07-08**\n\n'
    f'Source: ECONARES OSINT report (verified 2026-07-08 via LinkedIn, ERC.gov.ph filings, Inquirer Business, fdcutilities.com, EMIS).\n\n'
    f'**Identity confirmed:**\n'
    f'- Full name: Roderick Z. Fernandez\n'
    f'- Current title: Vice President, Project Development - FDC Utilities, Inc.\n'
    f'- Also holds: President - FDC Renewables Energy Solutions (FDC RES)\n'
    f'- Tenure at FDCUI: April 2011 - Present (15+ years)\n'
    f'- Education: B.S. Electrical Engineering, Mapua Institute of Technology\n'
    f'- LinkedIn: https://www.linkedin.com/in/roderick-fernandez-1236b3143 (166 followers, 159 connections)\n\n'
    f'**Career progression (publicly documented):**\n'
    f'1. Senior Manager (2014) - filed judicial affidavits in ERC cases on behalf of FDC Misamis\n'
    f'2. VP for Business Development (2019) - signed power supply deal with HEAD International GmbH at PHIVIDEC\n'
    f'3. VP for Project Development (current, per fdcutilities.com/leadership page)\n'
    f'4. FDC RES President (2025-present) - led Filinvest renewable energy transition announcement Sep 2025\n\n'
    f'**Coal procurement relevance:**\n'
    f'- Roderick has DIRECT and DOCUMENTED involvement in fuel procurement at FDC Misamis\n'
    f'- ERC Case filings (2014) identify him as Senior Manager handling Fuel Procurement Process\n'
    f'- He submitted judicial affidavits specifically on the Fuel Procurement Process and EPPA provisions\n'
    f'- FDC Misamis operates 3 x 135 MW (405 MW total) CFB coal-fired thermal plant in PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental - one of the largest in Northern Mindanao\n'
    f'- CFB technology allows use of WIDER RANGE of coal types and alternative fuels (relevant for Indonesian thermal coal pitch)\n'
    f'- Coal plant expansion (405 MW to 6 x 135 MW = 810 MW) applied for, suggesting continued coal fuel demand\n\n'
    f'**Current strategic context:**\n'
    f'- As FDC RES President, Roderick is leading Filinvest renewable energy transition (first switch under expanded RAP, Sep 2025)\n'
    f'- Dual mandate: continue operating coal assets while transitioning some facilities to renewables\n'
    f'- Means: long-term coal fuel demand is sustained for existing assets; only some sites switch\n\n'
    f'**Reach challenges:**\n'
    f'- Email roderick.fernandez@fdcui.com.ph: DELIVERY-FAILED (server timeout at IP 45.79.222.138, bounced Jun29-Jul7 2026)\n'
    f'- Landline +63 2 8575 1600 (FDCUI Makati HQ): routes through an operator; Ms. Gled confirmed 2026-07-07 callback request\n'
    f'- Recommended path: landline asking for Mr. Fernandez directly, reference Jul 7 callback confirmed by Ms. Gled\n\n'
    f'**Alternate contacts (FDCUI):**\n'
    f'- Sabrina Jeanne Alegrado: sabrina.alegrado@fdcutilities.com (senior FDCUI contact, secondary route)\n'
    f'- FDCUI Corporate Comms: corpcomm@fdcutilities.com\n'
    f'- FDCUI DPO: dpo.fdcui@fdcutilities.com\n'
    f'- FDCUI HQ Makati: +63 2 8575 1600 / +63 2 8819 6131\n'
    f'- Plant address: PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental 9002\n'
    f'- Email format (inferred): firstname.lastname@fdcutilities.com OR @fdcui.com.ph\n\n'
    f'**Assessment:** Roderick Z. Fernandez is NOT just a procurement clerk - he is a VP-level executive with 15-year track record at FDCUI and direct historical involvement in fuel/coal procurement decision-making. Worth pursuing aggressively. The main challenge is the email domain deliverability issue; recommended path is the landline.\n\n'
    f'Source: ECONARES OSINT research 2026-07-08.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': osint_note},
    'associations': [{'to': {'id': RODERICK}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'  NOTE OSINT: HTTP {sc}')

# === Step 4: Update FDCUI company description with Roderick's VP context ===
print()
print('=== Step 4: Update FDCUI company description ===')
fdcui_desc = (
    'FDC Misamis Power Corporation (MPC) is the operating entity; FDC Utilities, Inc. (FDCUI) is the parent '
    '(part of Filinvest Development Corporation, Gotianun family conglomerate). '
    'Operates the Balingasag Power Station, a 165 MW coal-fired thermal power plant '
    '(3x55 MW units) in Mandangoa, Balingasag, Misamis Oriental (commissioned Sep 2017) -- NOTE: this is the ORIGINAL '
    'MPC plant. PRIMARY ENTITY for ECONARES is the FDC Misamis 3x135 MW (405 MW total) CFB plant in PHIVIDEC Industrial Estate, '
    'Villanueva, Misamis Oriental (commissioned Sep 2016). Expansion from 405 MW to 6x135 MW (810 MW total) applied for.\n\n'
    'KEY PROCUREMENT CONTACT: Roderick Z. Fernandez, VP Project Development (and President of FDC Renewables Energy Solutions). '
    'Historical Senior Manager handling Fuel Procurement Process for FDC Misamis (per ERC filings 2014-2019). 15+ years at FDCUI. '
    'Email roderick.fernandez@fdcui.com.ph - DELIVERY FAILED (server 45.79.222.138 timeout, Jun29-Jul7 2026). '
    'Landline +63 2 8575 1600 (FDCUI Makati HQ) routes through operator; Ms. Gled confirmed Jul 7 2026 callback request.\n\n'
    'Coal demand: 500k MT/yr (current 405 MW) growing to 1.5-2M MT/yr (post-expansion 810 MW). '
    '80% Indonesia / 20% local supply split. CFB technology allows wider coal type + alternative fuel range - good fit for Indonesian thermal coal.\n\n'
    'Dual mandate (Roderick as FDC RES President): continue operating coal assets while transitioning some Filinvest facilities to renewables (first switch under expanded RAP announced Sep 2025). Means long-term coal demand is sustained.\n\n'
    'Plant address: PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental 9002\n'
    'Email format: firstname.lastname@fdcutilities.com OR @fdcui.com.ph\n'
    'Alternate contacts: Sabrina Alegrado (sabrina.alegrado@fdcutilities.com); corpcomm@fdcutilities.com; dpo.fdcui@fdcutilities.com\n\n'
    'Source: ECONARES OSINT research 2026-07-08.'
)
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/companies/{FDCUI_COMPANY}', {
    'properties': {
        'description': fdcui_desc
    }
})
print(f'  PATCH FDCUI company: HTTP {sc}')

# === Step 5: Add strategic outreach note to BOTH FDC deals ===
print()
print('=== Step 5: Add strategic outreach note to FDC deals ===')
deal_note = (
    f'**STRATEGIC OUTREACH UPDATE - 2026-07-08 (from OSINT enrichment)**\n\n'
    f'KEY INSIGHT: Roderick Z. Fernandez is NOT just a procurement contact - he is a **VP-level executive** with 15-year '
    f'track record at FDCUI. Historical documentation (ERC filings 2014-2019) shows he personally handled the **Fuel Procurement Process** for FDC Misamis. '
    f'He also serves as **President of FDC Renewables Energy Solutions (FDC RES)** - dual mandate of continued coal operations + selective renewables transition. '
    f'Means: long-term coal fuel demand is sustained for existing assets.\n\n'
    f'COAL DEMAND:\n'
    f'- Current (this deal): 500k MT/yr, 3 x 135 MW (405 MW total) CFB plant, PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental\n'
    f'- Expansion (separate deal): 1.5-2M MT/yr, 6 x 135 MW (810 MW total) post-expansion\n'
    f'- Supply mix: 80% Indonesia / 20% local\n'
    f'- CFB technology allows wider coal type + alt-fuel range -- good fit for Indonesian thermal coal pitch\n\n'
    f'OUTREACH STATUS:\n'
    f'- Email roderick.fernandez@fdcui.com.ph: DELIVERY FAILED (server 45.79.222.138 timeout, Jun29-Jul7 2026)\n'
    f'- Phone: +63 2 8575 1600 (FDCUI Makati HQ landline) - routes through operator; Ms. Gled confirmed Jul 7 callback request\n'
    f'- DO NOT send further emails to fdcui.com.ph until server issue resolved\n\n'
    f'RECOMMENDED NEXT STEPS:\n'
    f'1. IMMEDIATE: Call +63 2 8575 1600 and ask for Mr. Roderick Fernandez directly (reference Jul 7 callback)\n'
    f'2. IF NO ANSWER: Try alternate contacts - Sabrina Alegrado (sabrina.alegrado@fdcutilities.com) or FDCUI corp comm (corpcomm@fdcutilities.com)\n'
    f'3. Once connected: pitch Indonesian thermal coal, FOB Philippines ports, focus on CFB-compatible grades\n'
    f'4. Volume: start with 50-100k MT/month trial, scale to 1.5-2M MT/yr at full expansion\n\n'
    f'Source: ECONARES OSINT 2026-07-08.'
)
for did, label in [(DEAL_BASE, 'FDC Misamis 500k MT/yr'), (DEAL_EXPANSION, 'FDC Misamis Expansion 1.5-2M MT/yr')]:
    sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {'hs_timestamp': now_iso, 'hs_note_body': deal_note},
        'associations': [{'to': {'id': did}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 214}]}]
    })
    print(f'  NOTE on {did} ({label}): HTTP {sc}')

# === Step 6: Verification ===
print()
print('=== Step 6: Final verification ===')
# Roderick state
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': RODERICK}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role','hs_linkedin_url','associatedcompanyid','hs_lead_status'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    print(f'  Roderick: {name} | email={p.get("email","")} | job={(p.get("jobtitle","") or "")[:80]}... | role={p.get("hs_buying_role","")} | linkedin={p.get("hs_linkedin_url","")}')

# Sabrina
if sabrina_id:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': sabrina_id}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role','associatedcompanyid','hs_lead_status'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    for c in d.get('results',[]):
        p = c['properties']
        name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
        print(f'  Sabrina: {name} | email={p.get("email","")} | job={(p.get("jobtitle","") or "")[:80]}... | role={p.get("hs_buying_role","")} | co={p.get("associatedcompanyid","")}')

print()
print('=== Done ===')