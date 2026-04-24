# Email Intelligence SOP — ECONARES Trading Operations

**Purpose:** Systematically parse Gmail for leads, buyer responses, and deal signals across nickel, coal, diesel, PKS, and copper.

**Created:** April 18, 2026
**Last Updated:** April 20, 2026

---

## GMAIL SEARCH QUERIES (by Commodity)

Run these in Gmail search bar. Combine with `from:` or `to:` for specificity.

### Nickel Ore
```
nickel ore from:hubspot.com
nickel limonite OR nickel ore -news
tsingshan OR "stainless steel" nickel
```

### Diesel / Fuel Products
```
diesel from:hubspot.com
fuel oil OR diesel inquiry
cement plant diesel
energy crisis Philippines diesel
```

### Coal
```
coal from:hubspot.com
thermal coal OR steam coal
coal CIF OR FOB
```

### PKS (Palm Kernel Shells)
```
PKS from:hubspot.com
"palm kernel" OR PKS biomass
biomass energy Philippines
```

### Copper
```
copper ore from:hubspot.com
copper concentrate OR copper CIF
JX Advanced Metals
```

---

## LEAD RESPONSE PRIORITY MATRIX

| Priority | Signal | Action |
|----------|--------|--------|
| 🔴 High | Bounce/backlog notification | Find alternate contact, retry same day |
| 🟠 Urgent | Warm lead reply, specs requested | Call/WhatsApp within 2 hours |
| 🟡 Active | LOI received | Review terms, escalate to CEO |
| 🟢 Follow-up | Initial outreach sent | Auto-follow-up in 5 days |
| ⚪ Monitor | Market inquiry, no specs | Log in HubSpot, Nurture sequence |

---

## THIS WEEK'S KEY EMAIL EVENTS (Apr 14-20, 2026)

### Tsingshan — NICKEL ORE (HIGH PRIORITY — BOUNCE)
- **Sent to:** jason@tsingshan-steels.com
- **Subject:** Nickel Ore Supply Inquiry — ECONARES
- **Status:** DELIVERY FAILED
- **Action Required:** Verify alternate Tsingshan contact. Try procurement@tsingshan-steels.com or search LinkedIn for Tsingshan sourcing team.

### CEDC (Cebu Energy Development Corp) — DIESEL (WARM LEAD)
- **Contact:** Joy Desuyo (consultant)
- **Signal:** Expressed interest during energy crisis period
- **HubSpot Contact ID:** 464524163823
- **Action:** Follow up this week — leverage regional fuel volatility narrative

### Toledo Power Corp — DIESEL
- **Contact:** Via Joy Desuyo
- **Status:** Warm, linked to CEDC opportunity

### Republic Cement / Goodfound / Mabuhay — DIESEL
- **All in Negotiation stage (HubSpot)**
- **Combined pipeline:** $1.8M
- **Close date:** May 15, 2026

---

## GMAIL LABEL SYSTEM (Recommended)

Create Gmail labels matching this hierarchy:

### By Commodity
- Coal
- Diesel / Fuel Products
- Nickel Ore
- Copper Ore / Concentrates
- PKS (Palm Kernel Shells)

### By Deal Stage
- Lead / Prospecting
- Price Quote / Proposal
- Negotiation
- Deal Confirmed / Closed
- Lost / Declined

### By Counterparty Type
- Buyers
- Suppliers / Producers
- Vessels / Logistics
- Offtakers

### By Region/Regulator
- Philippines / Domestic (DENR/MGB)
- China
- Japan
- Indonesia

### Color Coding
- 🔴 Red: Urgent / High Value Deal
- 🟠 Orange: Active Negotiation
- 🟡 Yellow: Follow-up Required
- 🟢 Green: Deal Confirmed
- ⚪ Gray: Archive / Inactive

---

## AUTOMATION RULES

### Auto-label from HubSpot
```
Matches: from:hubspot.com
Apply label: [Commodity] + [Stage]
```

### Auto-label DENR/MGB mentions
```
Matches: MGB OR DENR OR "Mines and Geosciences"
Apply label: Philippines / Domestic
Star: Yes (flag for review)
```

### Bounced emails — Urgent flag
```
Matches: "Delivery Failed" OR "bounce" OR "undeliverable"
Apply label: 🔴 URGENT
Star: Yes
```

---

## NOTES

- Emails to DENR/MGB compliance details are OMITTED from first contact outreach (per ECONARES directive).
- Always review HubSpot deal stage before sending price-specific replies.
- Never reveal price in first reply — gather buyer requirements (specs, volume, logistics) first.

---

*ECONARES Trading Operations | Version 1.0 | April 2026*
