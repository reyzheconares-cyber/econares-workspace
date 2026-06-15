#!/usr/bin/env python3
"""Find the correct HubSpot IDs for Marc Yorobe and Martin Zamora via search."""
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


# search for Marc Yorobe
search_body = {
    "filterGroups": [{
        "filters": [{
            "propertyName": "firstname",
            "operator": "EQ",
            "value": "Marc"
        }, {
            "propertyName": "lastname",
            "operator": "EQ",
            "value": "Yorobe"
        }]
    }],
    "properties": ["firstname", "lastname", "email", "jobtitle", "company", "hs_linkedin_url", "phone", "lifecyclestage"],
    "limit": 5
}
code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/search', search_body)
print(f"Search Marc Yorobe: HTTP {code}")
for r in body.get('results', []):
    p = r.get('properties', {})
    print(f"  {r['id']}: {p.get('firstname','')} {p.get('lastname','')} | {p.get('company','')} | email={p.get('email','')} | linkedin={p.get('hs_linkedin_url','')}")
    print(f"    jobtitle: {p.get('jobtitle','')}")

# search for Martin Zamora
search_body = {
    "filterGroups": [{
        "filters": [{
            "propertyName": "firstname",
            "operator": "EQ",
            "value": "Martin"
        }, {
            "propertyName": "lastname",
            "operator": "EQ",
            "value": "Zamora"
        }]
    }],
    "properties": ["firstname", "lastname", "email", "jobtitle", "company", "hs_linkedin_url", "phone", "lifecyclestage"],
    "limit": 5
}
code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/search', search_body)
print(f"\nSearch Martin Zamora: HTTP {code}")
for r in body.get('results', []):
    p = r.get('properties', {})
    print(f"  {r['id']}: {p.get('firstname','')} {p.get('lastname','')} | {p.get('company','')} | email={p.get('email','')} | linkedin={p.get('hs_linkedin_url','')}")
    print(f"    jobtitle: {p.get('jobtitle','')}")
