"""Nippon Steel record creation + KYC enrichment (monitoring only)."""
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

print('=== STEP 1: Create Nippon Steel record ===')
desc = (
    "Nippon Steel Corporation (日本製鉄株式会社, TSE: 5401) - WORLD'S 4TH-5TH LARGEST STEELMAKER (2025: 82M MT/yr crude steel capacity; Japan production 80M MT, overtaken by US in 2025). "
    "Founded 1950 (current form Apr 2019 merger of Nippon Steel + Sumitomo Metal). HQ Marunouchi, Chiyoda-ku, Tokyo, Japan. "
    "Chairman and CEO: Eiji Hashimoto (since Apr 2024, tenure 7.17 yrs, 'iron negotiator'). President and COO: Tadashi Imai. "
    "Strategic target: 100M MT/yr global capacity by mid-2030s (restoring position as world's #1 ex-China). 529 group companies (419 subsidiaries + 110 equity affiliates as of Mar 31, 2025). "
    "RECENT MAJOR ACQUISITION: U.S. Steel Corp ($15B closed Jun 2025, $11B investment pledge) + 'golden share' national security agreement with US govt. "
    "GLOBAL FOOTPRINT: AM/NS India (ArcelorMittal JV, Hazira plant expansion); G Steel + G J Steel (Thailand, 0.92M MT/yr); Sanyo Special Steel (India); Ovako (Sweden, EAF-based decarbonization); Krosaki Harima (acquired 2024). NO current PH/Indonesia steel operations. "
    "RAW MATERIAL PROCUREMENT (100% imported): Iron ore 60.5% Australia + 28.2% Brazil + 8.6% Canada. Coking coal 56.5% Australia + ~20% Indonesia + 9.7% Canada. "
    "PROCUREMENT STRATEGY: 'Procure and earn profit in raw materials business' (Integrated Report 2025). Actively hunting coking coal + iron ore mine stakes (Reuters Nov 2023). Vertical integration focus — buy stakes in mines vs. spot procurement. "
    "ECONARES ANGLE: ECONARES has Indonesian thermal coal supply capability + coking coal supply capability + direct mine access + existing stockpile in Kalimantan, Indonesia. "
    "RECOMMENDED APPROACH: Lead with Indonesian thermal coal + coking coal as non-Australian alternative (Nippon sources 20% from Indonesia; existing mine asset base creates openness). Target Raw Material Procurement division Tokyo HQ. Japanese keiretsu culture = 12-24 month sales cycle, formal Nihongo business practice. "
    "EXECUTION WINDOW: Management bandwidth absorbed by US Steel integration (2025-2026); entry window opens 2026 H2 once US Steel settles. "
    "RELATED ENTITIES IN HUBSPOT: JFE Steel (sister Japanese steelmaker, ID 329648274159 - different procurement org but similar profile). NO PH or Indonesia steel subsidiary found."
)
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Nippon Steel Corporation',
        'domain': 'nipponsteel.com',
        'industry': 'MINING_METALS',
        'phone': '+81 3 6867 4111',
        'address': '2-6-1 Marunouchi, Chiyoda-ku, Tokyo 100-0005, Japan (Nippon Steel Corporation Head Office)',
        'city': 'Tokyo',
        'country': 'Japan',
        'website': 'https://www.nipponsteel.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 110000,
        'description': desc
    }
})
print(f'  CREATE: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
COMPANY_ID = r.get('id') if sc in (200, 201) else None

# Check for name auto-truncation
if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{COMPANY_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'Nippon Steel Corporation':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            sc3, r3 = http('PATCH', f'{BASE}/crm/v3/objects/companies/{COMPANY_ID}', {'properties': {'name': 'Nippon Steel Corporation'}})
            print(f'  PATCH name: {sc3}')

print()

# === STEP 2: KYC enrichment ===
print('=== STEP 2: KYC enrich (adding detailed intel) ===')
enrichment_desc = (
    "Nippon Steel Corporation (TSE: 5401) - JAPANESE STEELMAKER, world's 4th-5th largest (82M MT/yr crude steel, 2025). "
    "HQ Tokyo, Japan. CEO: Eiji Hashimoto (since Apr 2024). President: Tadashi Imai. "
    "100% raw material imports: iron ore (60.5% Australia + 28.2% Brazil + 8.6% Canada); coking coal (56.5% Australia + ~20% Indonesia + 9.7% Canada + 5.1% USA). "
    "Procurement strategy: vertical integration, actively acquiring mine stakes. Actively hunting coking coal + iron ore assets. "
    "Global footprint: U.S. Steel ($15B acquisition Jun 2025), AM/NS India (ArcelorMittal JV), G Steel Thailand, Ovako Sweden. "
    "ECONARES HAS INDONESIAN THERMAL COAL SUPPLY + COKING COAL CAPABILITY + DIRECT MINE ACCESS + EXISTING STOCKPILE IN KALIMANTAN. "
    "OPPORTUNITY: Indonesian thermal coal + coking coal as non-Australian alternative (Nippon already sources 20% from Indonesia). "
    "EXECUTION WINDOW: Management bandwidth absorbed by US Steel integration (2025-2026); entry window opens 2026 H2. "
    "KEY CONTACTS: Shogo Fujii (General Manager, Alabama — US Steel integration role). Raw Material Procurement division (Tokyo HQ) = primary target. "
    "RELATED ENTITIES: JFE Steel (sister Japanese steelmaker, HubSpot ID 329648274159) — separate procurement org but similar sourcing needs."
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{COMPANY_ID}', {
    'properties': {
        'description': enrichment_desc
    }
})
print(f'  PATCH: {sc}')

print()

# === Engagement note ===
print('=== STEP 3: Engagement note ===')
import datetime
note_body = (
    "<p><strong>Nippon Steel CRM Buildout (2026-07-02):</strong></p>"
    f"<p>Created Nippon Steel Corporation record (ID <code>{COMPANY_ID}</code>) — monitoring tier_1 target. HQ Tokyo, CEO Eiji Hashimoto, President Tadashi Imai, 82M MT/yr capacity, world's 4th-5th largest steelmaker. Just acquired U.S. Steel ($15B Jun 2025).</p>"
    "<p><strong>KEY OPPORTUNITY:</strong> ECONARES HAS Indonesian thermal coal supply capability + coking coal capability + direct mine access + existing stockpile in Kalimantan, Indonesia. Nippon already sources ~20% of coking coal from Indonesia — strong fit for non-Australian alternative supply.</p>"
    "<p><strong>Raw material procurement profile:</strong> 100% imported. Iron ore 60.5% Australia + 28.2% Brazil. Coking coal 56.5% Australia + ~20% Indonesia + 9.7% Canada. Nippon actively hunting coking coal + iron ore mine stakes (vertical integration strategy).</p>"
    "<p><strong>EXECUTION WINDOW:</strong> Management bandwidth currently absorbed by US Steel integration (2025-2026). Recommended entry window: 2026 H2 once integration settles. Use this period for relationship-building via LinkedIn + email intro.</p>"
    "<p><strong>OUTREACH STRATEGY:</strong> Lead with Indonesian thermal coal + coking coal as non-Australian alternative. Target Raw Material Procurement division (Tokyo HQ). Japanese keiretsu culture = 12-24 month sales cycle, formal Nihongo business practice, English-language barrier expected.</p>"
    "<p><strong>RELATED ENTITIES:</strong> JFE Steel (sister Japanese steelmaker, HubSpot ID 329648274159) — separate procurement org but similar sourcing profile. Shogo Fujii (General Manager, Alabama, US Steel integration role, LinkedIn verified) — secondary contact.</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{COMPANY_ID}/note_to_company', {})
    print(f'  assoc to Nippon Steel: {sc2}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{COMPANY_ID}?properties=name,industry,phone,address,city,state,country,website,hs_target_account,numberofemployees')
p = co['properties']
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account','numberofemployees']:
    print(f'  {k}: {p.get(k)}')
print()
print(f'  description length: {len(p.get("description") or "")} chars')
print(f'  description preview: {(p.get("description") or "")[:200]}...')
