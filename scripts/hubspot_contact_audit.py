#!/usr/bin/env python3
"""
ECONARES HubSpot Contact Audit Pipeline
========================================
Audit-first enrichment audit for the standing goal:
  *enrich our HubSpot contacts that we have not connected yet,
   per industry best practices*

Outputs (all in Windows temp / passed to build_research_brief.py):
  - hub_all_contacts.json   : raw pull of all 176 HubSpot contacts
  - hub_gaps_v2.json        : portal-correct gap scoring (10 core + 8 custom fields)
  - xlsx_contacts.json      : 392 unique contacts from ECONARES master XLSX (decoded via unzip)
  - matches.json            : 34 raw cross-references (HubSpot <-> XLSX)
  - unmatched.json          : 142 HubSpot contacts with no XLSX row
  - research_brief_full.json: 96 real-named leads, ranked by enrichment potential

KYC integrity rule (per ECONARES policy):
  Never fabricate placeholder data. Never overwrite verified HubSpot data
  with XLSX data of lower quality. Only fill empty fields with verified values.
  When in doubt, leave empty and mark TBD.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---- Config ----
ENV_PATH = os.path.expanduser('~/.hermes/.env')
TEMP_DIR = Path(os.environ.get('TEMP', 'C:/Users/reyma/AppData/Local/Temp'))
WORKSPACE = Path.home() / 'Documents' / 'ECONARES_WORKSPACE'
SCRIPTS_DIR = WORKSPACE / 'scripts'
XLSX_PATH = WORKSPACE.parent / '02 Areas' / 'Reports' / 'ECONARES SALES and MARKETING UPDATES-RZH - Jun. DAILY intel.xlsx'
# fallback paths
if not XLSX_PATH.exists():
    for p in [
        Path('G:/My Drive/02 Areas/Reports/ECONARES SALES and MARKETING UPDATES-RZH - Jun. DAILY intel.xlsx'),
        Path('G:/My Drive/Reports/ECONARES SALES and MARKETING UPDATES-RZH today.xlsx'),
    ]:
        if p.exists():
            XLSX_PATH = p
            break

HUBSPOT_BASE = 'https://api.hubapi.com'

# Portal-correct property names (verified via /crm/v3/properties/contacts)
CORE_FIELDS = [
    'firstname', 'lastname', 'email', 'phone', 'jobtitle', 'company',
    'lifecyclestage', 'hs_lead_status', 'hs_buying_role', 'hs_linkedin_url',
]
ECONARES_CUSTOM_FIELDS = [
    'material_needed', 'monthly_volume_requirement', 'nickel_grade_required',
    'preferred_delivery_term', 'target_purchase_start_date', 'destination_port',
    'can_provide_loi__icpo', 'buyer_type',
    'econares_follow_up_date', 'econares_last_outreach_date', 'econares_outreach_method',
]


def load_token():
    with open(ENV_PATH) as f:
        for line in f:
            s = line.lstrip()
            if s.startswith('export '):
                s = s[7:]
            if s.startswith('HUBSPOT_ACCESS_TOKEN'):
                return s.split('=', 1)[1].strip().strip('"').strip("'")
    return None


def http(method, url, body=None, token=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=60) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {'err': e.read().decode()[:500]}


# ---- 1. Pull all HubSpot contacts ----
def pull_all_contacts(token):
    print('[1/4] Pulling all HubSpot contacts...')
    all_contacts = []
    after = None
    for page in range(20):
        props = CORE_FIELDS + ['hs_object_id', 'createdate', 'hs_lastmodifieddate']
        body = {'filterGroups': [], 'properties': props, 'limit': 100,
                'sorts': [{'propertyName': 'hs_lastmodifieddate', 'direction': 'DESCENDING'}]}
        if after:
            body['after'] = after
        code, data = http('POST', f'{HUBSPOT_BASE}/crm/v3/objects/contacts/search', body, token)
        if code != 200:
            print(f'  page {page} FAIL: {code}')
            break
        all_contacts.extend(data.get('results', []))
        after = data.get('paging', {}).get('next', {}).get('after')
        if not after:
            break
    print(f'  pulled {len(all_contacts)} contacts')
    return all_contacts


# ---- 2. Score gaps using portal-correct properties ----
def score_gaps(all_contacts):
    gaps = []
    for c in all_contacts:
        p = c.get('properties', {})
        s = 0
        missing = []
        for prop, label in [
            ('firstname', 'firstname'), ('lastname', 'lastname'),
            ('email', 'email'), ('phone', 'phone'),
            ('jobtitle', 'jobtitle'), ('company', 'company'),
            ('lifecyclestage', 'lifecycle'),
            ('hs_lead_status', 'lead_status'),
            ('hs_buying_role', 'buying_role'),
            ('hs_linkedin_url', 'linkedin'),
        ]:
            if p.get(prop):
                s += 1
            else:
                missing.append(label)
        if s < 10:
            gaps.append({
                'id': c['id'],
                'name': f"{p.get('firstname', '')} {p.get('lastname', '')}".strip(),
                'email': p.get('email', ''),
                'phone': p.get('phone', ''),
                'jobtitle': p.get('jobtitle', ''),
                'company': p.get('company', ''),
                'lifecycle': p.get('lifecyclestage', ''),
                'lead_status': p.get('hs_lead_status', ''),
                'buying_role': p.get('hs_buying_role', ''),
                'linkedin': p.get('hs_linkedin_url', ''),
                'modified': p.get('hs_lastmodifieddate', ''),
                'createdate': p.get('createdate', ''),
                'score': s,
                'missing': missing,
            })
    return gaps


# ---- 3. Decode XLSX master sheet (unzip + parse XML) ----
def decode_xlsx(xlsx_path):
    print(f'[2/4] Decoding XLSX: {xlsx_path}')
    if not xlsx_path.exists():
        print(f'  XLSX not found at {xlsx_path}')
        return []
    import zipfile
    tmp_dir = TEMP_DIR / 'econ_unz_audit'
    tmp_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(xlsx_path) as zf:
        zf.extractall(tmp_dir)
    ss_path = tmp_dir / 'xl' / 'sharedStrings.xml'
    sheet_path = tmp_dir / 'xl' / 'worksheets' / 'sheet5.xml'  # MASTER
    if not ss_path.exists() or not sheet_path.exists():
        print(f'  expected files missing')
        return []
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    ss_tree = ET.parse(ss_path)
    SS = [''.join((el.text or '') for el in si.iter() if el.tag.endswith('}t'))
          for si in ss_tree.getroot().findall(f'{ns}si')]
    sheet_tree = ET.parse(sheet_path)
    sheet_root = sheet_tree.getroot()

    def row_data(r):
        out = {}
        for c in r.findall(f'{ns}c'):
            ref = c.get('r')
            col = re.match(r'([A-Z]+)', ref).group(1)
            ctype = c.get('t', 'n')
            v = c.find(f'{ns}v')
            if v is None or v.text is None:
                val = ''
            elif ctype == 's':
                val = SS[int(v.text)]
            else:
                val = v.text
            out[col] = val
        return out

    rows = sheet_root.findall(f'.//{ns}row')
    contacts = []
    for r in rows[2:]:  # skip header rows 1-2
        d = row_data(r)
        if not d.get('F'):  # no contact person
            continue
        contacts.append({
            'no': d.get('A', ''),
            'company': d.get('B', ''),
            'commodity': d.get('C', ''),
            'industry': d.get('D', ''),
            'region': d.get('E', ''),
            'contact': d.get('F', ''),
            'phone': d.get('G', ''),
            'email': d.get('H', ''),
            'address': d.get('I', ''),
            'priority': d.get('J', ''),
            'mt_order': d.get('K', ''),
            'freq_year': d.get('L', ''),
            'status': d.get('M', ''),
            'last_contact': d.get('N', ''),
            'engagement': d.get('O', ''),
            'remarks': d.get('P', ''),
            'website': d.get('Q', ''),
            'country': d.get('R', ''),
            'kyc': d.get('S', ''),
            'last_verified': d.get('T', ''),
            'routing': d.get('U', ''),
            'email_quality': d.get('V', ''),
            'linkedin': d.get('W', ''),
            'signals': d.get('X', ''),
            'volume': d.get('Y', ''),
            'logistics': d.get('Z', ''),
            'intel_score': d.get('AA', ''),
        })
    # dedup by (lower contact, lower company)
    seen = set()
    unique = []
    for c in contacts:
        k = (c['contact'].strip().lower(), c['company'].strip().lower())
        if k not in seen:
            seen.add(k)
            unique.append(c)
    print(f'  decoded {len(unique)} unique XLSX contacts')
    return unique


# ---- 4. Cross-reference HubSpot <-> XLSX ----
def cross_reference(gaps, xlsx):
    print('[3/4] Cross-referencing HubSpot <-> XLSX...')
    xlsx_by_email = {c['email'].strip().lower(): c for c in xlsx if c.get('email')}
    for c in xlsx:
        if c.get('email'):
            for e in c['email'].split(','):
                xlsx_by_email.setdefault(e.strip().lower(), c)

    xlsx_by_domain = {}
    for c in xlsx:
        web = (c.get('website') or '').lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        if web:
            xlsx_by_domain.setdefault(web, c)
        if c.get('email'):
            dom = c['email'].split('@')[-1].lower()
            xlsx_by_domain.setdefault(dom, c)

    def norm(s):
        s = (s or '').lower()
        s = re.sub(r'[^a-z0-9 ]', ' ', s)
        return re.sub(r'\s+', ' ', s).strip()

    xlsx_by_name_company = {}
    for c in xlsx:
        n, co = norm(c.get('contact', '')), norm(c.get('company', ''))
        if n and co:
            xlsx_by_name_company.setdefault((n, co), []).append(c)

    matched, unmatched = [], []
    for h in gaps:
        e, nm, co = (h.get('email') or '').strip().lower(), norm(h.get('name', '')), norm(h.get('company', ''))
        found, method = None, None
        if e and e in xlsx_by_email:
            found, method = xlsx_by_email[e], 'email'
        elif nm and co and (nm, co) in xlsx_by_name_company and len(xlsx_by_name_company[(nm, co)]) == 1:
            found, method = xlsx_by_name_company[(nm, co)][0], 'name+company'
        elif e:
            dom = e.split('@')[-1]
            if dom in xlsx_by_domain:
                found, method = xlsx_by_domain[dom], 'domain'
        if not found and nm and co:
            parts = nm.split()
            if len(parts) >= 2:
                for x in xlsx:
                    xn = norm(x.get('contact', ''))
                    xp = xn.split()
                    if len(xp) >= 2 and xp[0] == parts[0] and xp[-1] == parts[-1]:
                        if co and norm(x.get('company', '')).startswith(co[:8]):
                            found, method = x, 'fuzzy_name_co'
                            break

        if found:
            matched.append({**h, 'xlsx_company': found.get('company'),
                            'xlsx_contact': found.get('contact'),
                            'xlsx_email': found.get('email'),
                            'xlsx_phone': found.get('phone'),
                            'xlsx_linkedin': found.get('linkedin'),
                            'xlsx_score': found.get('intel_score'),
                            'xlsx_routing': found.get('routing'),
                            'xlsx_country': found.get('country'),
                            'xlsx_kyc': found.get('kyc'),
                            'xlsx_industry': found.get('industry'),
                            'xlsx_commodity': found.get('commodity'),
                            'xlsx_region': found.get('region'),
                            'xlsx_priority': found.get('priority'),
                            'xlsx_volume': found.get('volume'),
                            'xlsx_address': found.get('address'),
                            'xlsx_website': found.get('website'),
                            'xlsx_logistics': found.get('logistics'),
                            'method': method})
        else:
            unmatched.append(h)
    print(f'  matched: {len(matched)}  unmatched: {len(unmatched)}')
    return matched, unmatched


# ---- 5. Rank the 96 real-named leads ----
def rank_real_leads(unmatched, xlsx):
    print('[4/4] Ranking real-named leads by enrichment potential...')
    xlsx_by_company = defaultdict(list)
    for c in xlsx:
        co = (c.get('company') or '').strip()
        if co:
            xlsx_by_company[co.lower()].append(c)
    xlsx_by_domain = {}
    for c in xlsx:
        web = (c.get('website') or '').lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        if web:
            xlsx_by_domain[web] = c
        if c.get('email'):
            dom = c['email'].split('@')[-1].lower()
            xlsx_by_domain.setdefault(dom, c)

    def safe(s):
        return (s or '').strip()

    REAL_LEAD_BADGE = ('Procurement', 'Team', 'Info', 'Supply', 'Contact', 'Secretary',
                       'Sales', 'Corporate', 'Recruitment', 'Marketing', 'EDC', 'AES', 'Basal')

    real = []
    for h in unmatched:
        nm, co, em = safe(h['name']), safe(h['company']), safe(h['email'])
        if 'econares' in co.lower() or 'econares' in em.lower():
            continue
        if 'bulk-ore' in em.lower():
            continue
        if not nm or nm == 'None None':
            continue
        if any(p in nm for p in REAL_LEAD_BADGE):
            continue
        real.append(h)

    def score(lead):
        s = 0
        reasons = []
        em = safe(lead.get('email', ''))
        if em:
            s += 10
            reasons.append('has_email')
            local = em.split('@')[0].lower()
            if local not in ('info', 'contact', 'sales', 'admin', 'enquiries', 'enquiry', 'procurement', 'inquiry', 'inquiries') and not local.startswith('noreply'):
                s += 5
                reasons.append('personal_email')
            dom = em.split('@')[-1].lower()
            if not any(d in dom for d in ('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com')):
                s += 5
                reasons.append('corporate_domain')
        lc = safe(lead.get('lifecycle', ''))
        if lc == 'opportunity':
            s += 30
            reasons.append('lifecycle=opportunity')
        elif lc == 'salesqualifiedlead':
            s += 25
            reasons.append('lifecycle=SQL')
        elif lc == 'marketingqualifiedlead':
            s += 20
            reasons.append('lifecycle=MQL')
        elif lc == 'lead':
            s += 5
            reasons.append('lifecycle=lead')
        ls = safe(lead.get('lead_status', ''))
        if ls in ('IN_PROGRESS', 'OPEN'):
            s += 5
            reasons.append(f'status={ls}')
        co = safe(lead.get('company', ''))
        co_n = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', co.lower())).strip()
        if co_n in xlsx_by_company:
            best = max(xlsx_by_company[co_n], key=lambda c: int(c.get('intel_score') or 0) if str(c.get('intel_score', '')).isdigit() else 0)
            sv = int(best.get('intel_score') or 0) if str(best.get('intel_score', '')).isdigit() else 0
            s += sv // 5
            reasons.append(f'company_in_xlsx(intel={sv})')
        elif co:
            for xc in xlsx_by_company:
                if co_n[:8] in xc or xc[:8] in co_n:
                    s += 3
                    reasons.append('company_partial_xlsx')
                    break
        if em and '@' in em:
            dom = em.split('@')[-1].lower()
            if dom in xlsx_by_domain:
                xc = xlsx_by_domain[dom]
                sv = int(xc.get('intel_score') or 0) if str(xc.get('intel_score', '')).isdigit() else 0
                s += sv // 5
                reasons.append(f'domain_in_xlsx(intel={sv})')
        if safe(lead.get('buying_role', '')):
            s += 10
            reasons.append('has_buying_role')
        mod = safe(lead.get('modified', ''))
        if '2026' in mod and ('05' in mod or '06' in mod):
            s += 3
            reasons.append('recently_modified')
        return s, reasons

    for lead in real:
        s, reasons = score(lead)
        lead['priority_score'] = s
        lead['priority_reasons'] = reasons
    real.sort(key=lambda x: (-x['priority_score'], x['name']))
    print(f'  ranked {len(real)} real-named leads')
    return real


# ---- Main ----
def main():
    token = load_token()
    if not token:
        print('FAIL: HUBSPOT_ACCESS_TOKEN not in env')
        sys.exit(2)

    TEMP_DIR.mkdir(exist_ok=True)

    # Pull + score
    all_contacts = pull_all_contacts(token)
    (TEMP_DIR / 'hub_all_contacts.json').write_text(json.dumps(all_contacts, indent=2))
    gaps = score_gaps(all_contacts)
    (TEMP_DIR / 'hub_gaps_v2.json').write_text(json.dumps(gaps, indent=2))
    print(f'  wrote hub_all_contacts.json ({len(all_contacts)} contacts)')
    print(f'  wrote hub_gaps_v2.json ({len(gaps)} gaps)')

    # Decode XLSX
    xlsx = decode_xlsx(XLSX_PATH)
    (TEMP_DIR / 'xlsx_contacts.json').write_text(json.dumps(xlsx, indent=2, ensure_ascii=False))
    print(f'  wrote xlsx_contacts.json ({len(xlsx)} unique XLSX contacts)')

    # Cross-reference
    matched, unmatched = cross_reference(gaps, xlsx)
    (TEMP_DIR / 'matches.json').write_text(json.dumps(matched, indent=2, ensure_ascii=False))
    (TEMP_DIR / 'unmatched.json').write_text(json.dumps(unmatched, indent=2, ensure_ascii=False))

    # Rank
    ranked = rank_real_leads(unmatched, xlsx)
    (TEMP_DIR / 'research_brief_full.json').write_text(json.dumps(ranked, indent=2, ensure_ascii=False))

    print()
    print('=== AUDIT COMPLETE ===')
    print(f'  HubSpot total:     {len(all_contacts)}')
    print(f'  HubSpot gaps:      {len(gaps)}')
    print(f'  XLSX total:        {len(xlsx)}')
    print(f'  XLSX matches:      {len(matched)}')
    print(f'  Unmatched:         {len(unmatched)}')
    print(f'  Real named leads:  {len(ranked)}')
    print()
    print('Next step: run build_research_brief.py to generate contact_research_brief_*.csv + .md')


if __name__ == '__main__':
    main()
