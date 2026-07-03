"""
EMAIL 1 of 5 — Zhejiang Huayou Cobalt
To: Qi Sun (xct@huayou.com) — Procurement
CC: Hongliang Chen (CEO, information@huayou.com)
Subject: Philippine Nickel Ore Supply — HPAL-Grade Material for Your Consideration
"""

subject = "Philippine Nickel Ore Supply — HPAL-Grade Material for Your Consideration"
to_name = "Mr. Qi Sun"
to_title = "Procurement"
to_company = "Zhejiang Huayou Cobalt Co., Ltd."
to_email = "xct@huayou.com"

body = f"""Dear {to_name},

My name is [YOUR NAME], and I represent ECONARES International Trading Corp. (rzh@econares.ph), a Philippine-based supplier of industrial fuels and minerals with direct access to nickel ore from Philippines mining operations.

I am writing to explore whether Zhejiang Huayou Cobalt has interest in sourcing Philippine nickel ore for your HPAL operations — particularly given your existing offtake relationships with Nickel Asia Corporation and CTP Nickel Corporation.

**What We Offer:**
- Origin: Philippines nickel ore (direct mine access)
- Grade: Typical HPAL-grade limonite ore; Mg:Si ratio suited for high-pressure acid leach feed
- Volume: [YOUR VOLUME] MT per month, with flexibility for incremental increases
- Incoterms: FOB Philippines ports / CIF [destination] / CFR [destination]
- Supply arrangement: Short-term spot and medium-term supply contracts

**Why ECONARES:**
We maintain direct relationships with Philippine nickel miners, allowing us to arrange consistent supply without layered intermediary markups. Our team monitors ore quality specifications closely and can provide assay results, logistics support, and sampling protocols aligned with your HPAL process requirements.

I would welcome the opportunity to arrange a brief call — 15 minutes — to discuss your current and projected feed requirements, specification needs, and how our supply capabilities might align with Zhejiang Huayou Cobalt's HPAL expansion plans.

Alternatively, if there is a more appropriate contact within your procurement team for nickel ore feed materials, I would be grateful for an introduction.

Please feel free to reply directly to this email or reach me at rzh@econares.ph or +63 9XX XXX XXXX.

Thank you for your time, {to_name}.

Best regards,

[YOUR FULL NAME]
Sales & Marketing
ECONARES International Trading Corp.
Email: rzh@econares.ph
Mobile: +63 9XX XXX XXXX
Website: www.econares.ph

---
Note: Our trade terms are FOB / CIF / CFR. We do not offer DAP arrangements.
"""

print("=" * 60)
print("EMAIL 1: ZHEJANG HUAYOU COBALT")
print("=" * 60)
print(f"To: {to_name} <{to_email}>")
print(f"Subject: {subject}")
print()
print(body)
print()
print("[SAVE AS DRAFT AND SEND FROM rzh@econares.ph]")
