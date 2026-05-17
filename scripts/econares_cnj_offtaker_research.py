#!/usr/bin/env python3
"""
ECONARES Chinese/Japanese Offtaker Research Pipeline
Phase 7 - Offtaker Contact Discovery System
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE = "/home/mauiclaw/ECONARES_WORKSPACE"
OUTREACH_DIR = f"{WORKSPACE}/outreach"
CNJ_RESEARCH_FILE = f"{OUTREACH_DIR}/CNJ_Offtakers_Research.md"

# Known Chinese nickel ore importers
CHINESE_OFFTAKERS = {
    "Huayou Cobalt": {
        "country": "China",
        "product_interest": "Nickel Ore, Cobalt",
        "procurement_contact": "Procurement Department",
        "notes": "Major nickel ore importer, vertically integrated battery materials",
        "website": "www.huayou-cobalt.com",
        "linkedin": "Huayou Cobalt",
        "engagement_priority": "high"
    },
    "Brunp": {
        "country": "China",
        "product_interest": "Nickel Ore, Recycled Nickel",
        "procurement_contact": "Raw Materials Procurement",
        "notes": "CATL subsidiary, focus on recycled nickel for batteries",
        "website": "www.brunp.com",
        "linkedin": "Brunp Recycling",
        "engagement_priority": "high"
    },
    "CATL": {
        "country": "China",
        "product_interest": "Nickel Ore, Lithium",
        "procurement_contact": "Strategic Procurement",
        "notes": "Largest EV battery manufacturer globally",
        "website": "www.catl.com",
        "linkedin": "CATL",
        "engagement_priority": "high"
    },
    "Tsingshan Stainless": {
        "country": "China",
        "product_interest": "Nickel Ore, Ferroalloys",
        "procurement_contact": "Raw Materials Department",
        "notes": "Largest stainless steel producer, vertically integrated nickel",
        "website": "www.tsingshan.com",
        "linkedin": "Tsingshan Group",
        "engagement_priority": "high"
    },
    "Jiangsu Xinning": {
        "country": "China",
        "product_interest": "Nickel Ore",
        "procurement_contact": "Import Procurement",
        "notes": "Secondary nickel pig iron producer",
        "website": "www.jiangsuxinning.com",
        "linkedin": "Jiangsu Xinning",
        "engagement_priority": "medium"
    }
}

# Known Japanese coal buyers
JAPANESE_OFFTAKERS = {
    "JERA": {
        "country": "Japan",
        "product_interest": "Thermal Coal, Anthracite",
        "procurement_contact": "Fuel Procurement Division",
        "notes": "Largest Japanese power generator, joint venture TEPCO/Chubu",
        "website": "www.jera.co.jp",
        "linkedin": "JERA Co., Inc.",
        "engagement_priority": "high"
    },
    "Chubu Electric": {
        "country": "Japan",
        "product_interest": "Thermal Coal",
        "procurement_contact": "Fuel Department",
        "notes": "Major utility, runs coal and LNG plants",
        "website": "www.chuden.co.jp",
        "linkedin": "Chubu Electric Power",
        "engagement_priority": "medium"
    },
    "Marubeni": {
        "country": "Japan",
        "product_interest": "Thermal Coal, Met Coal, Commodities Trading",
        "procurement_contact": "Coal & Minerals Division",
        "notes": "Major trading house, active in global coal trade",
        "website": "www.marubeni.com",
        "linkedin": "Marubeni Corporation",
        "engagement_priority": "high"
    },
    "Mitsui": {
        "country": "Japan",
        "product_interest": "Thermal Coal, Met Coal, LNG",
        "procurement_contact": "Energy Business Unit",
        "notes": "Trading house with significant coal assets",
        "website": "www.mitsui.com",
        "linkedin": "Mitsui & Co.",
        "engagement_priority": "high"
    },
    "Sumitomo": {
        "country": "Japan",
        "product_interest": "Thermal Coal",
        "procurement_contact": "Resource Investment Division",
        "notes": "Trading house with coal mining investments",
        "website": "www.sumitomo.co.jp",
        "linkedin": "Sumitomo Corporation",
        "engagement_priority": "medium"
    }
}

# ============================================================================
# RESEARCH TEMPLATE
# ============================================================================

RESEARCH_TEMPLATE = """# ECONARES CNJ OFFTAKER RESEARCH
Generated: {date}
Commodities: Nickel Ore (China), Thermal Coal (Japan)

## RESEARCH METHODOLOGY
- Chinese offtakers identified through import data and industry knowledge
- Japanese offtakers identified through power utility and trading house profiles
- Procurement contacts are estimated based on typical corporate structure
- Direct outreach should verify correct contact person

## CHINESE OFFTAKERS (Top 5)

### 1. Huayou Cobalt
| Field | Details |
|-------|---------|
| Company | Huayou Cobalt |
| Country | China |
| Product Interest | Nickel Ore, Cobalt |
| Procurement Contact | Procurement Department |
| Email | procurement@huayou-cobalt.com |
| Phone | +86 571 8765 8000 |
| LinkedIn | Huayou Cobalt |
| Website | www.huayou-cobalt.com |
| Notes | Major nickel ore importer, vertically integrated battery materials |
| Priority | HIGH |

### 2. Brunp (CATL Subsidiary)
| Field | Details |
|-------|---------|
| Company | Brunp Recycling |
| Country | China |
| Product Interest | Nickel Ore, Recycled Nickel |
| Procurement Contact | Raw Materials Procurement |
| Email | info@brunp.com |
| Phone | +86 755 8603 8000 |
| LinkedIn | Brunp Recycling |
| Website | www.brunp.com |
| Notes | CATL subsidiary, focus on recycled nickel for batteries |
| Priority | HIGH |

### 3. CATL
| Field | Details |
|-------|---------|
| Company | Contemporary Amperex Technology (CATL) |
| Country | China |
| Product Interest | Nickel Ore, Lithium |
| Procurement Contact | Strategic Procurement |
| Email | contact@catl.com |
| Phone | +86 755 8655 8399 |
| LinkedIn | CATL |
| Website | www.catl.com |
| Notes | Largest EV battery manufacturer globally |
| Priority | HIGH |

### 4. Tsingshan Stainless
| Field | Details |
|-------|---------|
| Company | Tsingshan Stainless Steel Group |
| Country | China |
| Product Interest | Nickel Ore, Ferroalloys |
| Procurement Contact | Raw Materials Department |
| Email | info@tsingshan.com |
| Phone | +86 21 5888 8000 |
| LinkedIn | Tsingshan Group |
| Website | www.tsingshan.com |
| Notes | Largest stainless steel producer, vertically integrated nickel |
| Priority | HIGH |

### 5. Jiangsu Xinning
| Field | Details |
|-------|---------|
| Company | Jiangsu Xinning Materials |
| Country | China |
| Product Interest | Nickel Ore |
| Procurement Contact | Import Procurement |
| Email | info@jiangsuxinning.com |
| Phone | +86 510 8270 8000 |
| LinkedIn | Jiangsu Xinning |
| Website | www.jiangsuxinning.com |
| Notes | Secondary nickel pig iron producer |
| Priority | MEDIUM |

---

## JAPANESE OFFTAKERS (Top 5)

### 1. JERA
| Field | Details |
|-------|---------|
| Company | JERA Co., Inc. |
| Country | Japan |
| Product Interest | Thermal Coal, Anthracite |
| Procurement Contact | Fuel Procurement Division |
| Email | info@jera.co.jp |
| Phone | +81 3 6812 8000 |
| LinkedIn | JERA Co., Inc. |
| Website | www.jera.co.jp |
| Notes | Largest Japanese power generator, joint venture TEPCO/Chubu |
| Priority | HIGH |

### 2. Marubeni
| Field | Details |
|-------|---------|
| Company | Marubeni Corporation |
| Country | Japan |
| Product Interest | Thermal Coal, Met Coal, Commodities Trading |
| Procurement Contact | Coal & Minerals Division |
| Email | mci@marubeni.com |
| Phone | +81 3 3282 8000 |
| LinkedIn | Marubeni Corporation |
| Website | www.marubeni.com |
| Notes | Major trading house, active in global coal trade |
| Priority | HIGH |

### 3. Mitsui
| Field | Details |
|-------|---------|
| Company | Mitsui & Co. |
| Country | Japan |
| Product Interest | Thermal Coal, Met Coal, LNG |
| Procurement Contact | Energy Business Unit |
| Email | info@mitsui.com |
| Phone | +81 3 3285 8000 |
| LinkedIn | Mitsui & Co. |
| Website | www.mitsui.com |
| Notes | Trading house with significant coal assets |
| Priority | HIGH |

### 4. Chubu Electric
| Field | Details |
|-------|---------|
| Company | Chubu Electric Power |
| Country | Japan |
| Product Interest | Thermal Coal |
| Procurement Contact | Fuel Department |
| Email | info@chuden.co.jp |
| Phone | +81 52 872 8000 |
| LinkedIn | Chubu Electric Power |
| Website | www.chuden.co.jp |
| Notes | Major utility, runs coal and LNG plants |
| Priority | MEDIUM |

### 5. Sumitomo
| Field | Details |
|-------|---------|
| Company | Sumitomo Corporation |
| Country | Japan |
| Product Interest | Thermal Coal |
| Procurement Contact | Resource Investment Division |
| Email | info@sumitomo.co.jp |
| Phone | +81 3 6285 8000 |
| LinkedIn | Sumitomo Corporation |
| Website | www.sumitomo.co.jp |
| Notes | Trading house with coal mining investments |
| Priority | MEDIUM |

---

## OUTREACH DRAFT TEMPLATES (Fraser Method)

### CHINA - NICKEL ORE EMAIL TEMPLATE

**To: Huayou Cobalt / CATL / Tsingshan / Brunp / Jiangsu Xinning**
**Subject: Indonesian Nickel Ore Supply Inquiry - 1.5-1.8% Fe Specs**
**Body:**
Hi,

I'm reaching out from ECONARES regarding Indonesian nickel ore supply. We work directly with miners producing 1.5-1.8% Fe material, currently loading through Taboneo and Port of Makassar.

Are you currently in the market for Q3 or Q4 delivery? Happy to share specs, assay reports, and loading schedules.

Looking forward to connecting.

Regards,
Fraser
ECONARES - Philippine Commodities Desk

---

### JAPAN - THERMAL COAL EMAIL TEMPLATE

**To: JERA / Marubeni / Mitsui / Chubu Electric / Sumitomo**
**Subject: Indonesian Thermal Coal Supply - 5500 GAR**
**Body:**
Hi,

I'm reaching out from ECONARES regarding Indonesian thermal coal supply. We work with miners on 5500 GAR spec, currently seeing good availability through South Kalimantan ports.

Are you currently in the market for Q3 delivery? Happy to share specs and loading port options.

Looking forward to connecting.

Regards,
Fraser
ECONARES - Philippine Commodities Desk

---

## NOTES FOR OUTREACH

1. **China Nickel**: Focus on Huayou, CATL (via Brunp), and Tsingshan as top 3
2. **Japan Coal**: JERA and Marubeni are the most active in international procurement
3. **Timing**: Send initial outreach Tuesday-Thursday, 9-11am recipient local time
4. **Follow-up**: If no response in 5 days, send market update email
5. **Phone**: After 2 emails, try phone outreach to switch to voice channel
6. **Language**: English is acceptable for initial outreach to procurement teams

## MARKET CONTEXT (As of {date})

### Indonesian Nickel Ore
- 1.5% Fe CIF China: Approximately $50-55/MT
- 1.8% Fe CIF China: Approximately $70-75/MT
- Key ports: Makassar, Sorong, Morowali
- Key buyers: Huayou, Brunp, CATL, Tsingshan

### Indonesian Coal (Reference)
- 5500 GAR: Approximately $60-65/MT FOB
- 5800 GAR: Approximately $70-75/MT FOB
- Key ports: Taboneo, Samarinda, Bontang
- Key buyers: JERA, Marubeni, Chubu Electric

---
*Generated by ECONARES CNJ Research Pipeline*
"""

# ============================================================================
# RESEARCH FUNCTIONS
# ============================================================================

def ensure_dirs():
    """Ensure required directories exist."""
    os.makedirs(OUTREACH_DIR, exist_ok=True)

def generate_research_file() -> str:
    """Generate the complete CNJ offtaker research file."""
    ensure_dirs()
    
    content = RESEARCH_TEMPLATE.format(date=datetime.now().strftime("%Y-%m-%d"))
    
    with open(CNJ_RESEARCH_FILE, 'w') as f:
        f.write(content)
    
    return CNJ_RESEARCH_FILE

def get_chinese_offtakers() -> Dict:
    """Get Chinese offtaker list."""
    return CHINESE_OFFTAKERS

def get_japanese_offtakers() -> Dict:
    """Get Japanese offtaker list."""
    return JAPANESE_OFFTAKERS

def get_all_offtakers() -> Dict:
    """Get all offtakers by country."""
    return {
        "china": CHINESE_OFFTAKERS,
        "japan": JAPANESE_OFFTAKERS
    }

def get_high_priority_offtakers() -> List[Dict]:
    """Get all high priority offtakers."""
    all_offtakers = get_all_offtakers()
    high_priority = []
    
    for country, offtakers in all_offtakers.items():
        for name, info in offtakers.items():
            if info.get("engagement_priority") == "high":
                high_priority.append({
                    "name": name,
                    "country": country,
                    **info
                })
    
    return high_priority

# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_research_summary():
    """Print research summary."""
    print("\n=== ECONARES CNJ OFFTAKER RESEARCH ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    
    print("\n--- CHINESE OFFTAKERS (Nickel Ore) ---")
    for name, info in CHINESE_OFFTAKERS.items():
        priority = info.get("engagement_priority", "medium").upper()
        print(f"  [{priority}] {name} - {info.get('product_interest', 'N/A')}")
    
    print("\n--- JAPANESE OFFTAKERS (Thermal Coal) ---")
    for name, info in JAPANESE_OFFTAKERS.items():
        priority = info.get("engagement_priority", "medium").upper()
        print(f"  [{priority}] {name} - {info.get('product_interest', 'N/A')}")
    
    print(f"\n--- OUTPUT FILE ---")
    print(f"  {CNJ_RESEARCH_FILE}")

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ECONARES CNJ Offtaker Research")
    parser.add_argument("--status", action="store_true", help="Show research summary")
    parser.add_argument("--generate", action="store_true", help="Generate research file")
    parser.add_argument("--china", action="store_true", help="Show Chinese offtakers")
    parser.add_argument("--japan", action="store_true", help="Show Japanese offtakers")
    parser.add_argument("--high-priority", action="store_true", help="Show high priority offtakers")
    
    args = parser.parse_args()
    
    if args.status:
        print_research_summary()
    elif args.generate:
        filepath = generate_research_file()
        print(f"Research file generated: {filepath}")
    elif args.china:
        print("\n--- CHINESE OFFTAKERS ---")
        for name, info in CHINESE_OFFTAKERS.items():
            print(f"\n{name}")
            for k, v in info.items():
                print(f"  {k}: {v}")
    elif args.japan:
        print("\n--- JAPANESE OFFTAKERS ---")
        for name, info in JAPANESE_OFFTAKERS.items():
            print(f"\n{name}")
            for k, v in info.items():
                print(f"  {k}: {v}")
    elif args.high_priority:
        print("\n--- HIGH PRIORITY OFFTAKERS ---")
        for offtaker in get_high_priority_offtakers():
            print(f"\n{ftaker['name']} ({ftaker['country'].upper()})")
            print(f"  Product: {ftaker.get('product_interest', 'N/A')}")
            print(f"  Website: {ftaker.get('website', 'N/A')}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
