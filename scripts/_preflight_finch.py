#!/usr/bin/env python3
"""Pre-flight: pull state of all bulk-ore.com contacts and the Ed Finch canonical record."""
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
        with urllib.request.urlopen(r, data=d, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {'err': e.read().decode()[:500]}


# All bulk-ore.com contacts + the Ed Finch canonical
IDS = [
    '473333584588',  # Ed Finch - canonical
    '486369435329',  # info@bulk-ore.com (no name)
    '488052007614',  # efinch@bulk-ore.com (no name)
    '488078159596',  # e.finch@bulk-ore.com (no name)
    '488085684984',  # ed@bulk-ore.com (no name)
    '488086162116',  # ed.finch@bulk-ore.com (no name)
]

print("=== CURRENT STATE OF BULK-ORE.COM CONTACTS ===\n")
for cid in IDS:
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,company,jobtitle,phone,lifecyclestage,hs_lead_status,hs_buying_role,hs_linkedin_url')
    if code == 200:
        p = body.get('properties', {})
        nm = ((p.get('firstname') or '') + ' ' + (p.get('lastname') or '')).strip()
        print(f"--- {cid} ---")
        for k, v in p.items():
            if v:
                print(f"  {k}: {v}")
        print()
    else:
        print(f"--- {cid}: HTTP {code} ---\n")

# Also check deal associations for the canonical
print("\n=== DEALS ASSOCIATED WITH ED FINCH (473333584588) ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/contacts/473333584588/associations/deals')
if code == 200:
    print(f"  deals: {body.get('results', [])}")

# Check companies associated
print("\n=== COMPANIES ASSOCIATED WITH ED FINCH ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/contacts/473333584588/associations/companies')
if code == 200:
    print(f"  companies: {body.get('results', [])}")
