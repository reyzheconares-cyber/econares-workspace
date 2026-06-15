#!/usr/bin/env python3
"""Pre-flight for next batch (rank 17-25 in brief)."""
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


# Pull rank 17-30 from the brief
brief = json.load(open(r'C:/Users/reyma/AppData/Local/Temp/research_brief_full.json'))
for lead in brief[30:60]:
    cid = lead.get('id', '')
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,jobtitle,company,phone,hs_linkedin_url')
    if code == 200:
        p = body.get('properties', {})
        nm = ((p.get('firstname') or '') + ' ' + (p.get('lastname') or '')).strip()[:30]
        co = (p.get('company') or '')[:30]
        ph = p.get('phone') or ''
        em = (p.get('email') or '')[:30]
        print(f"  {cid}  {nm:<30} @ {co:<30} | phone='{ph}' | email='{em}'")
