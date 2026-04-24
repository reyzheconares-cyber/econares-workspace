# HubSpot Contact Enrichment Map — ECONARES
*Last updated: April 20, 2026. Use this to enrich HubSpot contacts before email campaigns.*

---

## Data Quality Targets

| Field | Target | Notes |
|-------|--------|-------|
| Industry | 80%+ | Most critical for personalization |
| Lead Status | 90%+ | Must know if OPEN/IN_PROGRESS |
| Job Title | 70%+ | For email salutation |
| Phone | 50% | Accept lower - often not publicly available |

---

## Personalization Tiers

### TIER A - Top Priority Buyers (26 contacts)

| Email | Company | Industry | Commodity Interest |
|-------|---------|----------|---------------------|
| contact@tssgroup.com.cn | Tsingshan Holdings | Mining & Metals - Nickel/Stainless Steel | Nickel Ore, NPI, Ferronickel |
| jason@tsingshan-steels.com | Tsingshan Group | Mining & Metals - Nickel/Stainless Steel | Nickel Ore, NPI |
| zhuhongmiao@tssgroup.com.cn | Tsingshan Holdings | Mining & Metals - Nickel/Stainless Steel | Nickel Ore |
| purchasing@lygend.com | Ningbo Lygend | Chemicals - Battery Materials | Nickel Ore, MHP, Nickel Sulfate |
| ales@lygend.com | Ningbo Lygend | Chemicals - Battery Materials | Nickel Ore |
| info@lygend.com | Ningbo Lygend | Chemicals - Battery Materials | Nickel Ore |
| trading@jinchuan-intl.com | Jinchuan International | Mining & Metals - Nickel/Copper | Nickel Ore, Copper Ore |
| info@jinchuan-intl.com | Jinchuan International | Mining & Metals - Nickel/Copper | Nickel Ore, Copper Ore |
| anson@jinchuan-intl.com | Jinchuan International | Mining & Metals - Nickel/Copper | CFO & Company Secretary |
| xct@huayou.com | Huayou Cobalt | Chemicals - Battery Materials/Cobalt | Nickel Ore, MHP, Cobalt |
| information@huayou.com | Huayou Cobalt | Chemicals - Battery Materials/Cobalt | Nickel Ore, Cobalt |
| sales@chinatisco.com | TISCO (Baowu Group) | Mining & Metals - Nickel/Stainless Steel | Nickel Ore, Ferronickel |
| chenbin02@baosteel.com | Baosteel Resources | Mining & Metals - Nickel/Stainless Steel | Nickel Ore |
| customer@baosteel.com | Baosteel Resources | Mining & Metals - Nickel/Stainless Steel | Nickel Ore |
| citicmetal@citic.com | CITIC Metal | Mining & Metals - Bulk Commodities | Nickel Ore, Copper Concentrate |
| procurement@byd.com | BYD | Manufacturing - EV/Battery | Nickel Ore (indirect - for NPI) |
| supply@catl.com | CATL | Manufacturing - EV/Battery | Nickel Ore (indirect) |
| purchase@jmm.co.jp | JX Advanced Metals | Manufacturing - Copper/Precious Metals | Copper Concentrate, Precious Metals |
| eortega@taiheiyo-cement.com.ph | Taiheiyo Cement | Manufacturing - Cement | Limestone, Coal, Diesel |
| jessie.sarias@unioncement.com.ph | Philcement (PHINMA) | Manufacturing - Cement | Coal, Limestone, Gypsum |
| jrrhisoler@mgen.com.ph | Meralco PowerGen (MGEN) | Power Generation | Coal, Diesel, Gas |

**Personalization angles for Tier A:**
- China Nickel (Tsingshan/Lygend/Jinchuan/Huayou/TISCO/Baosteel/CITIC) -> Reference their specific Ni capacity, FOB Philippines vs Indonesian supply advantage
- PH Cement (Taiheiyo/Philcement) -> Reference plant location, domestic logistics advantage vs Indonesian coal imports
- EV Battery Chain (BYD/CATL) -> Reference Philippine nickel as alternative supply chain to Indonesia
- JX Advanced Metals -> Copper concentrate with Au/Ag byproduct credits

---

### TIER B - Active Prospects (10 contacts)

| Email | Company | Industry | Commodity Interest |
|-------|---------|----------|---------------------|
| info@nickelindustries.com | Nickel Industries (ASX-listed) | Mining & Metals - Nickel/NPI | Nickel Ore |
| xhmineral@ytxinhai.com | Shandong Xinhai | Mining & Metals - Nickel/Tungsten | Nickel Ore, Tungsten |
| marketing@ytxinhai.com | Shandong Xinhai | Mining & Metals - Nickel/Tungsten | Nickel Ore |
| sales@chinabeihai.net | China Beihai | Manufacturing - Stainless Steel/Pipes | Nickel Ore |
| ecommerce@niscointl.cn | NISCO | Mining & Metals - Nickel/Stainless Steel | Nickel Ore, Ferronickel |
| sales@dlnis.com | Delong Nickel | Mining & Metals - Nickel/NPI | Nickel Ore, NPI |
| edfinch@bulk-ore.com | Bulk Ore Limited (HK) | Trading - Nickel/Bulk Commodities | Nickel Ore, Copper Concentrate |
| info@bigwaveresources.com | Big Wave Resources | Trading - Nickel/Commodities | Nickel Ore |
| info@fortunemetals.com | Fortune Metals (HK) | Trading - Nickel/Copper | Nickel Ore, Copper |
| contact@brightpoint.com.sg | Bright Point Trading (Singapore) | Trading - Nickel/Copper | Nickel Ore, Copper |

---

## Philippine Cement - Company-Based Enrichment (no email match)

| Company (contains) | Industry | Commodity Interest | Job Title Fallback |
|---|---|---|---|
| Mabuhay Filcement | Manufacturing - Cement | Coal, Limestone | Coal & Raw Materials |
| Goodfound Cement | Manufacturing - Cement | Coal, Diesel, Limestone | Procurement / Raw Materials |
| Republic Cement | Manufacturing - Cement | Coal, Diesel | Procurement Manager |
| Philcement (no email) | Manufacturing - Cement | Coal, Limestone, Gypsum | Procurement Officer |

---

## Test/Sample Data - Archive These

Contacts to archive in HubSpot (soft delete):

- Any email containing: test, sample, hubspot.com, example.com, null@
- Any contact with no email AND no company AND no name

PATCH endpoint with body: {"archived": true}

---

## Lead Status Values

| Status | When to Use |
|--------|-------------|
| NEW | Just added, never contacted |
| OPEN | Outreach in progress |
| IN_PROGRESS | Active conversation or deal negotiation |
| ATTEMPTED_TO_CONTACT | Tried, no reply yet |
| CLOSED | Deal won or lost |

---

## Enrichment Workflow

1. Fetch all contacts with ?properties=firstname,lastname,company,phone,email,jobtitle,industry,hs_lead_status
2. Apply safe() wrapper on every property - HubSpot returns None, not empty string
3. Categorize by email domain + company name keyword
4. Match against this enrichment map
5. Batch PATCH updates using temp file (-d @/tmp/hubspot_patch.json)
6. Re-fetch 2-3 sample contacts after PATCH to verify persistence
7. Space PATCH calls 0.3s apart (HubSpot rate limit ~90 req/min)

---

## Known Limitations

- Phone coverage ~47% is normal - PH/China contacts rarely share mobile publicly
- Jinchuan note: Mario Wong (former key contact) left July 2023. Anson Wong is now CFO & Company Secretary.
- DXB China India Resources: needs manual research - categorized as Tier C trading house.
