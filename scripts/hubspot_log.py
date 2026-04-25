#!/usr/bin/env python3
"""
ECONARES HubSpot Logger — /log command
Usage: /log Company - Contact Name - Status - Notes - Next Action - Date

Examples:
  /log Suprea Concrete - Aubrey connected - Ready Mixed - wants 20-30K MT/mo - callback April 28 - 2026-04-28
  /log Bulk Ore Ltd - Mr. Chen - Active - FCO sent for 5000MT Ni ore CIF Ningbo - follow up May 2 - 2026-05-02
  /log Mabuhay Cement - Nona Libradilla - Prospect - Diesel 10KL/90days - appointment email sent - 2026-04-25
"""

import sys
import os
import json
import re
import subprocess
import datetime

PAT = None
HUBSPOT_OWNER_ID = "90091659"

# Load PAT from .env
try:
    env_path = os.path.expanduser("/home/mauiclaw/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            if "HUBSPOT_ACCESS_TOKEN" in line and "export" in line:
                parts = line.strip().split('"')
                if len(parts) >= 2:
                    PAT = parts[1]
                elif "=" in line:
                    PAT = line.split("=", 1)[1].strip()
                break
except:
    pass

if not PAT:
    print("ERROR: Could not load HubSpot token")
    sys.exit(1)


def api_get(url):
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {PAT}", url],
        capture_output=True, text=True, timeout=15
    )
    try:
        return json.loads(r.stdout)
    except:
        return {}


def api_post(url, data):
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", "-H", f"Authorization: Bearer {PAT}",
         "-H", "Content-Type: application/json", "-d", json.dumps(data), url],
        capture_output=True, text=True, timeout=15
    )
    try:
        return json.loads(r.stdout)
    except:
        return {}


def search_contact(query, limit=5):
    return api_post(
        "https://api.hubapi.com/crm/v3/objects/contacts/search",
        {"query": query, "limit": limit, "properties": ["firstname", "lastname", "company", "email", "phone"]}
    )


def search_company(query, limit=5):
    return api_post(
        "https://api.hubapi.com/crm/v3/objects/companies/search",
        {"query": query, "limit": limit, "properties": ["name"]}
    )


def create_contact(firstname, lastname, company="", jobtitle="", phone="", email=""):
    props = {"firstname": firstname, "lastname": lastname}
    if company:
        props["company"] = company
    if jobtitle:
        props["jobtitle"] = jobtitle
    if phone:
        props["phone"] = phone
    if email:
        props["email"] = email
    return api_post("https://api.hubapi.com/crm/v3/objects/contacts", {"properties": props})


def create_company(name):
    return api_post("https://api.hubapi.com/crm/v3/objects/companies", {"properties": {"name": name}})


def create_task(subject, body, due_date, priority="MEDIUM", status="NOT_STARTED"):
    return api_post(
        "https://api.hubapi.com/crm/v3/objects/tasks",
        {
            "properties": {
                "hs_task_subject": subject,
                "hs_task_body": body,
                "hs_task_status": status,
                "hs_timestamp": f"{due_date}T09:00:00Z",
                "hs_task_priority": priority,
                "hubspot_owner_id": HUBSPOT_OWNER_ID
            }
        }
    )


def create_note(body, contact_id=None):
    data = {"properties": {"hs_note_body": body, "hs_timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}}
    return api_post("https://api.hubapi.com/crm/v3/objects/notes", data)


def parse_log_input(raw):
    """Parse the /log input into components."""
    # Format: Company - Contact - Status - Notes - Next Action - Date
    parts = [p.strip() for p in raw.split(" - ")]
    
    if len(parts) < 2:
        return None
    
    company = parts[0] if len(parts) >= 1 else ""
    contact = parts[1] if len(parts) >= 2 else ""
    status = parts[2] if len(parts) >= 3 else ""
    notes = parts[3] if len(parts) >= 4 else ""
    next_action = parts[4] if len(parts) >= 5 else ""
    due_date = parts[5] if len(parts) >= 6 else ""
    
    # Parse contact into first/last name
    contact_parts = contact.split()
    firstname = contact_parts[0] if contact_parts else ""
    lastname = " ".join(contact_parts[1:]) if len(contact_parts) > 1 else ""
    
    return {
        "company": company,
        "firstname": firstname,
        "lastname": lastname,
        "status": status,
        "notes": notes,
        "next_action": next_action,
        "due_date": due_date
    }


def run():
    if len(sys.argv) < 2:
        print("Usage: /log Company - Contact Name - Status - Notes - Next Action - Date")
        print("")
        print("Example: /log Suprea Concrete - Aubrey connected - Ready Mixed - wants 20-30K MT/mo - callback April 28 - 2026-04-28")
        sys.exit(1)
    
    raw_input = " ".join(sys.argv[1:])
    parsed = parse_log_input(raw_input)
    
    if not parsed:
        print("ERROR: Could not parse input. Use format:")
        print("  /log Company - Contact Name - Status - Notes - Next Action - Date")
        sys.exit(1)
    
    print(f"\n=== PROCESSING ===")
    print(f"Company: {parsed['company']}")
    print(f"Contact: {parsed['firstname']} {parsed['lastname']}")
    print(f"Status: {parsed['status']}")
    print(f"Notes: {parsed['notes']}")
    print(f"Next Action: {parsed['next_action']}")
    print(f"Due Date: {parsed['due_date']}")
    print()
    
    # Step 1: Find or create company
    print("[1/4] Searching company...")
    company_result = search_company(parsed["company"])
    companies = company_result.get("results", [])
    
    if companies:
        company_id = companies[0]["id"]
        print(f"    Found existing company: {companies[0]['properties'].get('name', '')} (ID: {company_id})")
    else:
        print(f"    Creating new company: {parsed['company']}...")
        company_result = create_company(parsed["company"])
        company_id = company_result.get("id")
        if company_id:
            print(f"    Created company (ID: {company_id})")
        else:
            print(f"    WARNING: Could not create company: {company_result}")
            company_id = None
    
    # Step 2: Find or create contact
    print("[2/4] Searching contact...")
    contact_result = search_contact(f"{parsed['firstname']} {parsed['lastname']}")
    contacts = contact_result.get("results", [])
    
    if contacts:
        contact_id = contacts[0]["id"]
        print(f"    Found existing contact: {parsed['firstname']} {parsed['lastname']} (ID: {contact_id})")
    else:
        print(f"    Creating new contact...")
        contact_result = create_contact(
            parsed["firstname"],
            parsed["lastname"],
            company=parsed["company"]
        )
        contact_id = contact_result.get("id")
        if contact_id:
            print(f"    Created contact (ID: {contact_id})")
        else:
            print(f"    WARNING: Could not create contact: {contact_result}")
            contact_id = None
    
    # Step 3: Create note with engagement details
    print("[3/4] Creating engagement note...")
    note_body = f"""ECONARES LOG ENTRY — {datetime.datetime.utcnow().strftime('%Y-%m-%d')}

Company: {parsed['company']}
Contact: {parsed['firstname']} {parsed['lastname']}
Status: {parsed['status']}

Notes: {parsed['notes']}

Next Action: {parsed['next_action']}
Due Date: {parsed['due_date']}
"""
    note_result = create_note(note_body)
    note_id = note_result.get("id")
    if note_id:
        print(f"    Note created (ID: {note_id})")
    else:
        print(f"    WARNING: Could not create note: {note_result}")
    
    # Step 4: Create follow-up task
    print("[4/4] Creating follow-up task...")
    if parsed["next_action"] and parsed["due_date"]:
        task_subject = f"[{parsed['company']}] {parsed['next_action']}"
        task_body = f"Company: {parsed['company']}\nContact: {parsed['firstname']} {parsed['lastname']}\nStatus: {parsed['status']}\n\nNotes: {parsed['notes']}"
        priority_map = {"HIGH": "HIGH", "high": "HIGH", "MEDIUM": "MEDIUM", "medium": "MEDIUM", "LOW": "LOW", "low": "LOW"}
        priority = priority_map.get(parsed["status"].upper(), "MEDIUM") if parsed["status"] else "MEDIUM"
        
        task_result = create_task(task_subject, task_body, parsed["due_date"], priority=priority)
        task_id = task_result.get("id")
        if task_id:
            print(f"    Task created (ID: {task_id}, Due: {parsed['due_date']})")
        else:
            print(f"    WARNING: Could not create task: {task_result}")
    elif parsed["next_action"]:
        print(f"    Skipping task — no due date specified")
    else:
        print(f"    Skipping task — no next action specified")
    
    print()
    print("=== DONE ===")
    print(f"Logged to HubSpot: {parsed['company']} — {parsed['firstname']} {parsed['lastname']}")


if __name__ == "__main__":
    run()
