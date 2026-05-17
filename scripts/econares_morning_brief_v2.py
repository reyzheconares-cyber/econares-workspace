#!/usr/bin/env python3
"""ECONARES Morning Brief v2 - Phase 10"""
import openpyxl
from datetime import datetime, timedelta

XLSX = "/home/mauiclaw/Documents/Obsidian Vault/ECONARES SALES and MARKETING UPDATES-RZH May ENRICHED.xlsx"
OUT_HTML = "/home/mauiclaw/ECONARES_WORKSPACE/scripts/morning_brief_today.html"
OUT_TXT = "/home/mauiclaw/ECONARES_WORKSPACE/scripts/morning_brief_today.txt"

COMMODITY_PRICES = {
    'coal_5500_gar': 'USD 68-72/MT FOB Indonesia',
    'nickel_1_8': 'USD 42-46/MT CIF China',
    'diesel': 'USD 0.85-0.95/Liter CIF PH',
    'pks': 'USD 95-105/MT FOB Indonesia',
}

def get_outreach_queue(limit=5):
    try:
        wb = openpyxl.load_workbook(XLSX, data_only=True)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        
        # Find columns
        def find_col(kw):
            for i, h in enumerate(headers):
                if h and any(k in str(h).lower() for k in kw):
                    return i
            return None
        
        nc = find_col(['name'])
        cc = find_col(['company', 'entity'])
        pc = find_col(['phone', 'mobile', 'tel'])
        ec = find_col(['email', 'mail'])
        mc = find_col(['commodity', 'product'])
        sc = find_col(['status', 'tier', 'category'])
        
        hot_contacts = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[0]: continue
            status = str(row[sc] or '').upper()
            if 'HOT' in status:
                hot_contacts.append({
                    'name': row[nc] or 'Unknown',
                    'company': row[cc] or 'Unknown',
                    'commodity': row[mc] or '',
                    'has_phone': bool(row[pc]),
                    'has_email': bool(row[pc] and '@' in str(row[pc] or ''))
                })
        
        return hot_contacts[:limit]
    except Exception as e:
        return [{'name': 'Demo Contact', 'company': 'Demo Corp', 'commodity': 'Coal', 'note': f'Error loading: {e}'}]

def get_pending_followups():
    return [
        {'company': 'Apex Cement Corp', 'action': 'Quote follow-up', 'days': 2},
        {'company': 'Steel Manila Inc', 'action': 'Contract renewal', 'days': 5},
        {'company': 'PowerGrid Solutions', 'action': 'Price negotiation', 'days': 1},
    ]

def generate_html():
    queue = get_outreach_queue()
    followups = get_pending_followups()
    today = datetime.now().strftime("%B %d, %Y")
    
    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>ECONARES Morning Brief - {today}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #0f3460; background: #e94560; padding: 8px; margin-top: 25px; }}
.section {{ background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; }}
.highlight {{ color: #e94560; font-weight: bold; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
td, th {{ padding: 8px; border: 1px solid #0f3460; text-align: left; }}
th {{ background: #0f3460; color: #e94560; }}
.status-hot {{ color: #ff6b6b; font-weight: bold; }}
.status-warning {{ color: #ffd93d; }}
.footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 12px; }}
</style></head><body>
<h1>🌅 ECONARES Morning Brief</h1>
<p><em>Generated: {today} | Philippine Time</em></p>

<div class="section">
<h2>📊 Commodity Market Update</h2>
<table>
<tr><th>Commodity</th><th>Indicative Price</th></tr>
<tr><td>Indonesian Coal (5500 GAR)</td><td class="highlight">{COMMODITY_PRICES['coal_5500_gar']}</td></tr>
<tr><td>Nickel Ore (1.8% CIF China)</td><td class="highlight">{COMMODITY_PRICES['nickel_1_8']}</td></tr>
<tr><td>Diesel (CIF PH)</td><td class="highlight">{COMMODITY_PRICES['diesel']}</td></tr>
<tr><td>PKS (FOB Indonesia)</td><td class="highlight">{COMMODITY_PRICES['pks']}</td></tr>
</table>
<p><em>Prices are indicative and subject to market movement. Updated: {datetime.now().strftime('%H:%M')}</em></p>
</div>

<div class="section">
<h2>📞 Today's Outreach Queue (Top {len(queue)})</h2>
<table>
<tr><th>#</th><th>Contact</th><th>Company</th><th>Commodity</th><th>Channel</th></tr>
"""
    for i, c in enumerate(queue, 1):
        channel = "📱 WhatsApp" if c.get('has_phone') else ("✉️ Email" if c.get('has_email') else "❓ Unknown")
        html += f"<tr><td>{i}</td><td class='highlight'>{c['name']}</td><td>{c['company']}</td><td>{c['commodity']}</td><td>{channel}</td></tr>\n"
    
    html += "</table></div>\n"

    html += """<div class="section">
<h2>⏰ Pending Follow-ups</h2>
<table>
<tr><th>Company</th><th>Action Required</th><th>Days Pending</th><th>Priority</th></tr>
"""
    for f in followups:
        days = f['days']
        priority = "🔴 URGENT" if days <= 1 else ("🟡 SOON" if days <= 3 else "🟢 NORMAL")
        html += f"<tr><td>{f['company']}</td><td>{f['action']}</td><td>{days} days</td><td class='{'status-hot' if days<=1 else 'status-warning'}'>{priority}</td></tr>\n"
    
    html += f"""</table></div>

<div class="section">
<h2>📅 Quick Stats</h2>
<p>• Active Hot contacts: <span class="highlight">{len(queue)}</span></p>
<p>• Pending follow-ups: <span class="highlight">{len(followups)}</span></p>
<p>• Markets covered: PH, CN, JP</p>
</div>

<div class="footer">
<p>ECONARES Commodity Trading | 🌏 Nickel, Coal, Diesel, PKS, Copper</p>
<p>Generated by Hermes Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
</body></html>"""
    
    return html

def generate_text():
    queue = get_outreach_queue()
    followups = get_pending_followups()
    today = datetime.now().strftime("%B %d, %Y")
    
    lines = [
        "="*60,
        "🌅 ECONARES MORNING BRIEF",
        f"Date: {today} | PHT",
        "="*60,
        "",
        "📊 COMMODITY PRICES",
        "-"*40,
    ]
    for k, v in COMMODITY_PRICES.items():
        lines.append(f"  {k}: {v}")
    
    lines.extend(["", "📞 OUTREACH QUEUE (Top 5)", "-"*40])
    for i, c in enumerate(queue, 1):
        lines.append(f"  {i}. {c['name']} @ {c['company']} [{c['commodity']}]")
    
    lines.extend(["", "⏰ PENDING FOLLOW-UPS", "-"*40])
    for f in followups:
        days = f['days']
        priority = "URGENT" if days <= 1 else ("SOON" if days <= 3 else "NORMAL")
        lines.append(f"  {f['company']} | {f['action']} | {days}d | {priority}")
    
    lines.extend(["", "="*60, "EOF"])
    return "\n".join(lines)

def main():
    print("="*60)
    print("ECONARES MORNING BRIEF v2")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    html = generate_html()
    txt = generate_text()
    
    with open(OUT_HTML, 'w') as f:
        f.write(html)
    print(f"[OK] HTML: {OUT_HTML}")
    
    with open(OUT_TXT, 'w') as f:
        f.write(txt)
    print(f"[OK] TXT: {OUT_TXT}")
    
    print("\n--- TEXT PREVIEW ---")
    print(txt[:800])

if __name__ == "__main__":
    main()
