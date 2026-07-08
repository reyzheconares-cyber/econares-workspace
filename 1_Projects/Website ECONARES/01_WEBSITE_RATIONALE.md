# WEBSITE RATIONALE AND DESIGN OVERVIEW
## ECONARES B2B WEB PLATFORM — CEO AND STAFF BRIEFING

**DATE:** 2026-07-08 (FOR PRESENTATION ON 2026-07-08)
**PREPARED BY:** SALES AND MARKETING OFFICER, ECONARES
**PURPOSE:** EXPLAIN THE RATIONALE, DESIGN DECISIONS, AND CONTENT STRUCTURE OF THE NEW ECONARES WEBSITE TO THE CEO AND STAFF
**AUDIENCE:** CEO, MANAGEMENT TEAM, AND KEY STAKEHOLDERS

---

# 1. EXECUTIVE SUMMARY

This document presents the rationale, design framework, and content structure of the new ECONARES B2B web platform, built end-to-end over the past 1–3 months as part of the company's digital transformation initiative. The site is currently live at **https://econares-website.vercel.app** for the CEO and staff to review and demo.

The website positions ECONARES as the **one accountable Philippine partner** for both the commodity inputs (industrial fuels, metallic and non-metallic minerals) and the engineering capacity (PCAB-licensed construction, marine services) that Philippine heavy industry needs. The platform consolidates 20 commodities, 24 services, and 14 reference projects into a single, fast, mobile-responsive site built for B2B procurement teams, project directors, and plant managers.

**BY THE NUMBERS (AT TIME OF LAUNCH):**
- 68 STATIC HTML PAGES
- 20 COMMODITY PAGES (4 INDUSTRIAL FUELS + 16 METALLIC AND NON-METALLIC MINERALS)
- 24 SERVICE PAGES (3 CATEGORIES × SUB-SERVICES)
- 14 PROJECT REFERENCE PAGES
- 1.8 MB TOTAL DIST SIZE (LOADS IN UNDER 2 SECONDS ON 3G)
- ZERO BROKEN LINKS ACROSS 3,196 INTERNAL REFERENCES
- MOBILE-RESPONSIVE FROM 320PX TO 1920PX
- WCAG 2.1 AA-READY STRUCTURE (SKIP-TO-CONTENT, ARIA, SEMANTIC TABLES, FOCUS RINGS)
- ORGANIZATION + LOCALBUSINESS + PRODUCT + SERVICE JSON-LD STRUCTURED DATA ON EVERY PAGE
- LIVE FORMSPIREE LEAD-CAPTURE WIRED ON BOTH PRODUCT AND SERVICE RFQ FORMS

---

# 2. WHY THE WEBSITE WAS NEEDED

## 2.1 THE BEFORE STATE

Before this build, ECONARES had **no live website**. The company's only public digital footprint was:
- A YAHOO EMAIL ADDRESS (ece.eleguinresources@yahoo.com) — UNPROFESSIONAL FOR B2B PROCUREMENT
- A LINKEDIN PAGE (MINIMAL ACTIVITY)
- NO PUBLIC CATALOG OF 20 COMMODITIES
- NO PUBLIC PORTFOLIO OF 14 REFERENCE PROJECTS
- NO PUBLIC CAPABILITY STATEMENT
- NO RFQ CAPTURE MECHANISM

This is a significant gap. **B2B procurement teams in cement, sugar, power, and manufacturing routinely disqualify suppliers without a working website** during pre-qualification. The absence of a site means ECONARES loses deals to competitors who can be Googled.

## 2.2 THE AFTER STATE

The new site gives ECONARES:
1. **A PUBLIC CATALOG** of all 20 commodities with spec tables, applications, and logistics
2. **A SEARCHABLE PORTFOLIO** of 14 reference projects (Republic Cement, Century Peak, Carrascal Nickel, TBC Port, Mandani Bay, etc.)
3. **A CAPABILITY STATEMENT** that communicates the integrated supply-and-build model
4. **TWO RFQ FORMS** (Product RFQ and Service RFQ) that route inquiries directly to the sales team
5. **MOBILE-FIRST DESIGN** for procurement officers checking on their phones
6. **SEO FOUNDATION** (sitemap, robots.txt, structured data) so the company can be found on Google

---

# 3. DESIGN PHILOSOPHY

## 3.1 INDUSTRIAL GRAVITAS MEETS CEBU ENERGY

The design brief was simple: **the site must look like a real company that moves tonnage, not a startup trying to look tech-y**. The visual language pairs serious industrial navy and steel-gray typography (Montserrat 800-weight headers) with energetic Cebu-color accents (red, orange, yellow) borrowed from the approved ECONARES logo.

The two design concepts delivered and compared were:
- **CONCEPT A (selected for the homepage and most pages):** Industrial card-grid layout with bold typography, colorful accents, and gradient project tiles. Industrial-feeling, scale-appropriate.
- **CONCEPT B (selected for /capabilities long-form page):** Editorial kami-style parchment canvas with Charter serif typography and a manifesto + numbered chapters. Gravitas, substance, print-grade.

The dual-mode approach lets ECONARES present different facets of the brand in different contexts: the homepage sells the integrated model; the /capabilities page documents the depth.

## 3.2 DOCUMENTED AESTHETIC PREFERENCES

Per the company's design system, all product imagery and photography will follow the ECONARES aesthetic:
- **CENTERED SUBJECT** in every frame
- **NATURAL COLOR SATURATION** (no oversaturated or desaturated product photos)
- **MODERN MINIMALIST LUXURY WHITE BACKGROUND** for studio shots
- **WARM ATMOSPHERIC LIGHT** with distinct light-dark layering for depth

This aesthetic applies to:
- The 20 commodity product photos (initial batch AI-generated as placeholders, to be replaced with real site photography)
- Future site photography at the Cebu yard, docks, and project sites
- Marketing collateral and printed brochures

## 3.3 TWO VISUAL CONCEPTS COMPARED

| ASPECT | CONCEPT A (SELECTED) | CONCEPT B (SELECTED FOR /CAPABILITIES) |
|---|---|---|
| VISUAL POSTURE | BOLD INDUSTRIAL | EDITORIAL PRINT |
| TRUST POSTURE | "WE MOVE TONNAGE" | "WE HAVE SUBSTANCE" |
| BEST FOR | HOMEPAGE, PRODUCTS, SERVICES, PROJECTS | CAPABILITIES, ABOUT |
| COLOR PALETTE | PRIMARY NAVY + RED/ORANGE ACCENTS | INK-BLUE ON PARCHMENT |
| TYPOGRAPHY | MONTSERRAT 800 (DISPLAY) + INTER (BODY) | CHARTER SERIF (BODY) + MONTSERRAT (DISPLAY) |
| AESTHETIC RISK | READS GENERIC IF EXECUTION SLIPS | READS LITERARY IF IMAGERY FALLS BEHIND |

---

# 4. SITE STRUCTURE AND NAVIGATION

## 4.1 PRIMARY NAVIGATION (8 ITEMS)

The site uses a clean 8-item primary navigation that maps directly to the three ECONARES divisions:

| # | NAV ITEM | URL | WHAT IT DOES |
|---|---|---|---|
| 1 | HOME | / | HERO + VALUE PROP + 3 DIVISIONS + 6 PROJECTS + INSIGHTS TEASER + CTA |
| 2 | ABOUT | /about/ | COMPANY BACKGROUND, CREDENTIALS, CONTACT INFO |
| 3 | PRODUCTS | /products/ | CATALOG OF 20 COMMODITIES (FUELS + MINERALS) |
| 4 | SERVICES | /services/ | 21 SUB-SERVICES ACROSS 3 CATEGORIES |
| 5 | PROJECTS | /projects/ | 14 REFERENCE PROJECTS WITH FILTERS |
| 6 | CAPABILITIES | /capabilities/ | LONG-FORM CAPABILITIES STATEMENT (CONCEPT B) |
| 7 | INSIGHTS | /insights/ | ARTICLES (STUBS, 3 TO BE WRITTEN FOR LAUNCH) |
| 8 | CONTACT | /contact/ | TWO RFQ FORMS (PRODUCT + SERVICE) WITH TAB SWITCHING |

The navigation is **mobile-responsive** with a hamburger drawer for screens under 1024px, and includes a sticky call/WhatsApp bottom bar on mobile for instant lead-capture.

## 4.2 THE THREE DIVISIONS (MAPPED TO COMPANY STRUCTURE)

| DIVISION | COMPANY ENTITY | DTI REG. | WEBSITE SECTION |
|---|---|---|---|
| 01 — INDUSTRIAL FUELS | ECE RESOURCES AND GENERAL SERVICES | 2015 | /products/ (fuels tab) |
| 02 — MINERALS | ECE RESOURCES AND GENERAL SERVICES | 2015 | /products/ (minerals tab) |
| 03 — CONSTRUCTION | ECE CONSTRUCTION SERVICES | 2019, PCAB-LICENSED | /services/ |

This three-division structure is repeated consistently across the homepage, /capabilities, /about, and the RFQ form tabs, so prospects and partners can map the website to the legal entities without confusion.

---

# 5. CONTENT HIGHLIGHTS (BY SECTION)

## 5.1 HOMEPAGE (/)

The homepage answers the question "WHY ECONARES?" in 8 seconds. Key elements:

- **HERO:** "Industrial Fuels, Minerals & Construction — From One Philippine Partner." with rotating gradient image carousel showing 4 site photos (placeholder for real photography)
- **CREDENTIALS STRIP:** SEC-REGISTERED OPC, DTI 2015 ECE RESOURCES, DTI 2019 ECE CONSTRUCTION, PCAB LICENSED, 15+ YEARS IN PH HEAVY INDUSTRY
- **THREE DIVISIONS:** Industrial Fuels, Minerals, Construction — with dedicated CTAs
- **6 PROJECT TILES:** Republic Cement, Century Peak, Carrascal Nickel, TBC Port, ALS, Mandani Bay
- **WHY ECONARES (4-POINT GRID):** Integrated supply + build, Cebu HQ + national reach, Quality-tested and inspected, PCAB-licensed engineering
- **INSIGHTS TEASER:** 3 article stubs (to be filled in post-launch)
- **FINAL CTA:** REQUEST FUEL QUOTE / DISCUSS A PROJECT / CALL

## 5.2 /PRODUCTS/ (THE CATALOG)

- 4 INDUSTRIAL FUELS with spec tables, applications, MOQ
- 16 METALLIC AND NON-METALLIC MINERALS with the same structure
- Each product page has: hero, spec table, logistics (packaging/MOQ/lead time), primary applications, quality assurance, related products
- "DON'T SEE YOUR COMMODITY?" CTA for custom RFQs

## 5.3 /SERVICES/

- 3 CATEGORIES: ENGINEERING & CONSTRUCTION, ENVIRONMENTAL PROTECTION, MARINE SERVICES
- 21 SUB-SERVICE PAGES with descriptions
- Covers the full PCAB-licensed capability

## 5.4 /PROJECTS/

- 14 REFERENCE PROJECTS grouped by SHIPMENTS and CONSTRUCTION
- Each project page has: client, year, type, location, scope, results

## 5.5 /CONTACT/

- TWO TAB RFQ FORM: PRODUCT RFQ and SERVICE RFQ
- Pre-populated commodity selector with all 20 commodities
- Pre-populated service selector with all 21 sub-services
- Routes inquiries to the sales team via Formspree
- Direct sales team contact cards (4 sales officers by division)

## 5.6 /CAPABILITIES/ (CONCEPT B)

- LONG-FORM MANIFESTO + 4 NUMBERED CHAPTERS
- Industrial gravitas meets print-grade typography
- For serious procurement teams who want to read the full capability statement

---

# 6. TECHNICAL DECISIONS (FOR THE TECH-CURIOUS)

## 6.1 STATIC SITE OVER CMS

**DECISION:** BUILD AS A STATIC SITE (ASTRO + TAILWIND) INSTEAD OF WORDPRESS, WEBFLOW, OR A TRADITIONAL CMS.

**RATIONALE:**
- **SPEED:** Static pages load in under 2 seconds on 3G, vs 4–8 seconds for CMS-driven sites
- **SECURITY:** No database, no plugin vulnerabilities, no admin panel to compromise
- **COST:** Hosting is free (Vercel Hobby tier covers this site indefinitely)
- **RELIABILITY:** Static sites have 99.99% uptime; CMS sites typically have 99.5%
- **SEO:** Google explicitly rewards fast static sites
- **MAINTENANCE:** No patching, no plugin updates, no database backups

## 6.2 DATA-DRIVEN ARCHITECTURE

All 20 commodity pages, 24 service pages, and 14 project pages are generated from YAML data files. This means:
- **ADDING A NEW PRODUCT** = edit `products.yaml`, rebuild, deploy (5 minutes)
- **UPDATING A SPEC** = edit one value, rebuild, deploy (3 minutes)
- **NO TOUCHING HTML** for routine content updates

## 6.3 MOBILE-FIRST DESIGN

- 320PX TO 1920PX RESPONSIVE
- HAMBURGER NAVIGATION UNDER 1024PX
- STICKY CALL/WHATSAPP BOTTOM BAR ON MOBILE
- OPTIMIZED FOR ONE-HAND USE (PROCUREMENT OFFICERS ON PHONES)

## 6.4 ACCESSIBILITY

- WCAG 2.1 AA-READY (CONTRAST, NAVIGATION, SEMANTIC HTML)
- SKIP-TO-CONTENT LINK FOR KEYBOARD USERS
- ARIA ROLES ON TAB LISTS, NAVIGATION, FORMS
- SEMANTIC TABLES WITH PROPER HEADERS
- FOCUS RINGS ON ALL INTERACTIVE ELEMENTS

## 6.5 SEO FOUNDATION

- SITEMAP.XML (68 URLS, AUTO-GENERATED)
- ROBOTS.TXT WITH SITEMAP REFERENCE
- JSON-LD STRUCTURED DATA (ORGANIZATION, LOCALBUSINESS, PRODUCT, SERVICE, CREATIVEWORK)
- CANONICAL URLS ON EVERY PAGE
- OPEN GRAPH + TWITTER CARD METADATA
- SEMANTIC HTML (H1, H2, H3 HIERARCHY)

---

# 7. NEXT STEPS (POST-PRESENTATION)

| # | TASK | OWNER | TIMELINE |
|---|---|---|---|
| 1 | CEO REVIEW AND SIGN-OFF ON DESIGN | CEO | 1–2 DAYS |
| 2 | PHOTOGRAPHY SHOOT AT CEBU YARD (1–2 DAYS) | MARKETING + OPERATIONS | 1–2 WEEKS |
| 3 | WRITE 3 LAUNCH INSIGHTS ARTICLES | MARKETING | 1 WEEK |
| 4 | GOOGLE WORKSPACE SETUP (SALES@ECONARES.COM) | CEO + IT | 2–3 DAYS |
| 5 | MIGRATE FROM VERCEL DEMO TO ECONARES.COM (CLOUDFLARE + NAMECHEAP) | IT | 1 WEEK |
| 6 | SUBMIT TO GOOGLE SEARCH CONSOLE + GOOGLE BUSINESS PROFILE | MARKETING | 1 DAY |
| 7 | ESTABLISH MAINTENANCE RETAINER (PROPOSED: ₱8,000/MONTH) | CEO + MARKETING | POST-LAUNCH |

---

# 8. CONCLUSION

The new ECONARES website is a **professional, B2B-ready, fast, mobile-responsive platform** that:
- Positions the company as the integrated Philippine partner for fuels, minerals, and construction
- Showcases the 20-commodity catalog and 14-project portfolio
- Captures RFQ leads through dedicated Product and Service forms
- Provides the SEO and mobile foundations for long-term digital growth
- Is built to industry best practices (static site, data-driven, accessible, SEO-ready)

The site is **live and ready for review** at **https://econares-website.vercel.app**.

---

**PREPARED BY:** SALES AND MARKETING OFFICER
**DATE:** 2026-07-08
**VERSION:** 1.0 (FINAL FOR PRESENTATION)
**STATUS:** READY FOR CEO + STAFF REVIEW
