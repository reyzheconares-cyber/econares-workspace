# Gmail Label Strategy — Commodity Trading Inbox System

**Purpose:** Organize ECONARES Gmail for fast deal signal detection across commodities.

---

## RECOMMENDED LABEL HIERARCHY (Flat Structure)

Use flat labels with compound names (e.g., `Coal - Price Quote`) for speed. No nested labels.

### Commodity Labels
```
Coal
Diesel / Fuel Products
Nickel Ore
Copper Ore / Concentrates
PKS (Palm Kernel Shells)
```

### Stage Labels
```
Lead / Prospecting
Price Quote / Proposal
Negotiation
Deal Confirmed / Closed
Lost / Declined
```

### Counterparty Type Labels
```
Buyers
Suppliers / Producers
Vessels / Logistics
Offtakers
```

### Region / Regulatory Labels
```
Philippines / Domestic
China
Japan
Indonesia
```

---

## COLOR CODING

| Color | Meaning | Example |
|-------|---------|---------|
| 🔴 Red | Urgent / High Value | Bounced emails, escalated deals |
| 🟠 Orange | Active Negotiation | LOI received, terms under review |
| 🟡 Yellow | Follow-up Required | No reply in 5 days |
| 🟢 Green | Deal Confirmed | Signed, ready to execute |
| ⚪ Gray | Archive / Inactive | Lost deals, old leads |

---

## KEY FILTER RULES

### Filter 1: HubSpot leads by commodity
```
Matches: from:hubspot.com nickel
Apply: Nickel Ore | [Check Stage]
```

### Filter 2: DENR/MGB compliance mentions
```
Matches: MGB OR DENR OR "Mines and Geosciences"
Apply: Philippines / Domestic
Star: Yes
```

### Filter 3: Bounced emails
```
Matches: "Delivery Failed" OR bounce OR undeliverable
Apply: 🔴 URGENT
Star: Yes
```

### Filter 4: Diesel/fuel with cement/power
```
Matches: diesel cement OR diesel power OR diesel plant
Apply: Diesel / Fuel Products
```

---

## INBOX ZERO WORKFLOW

1. **Process inbox in commodity batches** — Nickel first (highest value), then Diesel, Coal, Copper, PKS.
2. **Label immediately** on open — don't close without a label.
3. **Archive aggressively** — if no action needed, archive (don't delete).
4. **Escalate to HubSpot** — any buyer signal → update CRM immediately.
5. **Weekly review** — Every Monday: clear `Follow-up Required` label.

---

## SPECIFIC ENTITIES TO FILTER

| Entity | Commodity | Label |
|--------|-----------|-------|
| Goodfound | Diesel | Diesel / Fuel Products - Negotiation |
| Republic Cement | Diesel | Diesel / Fuel Products - Negotiation |
| Mabuhay | Diesel | Diesel / Fuel Products - Negotiation |
| Philcement | Diesel | Diesel / Fuel Products - Negotiation |
| Suprea | Diesel | Diesel / Fuel Products - Negotiation |
| JX Advanced Metals | Copper | Copper Ore / Concentrates - Initial Contact |
| Tsingshan | Nickel | Nickel Ore - Lead / Prospecting |
| CEDC | Diesel | Diesel / Fuel Products - Lead / Prospecting |

---

*ECONARES Sales Operations | Version 1.0 | April 2026*
