#!/usr/bin/env python3
"""Pre-flight: re-check state of the 15 candidates + write each."""
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


candidates = json.load(open(r'C:/Users/reyma/AppData/Local/Temp/blank_company_candidates.json'))

for c in candidates:
    cid = c['id']
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,company,jobtitle')
    p = body.get('properties', {})
    nm = ((p.get('firstname') or '') + ' ' + (p.get('lastname') or '')).strip()
    print(f"  {cid}  {nm[:30]:<30}  email='{(p.get('email') or '')[:30]}'  company='{p.get('company','')}'")
