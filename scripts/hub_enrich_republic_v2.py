#!/usr/bin/env python3
"""
Final pass — Republic Cement enrichment with verified portal enum + stage IDs.

Honest pipeline hygiene:
  Deal stage = "Initial Contact" (3410654913) - not Appointment Scheduled.
  Reality: 3 emails sent, zero replies. Inflating the stage corrupts the forecast.
  Buying role enum = [BLOCKER, BUDGET_HOLDER, CHAMPION, DECISION_MAKER,
                      END_USER, EXECUTIVE_SPONSOR, INFLUENCER,
                      LEGAL_AND_COMPLIANCE, OTHER]
  Industry best practice: VP-level = EXECUTIVE_SPONSOR, unresponsive gatekeeper = BLOCKER.
"""
import json
import os
import sys
import urllib.request
import urllib.error

ENV = os.path.expanduser("~/.hermes/.env")


def tok():
    with open(ENV) as f:
        for l in f:
            s = l.lstrip()
            if s.startswith("export "):
                s = s[7:]
            if s.startswith("HUBSPOT_ACCESS_TOKEN"):
                return s.split("=", 1)[1].strip().strip('"').strip("'")
    return None


T = tok()
if not T:
    sys.exit("no token")
BASE = "https://api.hubapi.com"


def http(m, u, b=None):
    r = urllib.request.Request(u, method=m)
    r.add_header("Authorization", f"Bearer {T}")
    r.add_header("Content-Type", "application/json")
    d = json.dumps(b).encode() if b is not None else None
    try:
        with urllib.request.urlopen(r, data=d, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {"err": e.read().decode()[:600]}


COMPANY_ID = "320106199766"

# --- 1. Patch 5 contact buying roles (idempotent) ---
ROLES = {
    "486865810164": "EXECUTIVE_SPONSOR",  # Mark Dimal (VP Supply Chain)
    "486865663724": "DECISION_MAKER",    # Rande Almarinez (Procurement Office Head)
    "471331594971": "CHAMPION",          # Allan Saquilayan (forwarding champion)
    "486856807101": "INFLUENCER",        # Rey Floresca
    "480143362798": "BLOCKER",           # Rachel Anne Castillo (unresponsive)
}
print("=== SET BUYING ROLES (5 contacts) ===")
for cid, role in ROLES.items():
    code, body = http(
        "PATCH",
        f"{BASE}/crm/v3/objects/contacts/{cid}",
        {"properties": {"hs_buying_role": role}},
    )
    if code in (200, 201):
        print(f"  {cid}  {role}  OK")
    else:
        print(f"  {cid}  {role}  FAIL {code} {body}")

# --- 2. Create deal - stage = Initial Contact (3410654913) ---
print("\n=== CREATE DEAL ===")
DESC = (
    "Pilot fuel-mix program (coal + PKS + woodchips) supporting Republic Cement's "
    "co-processing and decarbonization roadmap. Plant corridors: (1) Luzon - "
    "Bulacan/Rizal/Batangas, discharge via Manila Bay / Batangas; (2) Visayas - "
    "Danao/Cebu, discharge via Cebu Port; (3) Mindanao - Iligan. "
    "Buying center: Dimal (Exec Sponsor), Almarinez (DM), Saquilayan (Champion), "
    "Floresca (Influencer), Castillo (Blocker - currently unresponsive). "
    "Bypass contact added: Meraflor Tagactac (Mindanao Supply Chain). "
    "Lead Source: Outbound Prospecting."
)
deal_payload = {
    "properties": {
        "dealname": "Republic Cement - Fuel Mix Pilot (Coal + PKS)",
        "pipeline": "default",
        "dealstage": "3410654913",  # Initial Contact
        "amount": "5000000",
        "closedate": "2026-09-30",
        "dealtype": "newbusiness",
        "description": DESC,
    }
}
code, body = http("POST", f"{BASE}/crm/v3/objects/deals", deal_payload)
DEAL_ID = None
if code in (200, 201):
    DEAL_ID = body.get("id")
    print(f"  deal created id={DEAL_ID}")
    code2, body2 = http(
        "PUT",
        f"{BASE}/crm/v3/objects/deals/{DEAL_ID}/associations/companies/{COMPANY_ID}/deals_to_company",
        [],
    )
    print(f"  associate deal->company  HTTP {code2}")
else:
    print(f"  FAIL {code} {body}")

# --- 3. Create Meraflor Tagactac (no 'department' prop - it doesn't exist) ---
print("\n=== CREATE CONTACT: Meraflor Tagactac ===")
mera_payload = {
    "properties": {
        "firstname": "Meraflor",
        "lastname": "Tagactac",
        "jobtitle": "Associate Procurement Manager - Supply Chain (Mindanao)",
        "company": "Republic Cement",
        "lifecyclestage": "lead",
        "hs_lead_status": "NEW",
        "hs_buying_role": "INFLUENCER",
    }
}
code, body = http("POST", f"{BASE}/crm/v3/objects/contacts", mera_payload)
MERA_ID = None
if code in (200, 201):
    MERA_ID = body.get("id")
    print(f"  created id={MERA_ID}")
else:
    print(f"  create result: HTTP {code} {body}")
    s_code, s_body = http(
        "POST",
        f"{BASE}/crm/v3/objects/contacts/search",
        {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "firstname", "operator": "EQ", "value": "Meraflor"},
                        {"propertyName": "lastname", "operator": "EQ", "value": "Tagactac"},
                    ]
                }
            ],
            "properties": ["firstname", "lastname", "hs_object_id"],
            "limit": 5,
        },
    )
    if s_code == 200 and s_body.get("results"):
        MERA_ID = s_body["results"][0]["id"]
        print(f"  found existing id={MERA_ID}, reusing")
        http(
            "PATCH",
            f"{BASE}/crm/v3/objects/contacts/{MERA_ID}",
            {
                "properties": {
                    "hs_buying_role": "INFLUENCER",
                    "jobtitle": "Associate Procurement Manager - Supply Chain (Mindanao)",
                }
            },
        )

if MERA_ID:
    code, body = http(
        "PUT",
        f"{BASE}/crm/v3/objects/contacts/{MERA_ID}/associations/companies/{COMPANY_ID}/contact_to_company",
        [],
    )
    print(f"  associate contact->company  HTTP {code}")

# --- 4. Verify read-back ---
print("\n=== VERIFY READ-BACK ===")
for cid, expected in ROLES.items():
    code, body = http(
        "GET",
        f"{BASE}/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,hs_buying_role,jobtitle",
    )
    if code == 200:
        p = body.get("properties", {})
        actual = p.get("hs_buying_role", "<unset>")
        flag = "OK" if actual == expected else "MISMATCH"
        print(
            f"  [{flag}] {cid}: {p.get('firstname','')} {p.get('lastname','')} | role={actual} (expected {expected})"
        )

if DEAL_ID:
    code, body = http(
        "GET",
        f"{BASE}/crm/v3/objects/deals/{DEAL_ID}?properties=dealname,dealstage,amount,closedate,pipeline,dealtype",
    )
    if code == 200:
        p = body.get("properties", {})
        print(f"\n  DEAL {DEAL_ID}:")
        for k, v in p.items():
            if v:
                print(f"    {k}: {v}")
    code, body = http(
        "GET", f"{BASE}/crm/v3/objects/deals/{DEAL_ID}/associations/companies"
    )
    if code == 200:
        assocs = body.get("results", [])
        print(f"  deal->companies: {[a['id'] for a in assocs]}")

if MERA_ID:
    code, body = http(
        "GET",
        f"{BASE}/crm/v3/objects/contacts/{MERA_ID}?properties=firstname,lastname,jobtitle,company,hs_buying_role,lifecyclestage,hs_lead_status",
    )
    if code == 200:
        p = body.get("properties", {})
        print(f"\n  MERAFLOR {MERA_ID}:")
        for k, v in p.items():
            if v:
                print(f"    {k}: {v}")
    code, body = http(
        "GET", f"{BASE}/crm/v3/objects/contacts/{MERA_ID}/associations/companies"
    )
    if code == 200:
        assocs = body.get("results", [])
        print(f"  mera->companies: {[a['id'] for a in assocs]}")

print("\n=== FINAL COMPANY SUMMARY ===")
code, body = http(
    "GET",
    f"{BASE}/crm/v3/objects/companies/{COMPANY_ID}?properties=name,industry,description,phone,address,city,country,numberofemployees,founded_year,annualrevenue,linkedin_company_page,lifecyclestage,hs_lead_status",
)
if code == 200:
    p = body.get("properties", {})
    for k, v in p.items():
        if v:
            print(f"  {k}: {v}")
