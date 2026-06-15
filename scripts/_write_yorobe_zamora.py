#!/usr/bin/env python3
"""Write Marc Yorobe and Martin Zamora LinkedIn URLs with verify-by-read-back."""
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


WRITES = [
    ('474507129539', 'Marc Yorobe', 'https://ph.linkedin.com/in/marc-yorobe-b5657828',
     'web_search: Power Generation Executive at Meralco PowerGen (MGEN), 500+ connections, Metro Manila'),
    ('482963044080', 'Martin Antonio Zamora', 'https://ph.linkedin.com/in/martin-antonio-zamora-b11472',
     'web_search: President and CEO of Nickel Asia Corporation (NAC), named Asia Outstanding Leader 2023'),
]

for cid, name, url, source in WRITES:
    print(f"\n=== {cid}: {name} ===")
    # Pre-write
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=hs_linkedin_url,firstname,lastname,jobtitle,company')
    p = body.get('properties', {})
    pre = p.get('hs_linkedin_url', '')
    print(f"  pre-write: hs_linkedin_url = '{pre}'")
    print(f"  jobtitle: '{p.get('jobtitle', '')}'")
    print(f"  company: '{p.get('company', '')}'")

    # KYC: only write if blank
    if pre and pre.strip() and pre != 'None':
        print(f"  KYC: pre-existing value, SKIP write")
        continue

    # PATCH
    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}',
                      {"properties": {"hs_linkedin_url": url}})
    print(f"  PATCH result: HTTP {code}")
    if code in (200, 201):
        print(f"    wrote: {url}")
        print(f"    source: {source}")
    else:
        print(f"    FAIL: {body}")
        continue

    # Read-back
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,hs_linkedin_url,jobtitle,company')
    if code == 200:
        p = body.get('properties', {})
        actual = p.get('hs_linkedin_url', '')
        print(f"  verify read-back: '{actual}'")
        print(f"  RESULT: {'OK' if actual == url else 'MISMATCH'}")
