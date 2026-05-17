#!/usr/bin/env python3
"""ECONARES SMS/WhatsApp Outreach Script - Phase 5"""

import openpyxl
from datetime import datetime

XLSX = "/home/mauiclaw/Documents/Obsidian Vault/ECONARES SALES and MARKETING UPDATES-RZH May ENRICHED.xlsx"
OUT = "/home/mauiclaw/ECONARES_WORKSPACE/scripts/sms_outreach_output.txt"

def load_contacts():
    try:
        wb = openpyxl.load_workbook(XLSX, data_only=True)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        contacts = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0]:
                contacts.append(dict(zip(headers, row)))
        print(f"[OK] Loaded {len(contacts)} contacts")
        return contacts, headers
    except Exception as e:
        print(f"[ERROR] {e}")
        return [], []

def find_col(headers, kw_list):
    for i, h in enumerate(headers):
        if h and any(k in str(h).lower() for k in kw_list):
            return i
    return None

def filter_phone_only(contacts, headers):
    nc = find_col(headers, ['name'])
    cc = find_col(headers, ['company', 'entity'])
    pc = find_col(headers, ['phone', 'mobile', 'tel'])
    ec = find_col(headers, ['email', 'mail'])
    mc = find_col(headers, ['commodity', 'product'])
    sc = find_col(headers, ['status', 'tier', 'category'])
    oc = find_col(headers, ['source', 'origin'])

    result = []
    for row in contacts:
        phone = row[pc] if pc is not None else None
        if not phone:
            continue
        email = row[ec] if ec is not None else None
        if email and '@' in str(email):
            continue
        status = row[sc] if sc is not None else None
        tier = "COLD"
        if status:
            s = str(status).upper()
            if 'HOT' in s: tier = "HOT"
            elif 'TOP' in s: tier = "TOP"
        result.append({
            'name': row[nc] or 'Unknown',
            'company': row[cc] or 'Unknown',
            'phone': phone,
            'commodity': row[mc] or 'commodities',
            'tier': tier,
            'source': row[oc] or 'Unknown'
        })
    return result

def fmt_phone(p):
    d = ''.join(c for c in str(p).strip() if c.isdigit() or c == '+')
    if not d.startswith('+'):
        d = '+63' + d.lstrip('0') if d.startswith('0') else ('+' + d if d.startswith('63') else '+63' + d)
    return d

def gen_msg(c):
    name = str(c['name']).split()[0]
    comm = c['commodity'] or 'commodities'
    key = 'coal'
    for k in ['coal', 'nickel', 'diesel', 'pks', 'copper']:
        if k in comm.lower():
            key = {'nickel': 'nickel ore', 'pks': 'PKS (palm kernel shell)'}.get(k, k)
            break
    import hashlib
    tmpl = [
        f"Hi {name}, this is Reymarr from ECONARES -- we supply {key} to PH plants. Do you currently have a fixed supplier, or are you open to exploring options?",
        f"Hi {name}, Reymarr from ECONARES here. We deliver {key} to factories in PH -- are you currently locked into a supplier contract?",
        f"Hi {name}, ECONARES team here. We supply {key} to Philippine plants. Are you open to checking other options for your procurement?"
    ]
    return tmpl[int(hashlib.md5(c['name'].encode()).hexdigest(), 16) % len(tmpl)]

def main():
    print("=" * 60)
    print("ECONARES SMS/WHATSAPP OUTREACH")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    contacts, headers = load_contacts()
    if not contacts:
        print("[ERROR] No contacts"); return
    pc = filter_phone_only(contacts, headers)
    print(f"[INFO] {len(pc)} phone-only contacts (no email)")
    hot = [c for c in pc if c['tier'] == 'HOT']
    top = [c for c in pc if c['tier'] == 'TOP']
    other = [c for c in pc if c['tier'] == 'COLD']
    lines = ["="*60, "ECONARES SMS/WHATSAPP MESSAGES", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", f"Total: {len(pc)}", "="*60, ""]
    def add_section(title, lst):
        if not lst: return
        lines.extend(["\n" + "="*40, f"  {title} ({len(lst)})", "="*40])
        for i, c in enumerate(lst, 1):
            msg = gen_msg(c)
            wa = f"https://wa.me/{fmt_phone(c['phone']).replace('+','')}"
            lines.extend([f"\n--- #{i} ---", f"Name: {c['name']}", f"Company: {c['company']}", f"Phone: {fmt_phone(c['phone'])}", f"Source: {c['source']}", f"Comm: {c['commodity']}", f"WA: {wa}", "", f"Msg: {msg}", f"Len: {len(msg)}chars"])
    if hot: add_section("HOT", hot)
    if top: add_section("TOP", top)
    if other: add_section("OTHER", other)
    lines.extend(["", "="*60, "SUMMARY", "="*60, f"HOT: {len(hot)}", f"TOP: {len(top)}", f"Other: {len(other)}", f"TOTAL: {len(pc)}"])
    with open(OUT, 'w') as f: f.write("\n".join(lines))
    print(f"[OK] Wrote {OUT}")
    print(f"[OK] {len(pc)} messages")
    print("\n--- PREVIEW ---")
    for c in pc[:5]:
        print(f"To: {c['name']} | Msg: {gen_msg(c)}")
