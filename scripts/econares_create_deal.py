#!/usr/bin/env python3
"""ECONARES Obsidian Deal Creation Script - Phase 6"""
import sys, os, re
from datetime import datetime

DEALS_DIR = "/home/mauiclaw/Documents/Obsidian Vault/DEALS"
TEMPLATE_FILE = "/home/mauiclaw/Documents/Obsidian Vault/DEALS/DEAL_TEMPLATE.md"
INDEX_FILE = "/home/mauiclaw/Documents/Obsidian Vault/DEALS/DEALS_INDEX.md"

TEMPLATE_CONTENT = """---
created: {created}
status: LEAD
commodity:
company:
contact_name:
contact_phone:
contact_email:
estimated_value:
pipeline:
tags: [econares, deal]
---

# Deal: {company}

## Buyer Info
- **Company:** {company}
- **Contact:** {contact_name}
- **Phone:** {contact_phone}
- **Email:** {contact_email}

## Requirements
- **Commodity:** {commodity}
- **Volume:**
- **Quality specs:**
- **Delivery location:**
- **Target price:**
- **Timeline:**

## Price History
| Date | Price | Notes |
|------|-------|-------|
| {date} | | Initial quote |

## Contact Log
| Date | Type | Notes |
|------|------|-------|
| {date} | Created | Deal opened |

## Negotiation Notes


## Key Terms
- **Payment terms:**
- **Delivery terms:**
- **Inspection:**
- **Penalties:**

## Next Steps
- [ ] Initial contact
- [ ] Qualify requirements
- [ ] Submit quote
- [ ] Follow up
- [ ] Negotiate
- [ ] Close

---
*ECONARES Deal Tracker*
"""

def ensure_deals_dir():
    if not os.path.exists(DEALS_DIR):
        os.makedirs(DEALS_DIR)
        print(f"[OK] Created directory: {DEALS_DIR}")

def create_deal(company, commodity="", contact_name="", contact_phone="", contact_email="", estimated_value=""):
    ensure_deals_dir()
    # Sanitize company name for filename
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', company.lower()).strip('_')
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{safe_name}_{timestamp}.md"
    filepath = os.path.join(DEALS_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"[WARN] Deal already exists: {filepath}")
        return filepath
    
    now = datetime.now().strftime("%Y-%m-%d")
    content = TEMPLATE_CONTENT.format(
        created=now,
        date=now,
        company=company,
        contact_name=contact_name or "",
        contact_phone=contact_phone or "",
        contact_email=contact_email or "",
        commodity=commodity or "",
        estimated_value=estimated_value or ""
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"[OK] Created deal: {filepath}")
    update_index()
    return filepath

def update_index():
    """Update the deals index file."""
    files = sorted([f for f in os.listdir(DEALS_DIR) if f.endswith('.md') and f != 'DEALS_INDEX.md' and f != 'DEAL_TEMPLATE.md'])
    
    lines = [
        "# ECONARES Deals Index",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        f"Total deals: {len(files)}",
        "",
        "---",
        ""
    ]
    
    for f in files:
        filepath = os.path.join(DEALS_DIR, f)
        with open(filepath, 'r') as fp:
            content = fp.read()
        
        # Extract company name from first H1
        company = f.replace('.md', '').replace('_', ' ').title()
        m = re.search(r'^# Deal: (.+)$', content, re.MULTILINE)
        if m:
            company = m.group(1)
        
        # Extract status
        status = "LEAD"
        m = re.search(r'^status: (\w+)$', content, re.MULTILINE)
        if m:
            status = m.group(1)
        
        # Extract commodity
        commodity = ""
        m = re.search(r'^commodity: ?(.+)$', content, re.MULTILINE)
        if m:
            commodity = m.group(1).strip()
        
        link = f"./{f}"
        lines.append(f"- [[{link}|{company}]] -- {status} -- {commodity}")
    
    with open(INDEX_FILE, 'w') as fp:
        fp.write("\n".join(lines))
    
    print(f"[OK] Updated index: {INDEX_FILE}")

def main():
    if len(sys.argv) > 1:
        company = sys.argv[1]
        commodity = sys.argv[2] if len(sys.argv) > 2 else ""
        contact_name = sys.argv[3] if len(sys.argv) > 3 else ""
        contact_phone = sys.argv[4] if len(sys.argv) > 4 else ""
        contact_email = sys.argv[5] if len(sys.argv) > 5 else ""
        estimated_value = sys.argv[6] if len(sys.argv) > 6 else ""
        create_deal(company, commodity, contact_name, contact_phone, contact_email, estimated_value)
    else:
        print("ECONARES Deal Creator")
        print("Usage: python econares_create_deal.py <company> [commodity] [contact_name] [phone] [email] [est_value]")
        print("")
        print("Example: python econares_create_deal.py 'Apex Cement Corp' 'Coal' 'Juan dela Cruz' '+639123456789' 'juan@apex.com' '5000000'")
        print("")
        print("This creates a new deal notebook in:")
        print(f"  {DEALS_DIR}")

if __name__ == "__main__":
    main()
