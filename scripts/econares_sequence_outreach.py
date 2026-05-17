#!/usr/bin/env python3
"""
ECONARES Multi-Sequence Outreach Tracker
3-Touch Outreach System: Coal, Cement, Nickel
Phase 4 - Automated Outreach State Management
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

WORKSPACE = "/home/mauiclaw/ECONARES_WORKSPACE"
STATE_FILE = f"{WORKSPACE}/outreach_state.json"

TOUCH_TEMPLATES = {
    "coal": {
        "touch_1": {"channel": "email", "subject": "Indonesian Coal Supply Inquiry",
            "body": "Hi {name}, I'm reaching out from ECONARES regarding Indonesian coal supply. We work with miners directly on 5500-5800 GAR spec. Are you currently in the market for Q3 delivery? Happy to share specs and loading port options. Regards, Fraser", "gap_days": 4},
        "touch_2": {"channel": "email", "subject": "Quick market update - Indonesian coal 5500 GAR",
            "body": "Hi {name}, Quick market update - Indonesian coal 5500 GAR is currently at [price] FOB. Happy to share a full spec sheet. We've been moving decent volume through Taboneo this quarter. Let me know if you'd like to connect. Regards, Fraser", "gap_days": 5},
        "touch_3": {"channel": "SMS", "subject": "",
            "body": "Hi {name}, following up on my earlier message about coal supply. Are you the right person to speak with re: procurement? Happy to send a quick proposal. - Fraser/ECONARES", "gap_days": 0}
    },
    "cement": {
        "touch_1": {"channel": "email", "subject": "Cement Supply Partnership Inquiry",
            "body": "Hi {name}, ECONARES here regarding cement supply. We work with grinding stations in SE Asia on OPC and PPC grades. Are you sourcing for a project or ongoing operations? Can share mill test certs and loading schedules. Regards, Fraser", "gap_days": 4},
        "touch_2": {"channel": "email", "subject": "Cement market update - Philippines demand",
            "body": "Hi {name}, Quick market update - Indonesian cement is currently at [price] FOB. Happy to share a full spec sheet. We've been supplying into Luzon and Visayas. Let me know if you'd like to connect. Regards, Fraser", "gap_days": 5},
        "touch_3": {"channel": "SMS", "subject": "",
            "body": "Hi {name}, following up on my earlier message about cement supply. Are you the right person to speak with re: procurement? Happy to send a quick proposal. - Fraser/ECONARES", "gap_days": 0}
    },
    "nickel": {
        "touch_1": {"channel": "email", "subject": "Nickel Ore Supply Inquiry",
            "body": "Hi {name}, I'm reaching out from ECONARES regarding nickel ore supply. We work with miners in Indonesia on 1.5-1.8% Fe specs for stainless steel mills. Are you currently in the market? Happy to share analysis and port options. Regards, Fraser", "gap_days": 4},
        "touch_2": {"channel": "email", "subject": "Quick market update - Nickel ore CIF China",
            "body": "Hi {name}, Quick market update - Nickel ore 1.5% Fe is currently at [price] CIF China. Happy to share a full spec sheet. We've been moving volume through Shanghai and Rizhao ports. Let me know if you'd like to connect. Regards, Fraser", "gap_days": 5},
        "touch_3": {"channel": "SMS", "subject": "",
            "body": "Hi {name}, following up on my earlier message about nickel ore supply. Are you the right person to speak with re: procurement? Happy to send a quick proposal. - Fraser/ECONARES", "gap_days": 0}
    }
}

def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"contacts": [], "last_updated": None}

def save_state(state: Dict) -> None:
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_next_touch(current_touch: int) -> int:
    if current_touch >= 3:
        return 3
    return current_touch + 1

def get_touch_info(commodity: str, touch_num: int) -> Optional[Dict]:
    key = f"touch_{touch_num}"
    return TOUCH_TEMPLATES.get(commodity, {}).get(key)

def add_contact(name: str, company: str, commodity: str, email: str, phone: str = "", channel: str = "email") -> Dict:
    state = load_state()
    contact = {
        "id": f"{commodity[:3]}_{len(state['contacts']) + 1:03d}",
        "name": name, "company": company, "commodity": commodity.lower(),
        "email": email, "phone": phone, "preferred_channel": channel,
        "current_touch": 1, "last_contact_date": None, "last_touch_type": None,
        "status": "active", "created_at": datetime.now().isoformat(), "touch_history": []
    }
    state["contacts"].append(contact)
    save_state(state)
    return contact

def advance_contact(contact_id: str) -> Optional[Dict]:
    state = load_state()
    for contact in state["contacts"]:
        if contact["id"] == contact_id:
            current = contact["current_touch"]
            next_touch = get_next_touch(current)
            touch_info = get_touch_info(contact["commodity"], next_touch)
            if not touch_info:
                return None
            contact["current_touch"] = next_touch
            contact["last_contact_date"] = datetime.now().isoformat()
            contact["last_touch_type"] = touch_info["channel"]
            contact["touch_history"].append({"touch": next_touch, "date": datetime.now().isoformat(), "channel": touch_info["channel"]})
            if next_touch == 3:
                contact["status"] = "sequence_complete"
            save_state(state)
            return contact
    return None

def get_pending_outreach() -> List[Dict]:
    state = load_state()
    today = datetime.now().date()
    pending = []
    for contact in state["contacts"]:
        if contact["status"] in ["sequence_complete", "paused"]:
            continue
        last_date_str = contact.get("last_contact_date")
        if not last_date_str:
            pending.append({"contact": contact, "action": "send_touch_1", "message": f"NEW: {contact['name']} at {contact['company']} - ready for first contact"})
            continue
        last_date = datetime.fromisoformat(last_date_str).date()
        current_touch = contact["current_touch"]
        touch_info = get_touch_info(contact["commodity"], current_touch)
        if touch_info:
            gap = touch_info["gap_days"]
            if (today - last_date).days >= gap:
                pending.append({"contact": contact, "action": f"send_touch_{current_touch}", "message": f"DUE: {contact['name']} - touch {current_touch} after {gap} day gap"})
    return pending

def get_contact_by_id(contact_id: str) -> Optional[Dict]:
    state = load_state()
    for contact in state["contacts"]:
        if contact["id"] == contact_id:
            return contact
    return None

def pause_contact(contact_id: str) -> bool:
    state = load_state()
    for contact in state["contacts"]:
        if contact["id"] == contact_id:
            contact["status"] = "paused"
            save_state(state)
            return True
    return False

def resume_contact(contact_id: str) -> bool:
    state = load_state()
    for contact in state["contacts"]:
        if contact["id"] == contact_id:
            if contact["status"] == "paused":
                contact["status"] = "active"
                save_state(state)
                return True
    return False

def generate_outreach_message(contact_id: str) -> Optional[Dict]:
    contact = get_contact_by_id(contact_id)
    if not contact:
        return None
    touch_num = contact["current_touch"]
    touch_info = get_touch_info(contact["commodity"], touch_num)
    if not touch_info:
        return None
    body = touch_info["body"].format(name=contact["name"].split()[0])
    return {
        "contact_id": contact_id, "name": contact["name"], "company": contact["company"],
        "commodity": contact["commodity"], "touch": touch_num, "channel": touch_info["channel"],
        "subject": touch_info.get("subject", ""), "body": body,
        "email": contact["email"], "phone": contact["phone"]
    }

def print_status():
    state = load_state()
    print("\n=== ECONARES OUTREACH STATUS ===")
    print(f"Last Updated: {state.get('last_updated', 'Never')}")
    print(f"Total Contacts: {len(state['contacts'])}")
    for commodity in ["coal", "cement", "nickel"]:
        contacts = [c for c in state["contacts"] if c["commodity"] == commodity]
        active = [c for c in contacts if c["status"] == "active"]
        complete = [c for c in contacts if c["status"] == "sequence_complete"]
        print(f"\n{commodity.upper()}: {len(contacts)} total | {len(active)} active | {len(complete)} sequence complete")
        for c in contacts:
            print(f"  [{c['id']}] {c['name']} @ {c['company']} - Touch {c['current_touch']} ({c['status']})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ECONARES Outreach Tracker")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--add", nargs=4, metavar=("NAME", "COMPANY", "COMMODITY", "EMAIL"), help="Add new contact")
    parser.add_argument("--add-phone", nargs=5, metavar=("NAME", "COMPANY", "COMMODITY", "EMAIL", "PHONE"), help="Add new contact with phone")
    parser.add_argument("--pending", action="store_true", help="Show pending outreach")
    parser.add_argument("--generate", metavar="CONTACT_ID", help="Generate next message for contact")
    parser.add_argument("--advance", metavar="CONTACT_ID", help="Advance contact to next touch")
    parser.add_argument("--pause", metavar="CONTACT_ID", help="Pause contact outreach")
    parser.add_argument("--resume", metavar="CONTACT_ID", help="Resume paused contact")
    args = parser.parse_args()
    if args.status:
        print_status()
    elif args.add:
        contact = add_contact(*args.add)
        print(f"Added: {contact['id']} - {args.add[0]} @ {args.add[1]}")
    elif args.add_phone:
        contact = add_contact(args.add_phone[0], args.add_phone[1], args.add_phone[2], args.add_phone[3], args.add_phone[4])
        print(f"Added: {contact['id']} - {args.add_phone[0]} @ {args.add_phone[1]}")
    elif args.pending:
        pending = get_pending_outreach()
        print(f"\n=== PENDING OUTREACH ({len(pending)} contacts) ===")
        for item in pending:
            print(item["message"])
    elif args.generate:
        msg = generate_outreach_message(args.generate)
        if msg:
            print(f"\n=== MESSAGE FOR {msg['contact_id']} ===")
            print(f"To: {msg['name']} <{msg['email']}>")
            print(f"Channel: {msg['channel']}")
            print(f"Subject: {msg['subject']}")
            print(f"\n{msg['body']}")
        else:
            print("Contact not found or sequence complete")
    elif args.advance:
        result = advance_contact(args.advance)
        if result:
            print(f"Advanced {args.advance} to touch {result['current_touch']}")
        else:
            print("Contact not found")
    elif args.pause:
        print(f"Paused {args.pause}") if pause_contact(args.pause) else print("Contact not found")
    elif args.resume:
        print(f"Resumed {args.resume}") if resume_contact(args.resume) else print("Contact not found or not paused")
    else:
        parser.print_help()
