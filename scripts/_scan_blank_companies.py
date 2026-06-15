#!/usr/bin/env python3
"""Find all HubSpot contacts with blank company + non-generic email domain.
This is the highest-confidence fill pattern: contact's own email = their employer."""
import json
import os
import urllib.request
import urllib.error

ENV = os.path.expanduser('~/.hermes/.env')


def tok():
    with open(ENV) as f:
        for line in f:
            s = line.lstrip()
            if s.startswith('export '):
                s = s[7:]
            if s.startswith('HUBSPOT_ACCESS_TOKEN'):
                return s.split('=', 1)[1].strip().strip('"').strip("'")
    return None


T = tok()


def http(m, u, b=None):
    r = urllib.request.Request(u, method=m)
    r.add_header('Authorization', f'Bearer {T}')
    r.add_header('Content-Type', 'application/json')
    d = json.dumps(b).encode() if b is not None else None
    try:
        with urllib.request.urlopen(r, data=d, timeout=60) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {'err': e.read().decode()[:500]}


# Known mappings (built incrementally)
DOMAIN_TO_COMPANY = {
    'mgen.com.ph': 'MGEN (Meralco PowerGen)',
    'aboitizpower.com': 'AboitizPower',
    'aboitiz.com': 'Aboitiz Group',
    'republiccement.com': 'Republic Cement',
    'cemexholdingsphilippines.com': 'CEMEX Holdings Philippines',
    'chp.com.ph': 'CEMEX Holdings Philippines',
    'solaris.com.ph': 'Solaris',
    'edc.com.ph': 'Energy Development Corporation',
    'energy.com.ph': 'First Gen (Energy Development Corporation)',
    'teamenergy.ph': 'Team Energy (Pagbilao Energy)',
    'globalpower.com.ph': 'Global Business Power / MGEN',
    'meralcopowergen.com': 'Meralco PowerGen (MGEN)',
    'taiheiyo-cement.com.ph': 'Taiheiyo Cement Philippines',
    'spcpowergroup.com': 'SPC Power Corporation (Salcon Group)',
    'mabuhaycement.com': 'Mabuhay Filcement Inc.',
    'mfcement.com': 'Mabuhay Filcement Inc.',
    'pcpc.ph': 'Palm Concepcion Power Corporation (PCPC)',
    'centurypeakcement.com': 'Century Peak Cement Manufacturing',
    'philcement.com.ph': 'Philcement Corporation',
    'unioncement.com.ph': 'Union Cement (Philcement)',
    'gnpower.com': 'GNPower',
    'gnpk.com.ph': 'GNPower Kauswagan',
    'smgp.sanmiguel.com.ph': 'San Miguel Global Power Holdings Corp.',
    'sanmiguel.com.ph': 'San Miguel Corporation',
    'semiraramining.com': 'Semirara Mining and Power Corporation',
    'alsonspower.com': 'Alsons Power',
    'panasiaenergy.ph': 'Panasia Energy',
    'eramenminerals.com': 'Eramen Minerals',
    'carmencopper.com': 'Carmen Copper Corporation',
    'gfni.com.ph': 'Global Ferronickel Holdings',
    'huayou.com': 'Zhejiang Huayou Cobalt',
    'lygend.com': 'Ningbo Lygend Wisdom',
    'ytxinhai.com': 'Shandong Xinhai Mining Equipment',
    'tsingshan-steels.com': 'Tsingshan Steel',
    'tssgroup.com.cn': 'Tsingshan Holding Group',
    'bigwaveresources.com': 'Big Wave Resources',
    'cathaypacificcargo.com': 'Cathay Pacific',
    'hkmr.com.hk': 'HK Materials Resources',
    'yuantuo.com': 'Yuantuo Resources',
    'byd.com': 'BYD Company',
    'catl.com': 'CATL (Contemporary Amperex Technology)',
    'dingchuang.com': 'Dingchuang Groups',
    'zkjck.com': 'Fujian Yunding Mining (Zhongke Jinhe)',
    'niscointl.cn': 'NISCO (National Industrial Symbioses)',
    'delonghi.com': 'Delong Nickel',
    'dlnis.com': 'Delong Nickel',
    'tisco.com.cn': 'TISCO (Baowu Group)',
    'citic.com': 'CITIC Group',
    'primary.com.ph': 'Primary Structures',
    'scbi.ph': 'San Carlos Bioenergy',
    'mabuhayfilcement.com': 'Mabuhay Filcement Inc.',
    'bulk-ore.com': 'Bulk Ore Limited',
    'minergypower.com.ph': 'Minergy Power Corporation',
    'rhi.com.ph': 'Republic Hydraulic Industries',
    'lafargeholcim.com': 'LafargeHolcim',
    'acciona.com': 'Acciona Energia',
    'upd.edu.ph': 'University of the Philippines',
    'up.edu.ph': 'University of the Philippines',
    'meralco.com.ph': 'Meralco',
    'nickelindustries.com': 'Nickel Industries',
    'jmm.co.jp': 'JX Advanced Metals',
    'sumitomocorp.com': 'Sumitomo Corporation',
    'aaltosenior.com': 'Aaltonen Senior',
    'mcc.com.cn': 'MCC',
    'sinosteel.com': 'Sinosteel',
    'crh.com': 'CRH plc',
    'lkggroup.com': 'LKG Group',
    'horizonmining.com.cn': 'Horizon Mining',
    'cssc.net.cn': 'CSSC',
    'chinaminmetals.com': 'China Minmetals',
    'phoenix-pulp.com': 'Phoenix Pulp',
    'switchon.ph': 'Switch-On',
    'mine Supply Pro': 'Mine Supply Pro',
    'ge.com': 'GE',
    'tavily.com': 'Tavily',
    'bhp.com': 'BHP',
    'rio.com.au': 'Rio Tinto',
    'vale.com': 'Vale',
    'glencore.com': 'Glencore',
    'angloamerican.com': 'Anglo American',
    'tesla.com': 'Tesla',
    'jm.com': 'Johnson Matthey',
    'uop.com': 'Honeywell UOP',
    'chevron.com': 'Chevron',
    'shell.com': 'Shell',
    'aaltosenior': 'Aaltonen',
    'concretesolutions.com.ph': 'Concrete Solutions Inc.',
    'eureka-forge.com': 'Eureka Forge',
    'philjayc.com': 'Philjayco',
    'philipinecement.com': 'Philcement',
    'alliance-rs.com': 'Alliance Resource',
    'santos-cement': 'Santos Cement',
    'eurochem.com': 'EuroChem',
    'vedanta.com': 'Vedanta',
    'importgroup.com': 'ImportGroup',
    'holcim.com': 'Holcim',
    'cebuconcrete.com': 'Cebu Concrete',
    'cbp.com.ph': 'CBP',
    'synergy-sc.com': 'Synergy SC',
    'asiacemex.com': 'Asia Cemex',
    'cogencor.com': 'Cogencor',
    'stone-sys.com': 'Stone Systems',
    'powersupply.com': 'Power Supply Co',
    'cebupacific': 'Cebu Pacific',
    'chincoalintl.com': 'China Coal International',
}

GENERIC = ('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'mail.ru', 'qq.com', '163.com', 'mailchimp.com')

# Pull all contacts
all_c = []
after = None
for page in range(20):
    body = {
        'filterGroups': [],
        'properties': ['firstname', 'lastname', 'email', 'jobtitle', 'company', 'phone', 'lifecyclestage', 'hs_lead_status'],
        'limit': 100,
        'sorts': [{'propertyName': 'hs_lastmodifieddate', 'direction': 'DESCENDING'}]
    }
    if after:
        body['after'] = after
    code, data = http('POST', f'https://api.hubapi.com/crm/v3/objects/contacts/search', body)
    if code != 200:
        break
    all_c.extend(data.get('results', []))
    after = data.get('paging', {}).get('next', {}).get('after')
    if not after:
        break

print(f"Total contacts: {len(all_c)}")

# Filter: blank company + non-generic email + mapped domain
candidates = []
for c in all_c:
    p = c.get('properties', {})
    co = (p.get('company') or '').strip()
    em = (p.get('email') or '').strip().lower()
    if co: continue
    if not em or '@' not in em: continue
    dom = em.split('@')[-1]
    if dom in GENERIC: continue
    nm = ((p.get('firstname') or '') + ' ' + (p.get('lastname') or '')).strip()
    if not nm: continue

    suggested = DOMAIN_TO_COMPANY.get(dom)
    if not suggested: continue

    candidates.append({
        'id': c['id'],
        'name': nm,
        'email': em,
        'domain': dom,
        'jobtitle': p.get('jobtitle', ''),
        'lifecycle': p.get('lifecyclestage', ''),
        'lead_status': p.get('hs_lead_status', ''),
        'suggested': suggested,
    })

print(f"\n=== Blank-company + corporate-domain candidates: {len(candidates)} ===\n")
for c in candidates:
    print(f"  {c['id']}  {c['name'][:30]:<30}  {c['email'][:35]:<35}  ->  {c['suggested']}")

# Save
with open(r'C:/Users/reyma/AppData/Local/Temp/blank_company_candidates.json', 'w') as f:
    json.dump(candidates, f, indent=2)
print(f"\nSaved to blank_company_candidates.json")
