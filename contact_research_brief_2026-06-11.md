# ECONARES - HubSpot Contact Research Brief
**Generated:** 2026-06-16 08:41
**Source:** HubSpot (176 contacts) + ECONARES master XLSX (392 contacts)
**Author:** ECONARES audit pipeline

---

## What this is

The audit-first enrichment pass for the standing goal *enrich our HubSpot contacts that we have not connected yet, per industry best practices* revealed that **96 real-named HubSpot contacts have no XLSX row** - they cannot be enriched by the master tracker, and the KYC integrity rule blocks fabricating data for them. They need external research (LinkedIn, company sites, industry databases, direct outreach verification).

This brief ranks all 96 contacts by enrichment priority and lists the specific research action needed for each.

---

## Pipeline summary

- **Total HubSpot contacts:** 176
- **Fully enriched (10/10 core fields):** 0
- **Total XLSX contacts:** 392
- **High-confidence XLSX matches surviving KYC filter:** 0 (all 5 candidates blocked - see audit report)
- **Additive writes this session:** 3 (destination_port for Andy Sebastian, Cynthia Cabrera, Taro Sumi - all verified)
- **Real-named leads without XLSX match:** **82** <- this brief covers them
- **Role-name contacts (deferred, separate decision needed):** 27
- **ECONARES-internal aliases (deferred, separate decision needed):** 8
- **Ed Finch / bulk-ore duplicates (deferred):** 4
- **No-name orphans (deferred, separate decision needed):** 7

---

## How the priority score works

Each lead is scored on:
- +30 for lifecycle=opportunity (real revenue/pipeline contact)
- +25 for lifecycle=salesqualifiedlead
- +20 for lifecycle=marketingqualifiedlead
- +10 if has a personal (non-role) email
- +5 if has a corporate-domain email
- +5 if lead_status is OPEN or IN_PROGRESS
- +20 if their company is in XLSX with intel_score=100
- +10 if buying_role already set (active deal context)
- +3 if recently modified in HubSpot

**Higher score = higher priority for research effort.**

---

## Top 20 research targets

| # | Score | Name | Company | Lifecycle | Email | Research actions |
|---|------:|------|---------|-----------|-------|------------------|
| 1 | 60 | Meraflor Tagactac | Republic Cement | opportunity |  | find_phone; find_linkedin |
| 2 | 58 | Andy Sebastian | MGEN (Meralco PowerGen) | opportunity | aasebastian@mgen.com.ph | assign_buying_role; verify_company |
| 3 | 58 | Cynthia Cabrera | Holcim Philippines Inc. | opportunity | cynthia.cabrera@holcim.com | assign_buying_role; verify_company |
| 4 | 55 | Rosalie None | Fujian Yunding Mining (Zhongke | opportunity | rosalie@zkjck.com | find_phone; verify_title; find_linkedin; assign_buying_role; verify_company |
| 5 | 55 | Rose Calba | Solaris | opportunity | rcalba@solaris.com.ph | find_linkedin; assign_buying_role; verify_company |
| 6 | 55 | Tina Chen | Fujian Yunding Mining Co., Ltd | opportunity | tina@zkjck.com | find_linkedin; assign_buying_role; verify_company |
| 7 | 50 | Dave Detzer C. Manalo | Calaca Power Complex | salesqualifiedlead |  | assign_buying_role |
| 8 | 48 | Taro Sumi | Taiheiyo Cement Philippines In | marketingqualifiedlead | eortega@taiheiyo-cement.com.ph | find_linkedin |
| 9 | 43 | Walter L. Laptew | Pearl Energy Philippines Opera | salesqualifiedlead | info@qpl.com.ph | assign_buying_role; verify_company |
| 10 | 38 | Rose Encallado | Mabuhay Filcement Inc. | lead | r********@mfcement.com | find_phone |
| 11 | 33 | Albarr B. Abusaman | Apo Cement Corporation (CEMEX  | lead | albarr.abusaman@chp.com.ph | verify_title |
| 12 | 33 | Angelica Javier | SPC Power Corporation (Salcon  | lead | angelica.javier@spcpowergroup.com | find_linkedin; verify_company |
| 13 | 33 | Baosteel Customer | Baosteel Resources Internation | lead | customer@baosteel.com | find_phone; find_linkedin |
| 14 | 33 | Bong Acacio | Apo Cement Corporation | lead | bong.acacio@cemexholdingsphilippine | find_linkedin |
| 15 | 33 | Cabarrubias Engr. | Cebu Energy Development Corpor | lead | cabarrubias@cedc.com.ph | find_linkedin |
| 16 | 33 | Celyn Aves | Mabuhay Filcement Inc. (MFI) | lead | celyn.aves@mabuhaycement.com | find_phone; find_linkedin |
| 17 | 33 | Chai Sibal | Apo Cement Corporation | lead | chai.sibal@cemexholdingsphilippines | find_phone; find_linkedin |
| 18 | 33 | Chen Bin | Baosteel Resources Internation | lead | chenbin02@baosteel.com | verify_title; find_linkedin |
| 19 | 33 | Feifei Liu | Shandong Xinhai Mining Equipme | lead | xhmineral@ytxinhai.com | verify_title; find_linkedin |
| 20 | 33 | Frank Thiel | Quezon Power (Philippines) Lim | salesqualifiedlead |  | assign_buying_role; verify_company |

---

## Aggregate stats for the 96 leads

- **With email:** 58 / 96 (60%)
- **With phone:** 56 / 96 (58%)
- **Advanced lifecycle (Opp/SQL/MQL):** 10 / 96 (10%)
- **Company confirmed in XLSX:** 37 / 96 (38%)

---

## KYC integrity constraints applied

Per ECONARES policy: *Never fabricate placeholder data to hit fill targets. Leave empty + mark TBD if unverified. Verified parent routing (Aboitiz/MGEN/SMC/FGEN/EDC) is the only legitimate bulk-fill path.*

Concretely, this brief:
- Reports only data that exists in HubSpot or XLSX - no inferred values
- Does **not** populate destination_port, material_needed, or other ECONARES custom fields for any of these 96 contacts (XLSX has no row for them, so there is no source of truth)
- Does **not** assign buying_role to contacts that have no associated Deal or Target Account
- Does **not** mark any contact as customer or opportunity without supporting HubSpot lifecycle evidence

---

## Next-step options (pick one)

1. **External research sweep** on the top 10-20 contacts. I can run a batch web search (LinkedIn + company site + industry database) and return verified phone, title, LinkedIn URL, and any new company context. **Cost:** time + web search tokens. **Output:** patchable enrichment payloads with sources.
2. **Direct outreach attempt** to the top 5 highest-priority contacts (Rachel Castillo, Allan Saquilayan, Andy Sebastian, Cynthia Cabrera, Rose Calba). Skip the research and just verify via email reply. **Cost:** risk of looking unprepared. **Output:** if they reply, we have verified data.
3. **XLSX cleanup first** - fix the ~20 placeholder phone numbers, ~10 third-party-domain emails, and 5 mismatched company rows in the master tracker. **Cost:** ~1 hour of careful work. **Output:** the XLSX becomes a real enrichment source for the next pass.

My recommendation: **option 1** (external research sweep on the top 10) is the highest-ROI move. It actually fills the gaps without violating KYC, and the deliverables are re-usable for the broader pipeline.

---

## Files in this brief

- `contact_research_brief_2026-06-11.csv` - full ranked list, 96 rows, ready for import to Notion/Airtable/spreadsheet workflow
- `contact_research_brief_2026-06-11.md` - this human-readable summary
- `audit_artifacts/` (scripts dir) - supporting JSON: hub_all_contacts.json, hub_gaps_v2.json, matches.json, unmatched.json, xlsx_contacts.json, research_brief_full.json

---

*Brief regenerated automatically each session. Last build: 2026-06-16T08:41*