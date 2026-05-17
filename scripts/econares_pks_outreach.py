#!/usr/bin/env python3
"""ECONARES PKS Market Development Outreach Phase 9"""

import os
from datetime import datetime
from typing import Dict, List

WORKSPACE = "/home/mauiclaw/ECONARES_WORKSPACE"
OUTREACH_DIR = f"{WORKSPACE}/outreach"
PKS_OUTREACH_FILE = f"{OUTREACH_DIR}/PKS_Market_Outreach_List.md"

CEMENT_PLANTS = {
    "Holcim Philippines": {"location": "Lugus, La Union", "type": "clinker", "pks_potential": "high", "procurement_contact": "Procurement Head", "notes": "Major multinational"},
    "Republic Cement": {"location": "Bulatao, Rizal", "type": "clinker", "pks_potential": "high", "procurement_contact": "Supply Chain Head", "notes": "Sustainability initiatives"},
    "Northern Cement": {"location": "Sison, Pangasinan", "type": "clinker", "pks_potential": "high", "procurement_contact": "Procurement Director", "notes": "Local group"},
    "Cemex Philippines": {"location": "Darong, Davao del Sur", "type": "clinker", "pks_potential": "medium", "procurement_contact": "Procurement Manager"},
    "Mindanao Cement": {"location": "Banga, South Cotabato", "type": "grinding", "pks_potential": "medium", "procurement_contact": "Procurement Officer"}
}

COAL_PLANTS = {
    "Sual Coal Plant": {"location": "Sual, Pangasinan", "capacity_mw": "1200", "pks_potential": "high", "owner": "SPPC/GTP", "procurement_contact": "Fuel Manager"},
    "Masinloc Coal Plant": {"location": "Masinloc, Zambales", "capacity_mw": "900", "pks_potential": "high", "owner": "TeaM Holdings", "procurement_contact": "Fuel Procurement"},
    "Santa Cruz Coal Plant": {"location": "Santa Cruz, Zambales", "capacity_mw": "600", "pks_potential": "medium", "owner": "GN Power", "procurement_contact": "Procurement Head"},
    "Pagbilao Coal Plant": {"location": "Pagbilao, Quezon", "capacity_mw": "900", "pks_potential": "medium", "owner": "Abott Group", "procurement_contact": "Supply Manager"},
    "Deductaca Coal Plant": {"location": "Cordova, Cebu", "capacity_mw": "200", "pks_potential": "medium", "owner": "Cebu Energy Development", "procurement_contact": "Procurement Officer"}
}

OUTREACH_TEMPLATE = """# ECONARES PKS MARKET DEVELOPMENT OUTREACH
Generated: {date}

## MARKET CONTEXT
PKS: Biomass from palm oil processing, 4,000-4,500 kcal/kg
Price: $80-120/MT CIF Philippines | Blend ratio: 10-30pct with coal

---

## CEMENT PLANT OUTREACH

### Holcim Philippines (HIGH)
**To:** Procurement Head, Holcim Philippines
**Subject:** Palm Kernel Shell Supply for La Union Facility
Hi, ECONARES here regarding PKS supply. Working with Indonesian producers on 4,200+ kcal/kg material. Happy to share specs and sample proposal. Are you the right person for alternative fuels?
- Fraser, ECONARES

### Republic Cement (HIGH)
**To:** Supply Chain Head, Republic Cement
**Subject:** PKS Supply Inquiry - Rizal Facility
Hi, regarding PKS supply for your Bulatao facility. 4,200+ kcal/kg material from Indonesia. Your sustainability focus makes PKS a good fit. Happy to share details. Exploring alternative fuels?
- Fraser, ECONARES

### Northern Cement (HIGH)
**To:** Procurement Director, Northern Cement
**Subject:** Palm Kernel Shell Supply - Pangasinan
Hi, regarding PKS supply for Northern Cement. 4,000-4,500 kcal/kg material, good logistics to Northern Luzon ports. Happy to share specs and pricing. Right person for alternative fuels?
- Fraser, ECONARES

---

## COAL PLANT OUTREACH

### Sual Coal Plant (HIGH - 1200 MW)
**To:** Fuel Manager, Sual Coal Plant
**Subject:** PKS Co-firing Opportunity - Sual Facility
Hi, regarding PKS for your Sual facility. 4,200+ kcal/kg material, logistics to Northern Luzon. 10-20pct blend helps sustainability targets. Happy to share specs and trial proposal. Right person for fuel procurement?
- Fraser, ECONARES

### Masinloc Coal Plant (HIGH - 900 MW)
**To:** Fuel Procurement, Masinloc Coal Plant
**Subject:** Palm Kernel Shell Supply - Masinloc
Hi, regarding PKS supply for Masinloc. 4,000-4,500 kcal/kg material, logistics through Subic or Manila. Evaluating biomass blending options?
- Fraser, ECONARES

---

## OUTREACH TRACKING
| Company | Type | Potential | Status |
|---------|------|-----------|--------|
| Holcim Philippines | Cement | HIGH | NOT CONTACTED |
| Republic Cement | Cement | HIGH | NOT CONTACTED |
| Northern Cement | Cement | HIGH | NOT CONTACTED |
| Sual Coal Plant | Coal | HIGH | NOT CONTACTED |
| Masinloc Coal Plant | Coal | HIGH | NOT CONTACTED |
| Cemex Philippines | Cement | MEDIUM | NOT CONTACTED |
| Mindanao Cement | Cement | MEDIUM | NOT CONTACTED |
| Santa Cruz Coal Plant | Coal | MEDIUM | NOT CONTACTED |
| Pagbilao Coal Plant | Coal | MEDIUM | NOT CONTACTED |
| Deductaca Coal Plant | Coal | MEDIUM | NOT CONTACTED |

---
Generated: {date}
"""

def ensure_dirs():
    os.makedirs(OUTREACH_DIR, exist_ok=True)

def generate_pks_outreach_file() -> str:
    ensure_dirs()
    content = OUTREACH_TEMPLATE.format(date=datetime.now().strftime("%Y-%m-%d"))
    with open(PKS_OUTREACH_FILE, 'w') as f:
        f.write(content)
    return PKS_OUTREACH_FILE

def get_high_priority_targets() -> List[Dict]:
    targets = []
    for name, info in CEMENT_PLANTS.items():
        if info.get("pks_potential") == "high":
            targets.append({"company": name, "type": "cement", "location": info.get("location"), "contact": info.get("procurement_contact"), "potential": "HIGH"})
    for name, info in COAL_PLANTS.items():
        if info.get("pks_potential") == "high":
            targets.append({"company": name, "type": "coal", "location": info.get("location"), "capacity": info.get("capacity_mw"), "contact": info.get("procurement_contact"), "potential": "HIGH"})
    return targets

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ECONARES PKS")
    parser.add_argument("--status", action="store_true", help="Show summary")
    parser.add_argument("--generate", action="store_true", help="Generate file")
    parser.add_argument("--high-priority", action="store_true", help="Show high priority")
    args = parser.parse_args()
    if args.status:
        print("=== PKS MARKET ===")
        for name, info in CEMENT_PLANTS.items():
            print(f"  [{info.get('pks_potential', 'medium').upper()}] {name}")
        for name, info in COAL_PLANTS.items():
            print(f"  [{info.get('pks_potential', 'medium').upper()}] {name} {info.get('capacity_mw')}MW")
    elif args.generate:
        filepath = generate_pks_outreach_file()
        print(f"Generated: {filepath}")
    elif args.high_priority:
        for t in get_high_priority_targets():
            print(f"{t['company']} ({t['type']}) - {t['location']}")
    else:
        parser.print_help()
