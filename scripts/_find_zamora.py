#!/usr/bin/env python3
"""Find Martin Zamora via email or company."""
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


# search by email
search_body = {
    "filterGroups": [{
        "filters": [{
            "propertyName": "email",
            "operator": "EQ",
            "value": "hello@nickelasia.com"
        }]
    }],
    "properties": ["firstname", "lastname", "email", "jobtitle", "company", "hs_linkedin_url"],
    "limit": 5
}
code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/search', search_body)
print(f"Search by email: HTTP {code}, results={len(body.get('results', []))}")
for r in body.get('results', []):
    p = r.get('properties', {})
    print(f"  {r['id']}: {p.get('firstname','')} {p.get('lastname','')} | {p.get('company','')} | email={p.get('email','')} | linkedin={p.get('hs_linkedin_url','')}")
    print(f"    jobtitle: {p.get('jobtitle','')}")

# search by company
search_body = {
    "filterGroups": [{
        "filters": [{
            "propertyName": "company",
            "operator": "CONTAINS",
            "value": "Nickel Asia"
        }]
    }],
    "properties": ["firstname", "lastname", "email", "jobtitle", "company", "hs_linkedin_url"],
    "limit": 10
}
code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/search', search_body)
print(f"\nSearch by company contains 'Nickel Asia': HTTP {code}, results={len(body.get('results', []))}")
for r in body.get('results', []):
    p = r.get('properties', {})
    print(f"  {r['id']}: {p.get('firstname','')} {p.get('lastname','')} | {p.get('company','')} | email={p.get('email','')} | linkedin={p.get('hs_linkedin_url','')}")
    print(f"    jobtitle: {p.get('jobtitle','')}")
