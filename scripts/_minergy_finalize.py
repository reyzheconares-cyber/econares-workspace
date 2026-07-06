"""Finalize Minergy cleanup: fix stale jobtitle + enrich company description."""
import json, urllib.request, datetime

ENV = r'C:\Users\reyma\.hermes\.env'
with open(ENV, 'r', encoding='utf-8') as f:
    T = None
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

# === Step 1: Fix stale jobtitle on contact 478913617612 ===
print('=== Step 1: Fix contact jobtitle ===')
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/478913617612', {
    'properties': {
        'jobtitle': 'Coal Procurement Contact (shared procurement inbox for Balingasag Power Station)'
    }
})
print(f'PATCH jobtitle: HTTP {sc}')

# Add a note documenting the title fix
note_body = (
    f'**JOBTITLE UPDATED - {today}**\n\n'
    f'Previous title: "Coal Procurement - Minergy Coal Corp" (referenced deleted entity 320523465441).\n'
    f'New title: "Coal Procurement Contact (shared procurement inbox for Balingasag Power Station)" '
    f'(references real company 320527602408, Minergy Power Corporation - Balingasag Power Station).\n\n'
    f'Email info@minergypower.com.ph is the official Balingasag Power Station procurement shared inbox.\n'
    f'Use this contact for all ECONARES Indonesian thermal coal outreach to Minergy.\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_body},
    'associations': [{'to': {'id': '478913617612'}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE title update: HTTP {sc}')

# === Step 2: Enrich company 320527602408 description with corporate structure ===
print()
print('=== Step 2: Enrich Balingasag Power Station description ===')
new_desc = (
    'Balingasag Power Station Overview\n\n'
    'Minergy Power Corporation (MPC) operates the Balingasag Power Station, a 165 MW coal-fired thermal power plant '
    '(3x55 MW units) located in Mandangoa, Balingasag, Misamis Oriental in Northern Mindanao. The plant was '
    'commissioned in September 2017 by Minergy Coal Corporation, a subsidiary of Cagayan Electric Power & Light Co '
    '(CEPALCO). The facility has its own coal jetty with two coal unloaders and a 138kV substation.\n\n'
    'Corporate Structure (verified 2026-07-06):\n'
    '- Parent: Cagayan Electric Power & Light Co (CEPALCO)\n'
    '- Grand-parent: Mindanao Energy Systems Inc (MINERGY - the parent company)\n'
    '- Sister entity: MINERGY (322943715053, Cagayan de Oro) - renewable energy (solar, clean power); SEPARATE COMPANY\n'
    '- MPC: 40% owned by Vivant Integrated Generation Corp (VIGC), a wholly-owned subsidiary of Vivant Energy Corp, '
    'which is 100% owned by publicly-listed Vivant Corporation.\n'
    '- Power off-taker: CEPALCO franchise territory (150 MW net capacity)\n\n'
    'EPC contractors: Mitsubishi Corporation (Japan) main EPC; Toshiba (Power Block); DOHWA (balance plant, Korea). '
    'Equipment: GE steam turbine generator sets + Foster Wheeler boilers.\n\n'
    'Commodity Requirements for ECONARES\n'
    'Coal Specifications: CFB spec; estimated annual volume 165 MW x 0.45 capacity factor x 8,000 hrs x ~0.5 kg/kWh = ~300,000 MT/year.\n'
    'Coal grade: NAR 4,200-6,200 GAR, low-to-mid ash, low sulfur preferred. '
    'Fuel switching / alternative fuels (PKS, biomass) possible for sustainability mandates.\n\n'
    'Procurement contact: info@minergypower.com.ph (shared procurement inbox).'
)
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/companies/320527602408', {
    'properties': {
        'description': new_desc
    }
})
print(f'PATCH company description: HTTP {sc}')

# === Step 3: Final verification ===
print()
print('=== Step 3: Final Minergy state ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'CONTAINS_TOKEN', 'value': 'Minergy'}]}], 'properties': ['name','industry','city','country','domain','num_associated_contacts','hs_object_id'], 'limit': 20}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Minergy companies remaining: {d.get("total",0)} (search may double-count)')
for c in d.get('results',[]):
    p = c['properties']
    print(f'  {c["id"]}: {p.get("name","")} | industry={p.get("industry","")} | domain={p.get("domain","")} | contacts={p.get("num_associated_contacts","")}')

# Exact-match search to be sure
print()
print('=== Exact-match search (name CONTAINS Minergy + name <> repeat) ===')
for q in ['Minergy Power', 'Minergy Coal', 'MINERGY']:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'EQ', 'value': q}]}], 'properties': ['name','hs_object_id','num_associated_contacts'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    if d.get('total',0) > 0:
        for c in d.get('results',[]):
            p = c['properties']
            print(f'  {c["id"]}: {p.get("name","")} | contacts={p.get("num_associated_contacts","")}')
    else:
        print(f'  "{q}": 0 records')

print()
print('=== Done ===')