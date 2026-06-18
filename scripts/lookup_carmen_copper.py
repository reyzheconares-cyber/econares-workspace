#!/usr/bin/env python
"""Look up the company for contact 482909437631 (L.M. Pantilo) so we can
back-fill the company association for the Carmen Copper orphan task."""

from pathlib import Path
import requests

TOKEN_PATH=*** / ".hermes" / ".env"
BASE = "https://api.hubapi.com"
CONTACT_ID = "482909437631"


def load_token():
    text = TOKEN_PATH.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        if s.startswith("HUBSPOT_ACCESS_TOKEN=***            val = s.split("=", 1)[1].strip().strip('"').strip("'")
            return val
    raise RuntimeError("no token")


tok = load_token()
h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

# 1. Get the contact's full record with company
url = f"{BASE}/crm/v3/objects/contacts/{CONTACT_ID}"
r = requests.get(url, headers=h, params={"properties": "firstname,lastname,email,company,associatedcompanyid,associatedcompany"}, timeout=30)
print("CONTACT GET status:", r.status_code)
print(r.json())

# 2. Also search companies for "atlas consolidated" and "carmen copper corporation" and "carmen"
for q in ["Carmen Copper Corporation", "Carmen Copper", "Atlas Consolidated", "carmencopper"]:
    sr = requests.post(f"{BASE}/crm/v3/objects/companies/search",
                       headers=h, json={"query": q, "limit": 3,
                                        "properties": ["name", "domain"]}, timeout=30)
    print(f"\nCOMPANY SEARCH '{q}': {sr.status_code}")
    for res in sr.json().get("results", []):
        print(f"  {res['id']}  {res.get('properties', {}).get('name', '')}  domain={res.get('properties', {}).get('domain', '')}")
