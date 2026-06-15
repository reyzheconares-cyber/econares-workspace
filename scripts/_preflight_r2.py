#!/usr/bin/env python3
"""Pre-flight: check current HubSpot state for the next round 2 contact."""
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


# Bong Acacio (478270415572)
for cid, name in [('478270415572', 'Bong Acacio'), ('480931219144', 'Rose Encallado')]:
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,jobtitle,company,hs_linkedin_url,phone,lifecyclestage')
    if code == 200:
        p = body.get('properties', {})
        print(f"\n=== {cid}: {name} ===")
        for k, v in p.items():
            if v:
                print(f"  {k}: {v}")
