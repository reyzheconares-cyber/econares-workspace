#!/usr/bin/env python3
"""Pre-flight for round 2 next batch: Liza Sigua, Pia Alipio, Feifei Liu."""
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


# 481005002437 Liza Sigua
# 483002066641 Pia Alipio
# 469448074998 Feifei Liu
for cid, name in [
    ('481005002437', 'Liza Sigua'),
    ('483002066641', 'Pia Alipio'),
    ('469448074998', 'Feifei Liu'),
    ('499134924528', 'Great Odili'),
]:
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,jobtitle,company,hs_linkedin_url,phone,lifecyclestage')
    if code == 200:
        p = body.get('properties', {})
        print(f"\n=== {cid}: {name} ===")
        for k, v in p.items():
            if v:
                print(f"  {k}: {v}")
