#!/usr/bin/env python3
"""Quarantine internal and orphan contacts by setting lifecyclestage=other.
Industry best practice for hygiene without destructive deletion."""
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

# Loaded from the unmatched.json analysis
INTERNALS = [
    '462552038097', # lsf.econares@gmail.com
    '464341160651', # jc.econares@gmail.com
    '469804523234', # asb.econares@gmail.com
    '482151092961', # gbteconares@gmail.com
    '482888176359', # mnd.econares@gmail.com
    '486369469114', # mob.econares@gmail.com
    '488438211314', # bra.econares@gmail.com
    '469804523234', # asb.econares@gmail.com (duplicate in my list, set ensures unique)
]

ORPHANS = [
    '480948409032', # Mailchimp Imports None
    '480965293814', # None None (clabeto@mgen.com.ph)
    '484498666174', # None None (dcinvestmentpromotion@gmail.com)
    '486370143934', # None None (hyxh@huayou.com)
]

TO_QUARANTINE = list(set(INTERNALS + ORPHANS))

print(f"=== QUARANTINING {len(TO_QUARANTINE)} INTERNAL/ORPHAN CONTACTS ===")
for cid in TO_QUARANTINE:
    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}',
                      {"properties": {"lifecyclestage": "other"}})
    if code in (200, 201):
        print(f"  {cid} -> lifecyclestage=other  OK")
    else:
        print(f"  FAIL on {cid}: HTTP {code} {body}")
