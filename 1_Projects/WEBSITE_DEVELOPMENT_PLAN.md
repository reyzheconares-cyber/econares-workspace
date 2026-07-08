# ECONARES Website Development Plan

> **Company:** ECE Construction and Resources OPC (trade name: **ECONARES**)
> **Document type:** Execution-ready website plan for downstream agentic build
> **Plan version:** 1.0
> **Prepared:** 2026-06-16
> **Source materials:**
> - `ECONARES-COMPANY-PROFILE-updated.pdf` (vision + mission, products, services, projects, contact)
> - `APPROVED Logo.png` (brand identity, color palette, typography)

---

## How to use this plan

This is a self-contained spec an agentic build tool (or human developer) can follow end-to-end. Sections 1–7 answer the user's brief. Section 8 contains the execution brief, page-by-page content blocks, brand tokens, and a sitemap that a code-generation agent can consume directly.

---

# 1. Overview of the Company and Its Mission (150–200 words)

**ECE Construction and Resources OPC ("ECONARES")** is a SEC-registered Philippine construction and trading company headquartered at G/F BT & T Building, Hollow Block Road, Tabunok, Talisay City, Cebu 6045. Operating through three aligned subsidiaries — **ECE Resources and General Services** (DTI-registered 2015, industrial fuels and mine minerals), **ECE Construction Services** (DTI-registered 2019, PCAB-licensed contractor), and its parent trading arm — ECONARES delivers a fully integrated supply-and-build model to Philippine heavy industry.

The company supplies **industrial fuels** (steam coal, metallurgical coke, palm kernel shell, woodchips) and **metallic and non-metallic minerals** (construction aggregates, marine sand, boulders, diorite, limestone, chromite, nickel, iron sand, silica sand, greywackes, pozzolan, copper, clinker, quicklime/hydrated lime, gypsum, anhydrite) to **sugar mills, cement plants, manufacturing plants, and power-generation facilities** nationwide. Its construction arm executes **horizontal and vertical engineering works** — land development, reclamation, ports, bridges, shipyards, industrial plants, steel fabrication, civil, electrical, mechanical, and water-treatment projects.

**Vision & Mission:** *To provide high quality construction and engineering services to Philippine industry that helps national economic progress and development — while protecting the environment and preserving life through the wise and prudent use of resources, for the benefit of all mankind and generations to come.*

The website must position ECONARES as the **one accountable Philippine partner** for both the commodity inputs and the engineering capacity that heavy industry needs — a single source for fuel, minerals, construction, and marine logistics.

---

# 2. Key Features to Include on the Website

The site is a **B2B lead-generation and credibility engine**, not an e-commerce store. Every feature must serve a procurement officer, plant manager, or project director evaluating ECONARES for a contract or supply order.

## 2.1 Core features (must-have)

| # | Feature | Purpose | Priority |
|---|---------|---------|----------|
| 1 | **Product catalog** (Industrial Fuels + Minerals) | Browseable index of all commodities with specs, typical applications, origin, packaging | P0 |
| 2 | **Supplier capability module** | Vessel sizes, fleet list, tonnage capacity, port coverage, delivery lead times, MOQ | P0 |
| 3 | **Construction services module** | Service categories, past project portfolio, PCAB license display | P0 |
| 4 | **RFQ / Inquiry forms** (separated by product vs. service) | Conversion point — structured data capture | P0 |
| 5 | **Trust signals footer band** | SEC registration, DTI registrations (2015 & 2019), PCAB license, years operating | P0 |
| 6 | **Contact page** with map + multiple contact channels | Cebu HQ address, landline, email, sales-team direct lines | P0 |
| 7 | **About / Company background** | Story, subsidiaries, vision-mission, leadership | P0 |
| 8 | **Project portfolio / case studies** | Republic Cement coal shipments, Century Peak aggregates, Carrascal nickel, TBC Port, Mandani Bay, PDODC Housing, ALS Deep Well, etc. | P1 |
| 9 | **News / Insights blog** | Market updates, regulatory changes, supply-chain intelligence — SEO driver | P1 |
| 10 | **Careers page** | Org chart + open roles (President/CEO, Operations, Sales, Engineering, etc.) | P2 |
| 11 | **Multi-language toggle (English / Filipino)** | Serves local Cebu/Visayas and national Luzon markets | P2 |
| 12 | **Live chat or WhatsApp Business button** | B2B buyers expect fast response on WhatsApp in PH | P2 |

## 2.2 What the site is NOT
- No e-commerce checkout, no online payment, no shopping cart.
- No customer login portal in v1 (can be added in v2 as a client-intranet for repeat buyers).

---

# 3. Recommended Structure and Navigation Layout

## 3.1 Top-level menu (max 6 items)

```
HOME  |  ABOUT  |  PRODUCTS  ▾  |  SERVICES  ▾  |  PROJECTS  |  CONTACT
```

(If "Insights" is added later, it sits between Projects and Contact.)

## 3.2 Full sitemap

```
/ (Home)
/about
   /about/company-background
   /about/vision-mission
   /about/leadership
   /about/subsidiaries
   /about/certifications
/products
   /products/industrial-fuels
      /products/industrial-fuels/steam-coal
      /products/industrial-fuels/metallurgical-coke
      /products/industrial-fuels/palm-kernel-shell
      /products/industrial-fuels/woodchips
   /products/metallic-non-metallic-minerals
      /products/minerals/aggregates
      /products/minerals/marine-sand
      /products/minerals/boulders-armour-rocks
      /products/minerals/diorite
      /products/minerals/limestone
      /products/minerals/chromite
      /products/minerals/nickel
      /products/minerals/iron-sand
      /products/minerals/silica-sand
      /products/minerals/greywackes
      /products/minerals/pozzolan
      /products/minerals/copper
      /products/minerals/clinker
      /products/minerals/quicklime-hydrated-lime
      /products/minerals/gypsum
      /products/minerals/anhydrite
/services
   /services/engineering-construction
      /services/engineering-construction/land-development
      /services/engineering-construction/ports-bridges
      /services/engineering-construction/industrial-plants
      /services/engineering-construction/steel-fabrication
      /services/engineering-construction/civil-mech-electrical
      /services/engineering-construction/water-treatment
   /services/environmental-protection
   /services/marine-services
      /services/marine-services/lct-tug-barge
      /services/marine-services/vessel-piling-barge
      /services/marine-services/crane-cutter-suction-dredger
/projects
   /projects/coal-shipments
   /projects/mineral-shipments
   /projects/construction
/contact
   /contact/rfq-product
   /contact/rfq-service
   /contact/office-location
/legal
   /legal/privacy-policy
   /legal/terms-of-use
```

## 3.3 Footer

Four columns: Company | Products | Services | Contact, plus a credentials strip:
> *SEC-Registered | DTI 2015 (ECE Resources) | DTI 2019 (ECE Construction) | PCAB Licensed*

---

# 4. Best Practices for UX and Design

## 4.1 Information architecture
- **Audience-first hierarchy.** A procurement officer landing on the homepage must see, within 3 seconds, that ECONARES supplies bulk industrial fuels and minerals AND has a PCAB-licensed construction arm. The hero must split visually into these two value propositions with a single CTA each ("Request Fuel Quote" / "Discuss a Project").
- **Spec-driven product pages.** Each commodity gets a consistent template: typical specs (calorific value, ash %, size, moisture, origin), primary applications, packaging/delivery, MOQ, and an RFQ button. Specs are the #1 thing B2B buyers look for.
- **No hidden contact info.** Phone, email, and a WhatsApp link appear in the sticky header on every page.

## 4.2 Visual design — driven by the approved logo
- **Color palette (extracted from `APPROVED Logo.png`):**

  | Token | Hex | Use |
  |---|---|---|
  | `--brand-red` | `#F5251D` | Primary CTAs, "EC" accent |
  | `--brand-orange` | `#F78D1E` | Secondary accent, hover |
  | `--brand-yellow` | `#FDE126` | Highlights, badges |
  | `--brand-sky` | `#6DA6E3` | Informational sections |
  | `--brand-blue` | `#0033FF` | Footer, link emphasis |
  | `--brand-green` | `#6AFE01` | Trust-strip / "verified" tags |
  | `--brand-deep` | `#002A54` | Hero text on light bg, footer bg |
  | `--brand-slate` | `#2E343B` | Body text, borders |
  | `--brand-sky-mute` | `#4F6876` | Section backgrounds |
  | `--brand-tan` | `#A98F7A` | Construction-service accents |
  | `--brand-khaki` | `#DCD3A6` | Marine-service accents |
  | `--neutral-0` | `#FFFFFF` | Page bg |
  | `--neutral-100` | `#F5F5F5` | Card bg |
  | `--neutral-900` | `#0E1116` | Text on light |

- **Typography.**
  - Headings: a heavy bold display sans (e.g., **Montserrat ExtraBold** or **Poppins Black** — closest Google-font match to the logo's blocky rounded style).
  - Body: a clean neutral sans (e.g., **Inter** or **Open Sans**) for spec tables and dense product copy.
  - Tagline-style accents: a wide geometric sans (e.g., **Barlow Condensed Bold**) for the "CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING" service labels.

## 4.3 Performance and responsiveness
- **Mobile-first** (60%+ of Philippine B2B browsing is mobile, especially in the field).
- **Lighthouse targets:** Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95 on the homepage.
- **Core Web Vitals:** LCP < 2.5s, CLS < 0.1, INP < 200ms.
- Lazy-load all project images; serve WebP/AVIF; preload hero logo.

## 4.4 Accessibility (WCAG 2.1 AA minimum)
- Color-contrast ≥ 4.5:1 for body text; ≥ 3:1 for large text. **Watch out:** the brand sky-blue (`#6DA6E3`) and lime-green (`#6AFE01`) fail AA on white — use them as decorative/background tints only, never for body copy.
- Full keyboard navigation; visible focus rings (use `--brand-orange` 2px outline).
- ARIA labels on all icon-only buttons (RFQ, WhatsApp, search).
- Form fields: persistent labels (not placeholder-only), inline error messages, `aria-describedby` for help text.
- Skip-to-content link as the first focusable element.
- Captions / transcripts for any video on the homepage or project pages.

## 4.5 Trust and conversion patterns
- Real office photo and the BT & T Bldg address on the Contact page — not a stock photo.
- Visible landline (+63 32 232 6280) — B2B Filipino buyers still call.
- Sticky bottom-bar on mobile with "Call Now" and "WhatsApp" buttons.
- Inline trust badges near every RFQ form: SEC, DTI, PCAB, "15+ years in Philippine heavy industry" (recompute from 2015 founding).

---

# 5. SEO Strategy to Enhance Visibility

## 5.1 Keyword strategy (PH-market, English-default, Filipino secondary)

**Tier 1 — Direct intent (highest commercial value):**
- "steam coal supplier Philippines"
- "metallurgical coke supplier Cebu"
- "palm kernel shell supplier"
- "industrial fuel supplier Visayas"
- "construction aggregates supplier Philippines"
- "marine sand supplier Cebu"
- "limestone supplier Philippines"
- "clinker supplier Philippines"
- "PCAB licensed contractor Cebu"
- "land development contractor Cebu"
- "port construction Philippines"

**Tier 2 — Vertical / industry intent:**
- "coal supplier for cement plant Philippines"
- "fuel supply for sugar mill"
- "power plant fuel supplier"
- "bulk minerals for heavy industry"
- "industrial minerals Cebu"
- "dredging services Philippines"

**Tier 3 — Long-tail / informational (blog targets):**
- "steam coal specifications for cement kilns"
- "PCAB license classification guide Philippines"
- "palm kernel shell vs woodchips biomass comparison"
- "marine sand vs river sand for construction"

**Local SEO:**
- Google Business Profile: name, address, phone (NAP) must match site exactly.
- Service-area pages: Cebu, Manila, Batangas, Iloilo, Davao, General Santos — match your known client geography.
- LocalBusiness + Organization JSON-LD on every page.

## 5.2 On-page SEO template (per product/service page)

```html
<title>{Product} Supplier in the Philippines | ECONARES</title>
<meta name="description" content="ECONARES supplies {product} to cement, sugar, and power plants across the Philippines. Bulk orders, vessel delivery, quality-tested. Request a quote.">
<link rel="canonical" href="https://econares.com/products/{slug}">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content=".../og-{slug}.jpg">
<script type="application/ld+json">{
  "@context":"https://schema.org",
  "@type":"Product",
  "name":"{Product}",
  "brand":{"@type":"Brand","name":"ECONARES"},
  "manufacturer":{"@type":"Organization","name":"ECE Construction and Resources OPC"},
  "category":"Industrial Fuel / Mineral"
}</script>
```

## 5.3 Meta-description formula

`[Who we are] + [what we supply/do] + [where] + [proof / CTA]`

Examples:
- Homepage: *"ECONARES is a SEC-registered Philippine supplier of industrial fuels (steam coal, metallurgical coke, PKS, woodchips) and metallic & non-metallic minerals, with a PCAB-licensed construction arm. Serving cement, sugar, power, and manufacturing industries from Cebu since 2015."* (158 chars)
- Steam Coal: *"Bulk steam coal supplied to Philippine cement and power plants. Quality-tested, vessel-delivered, MOQ 5,000 MT. Request a quotation from ECONARES."* (140 chars)

## 5.4 Technical SEO
- SSL (HTTPS) mandatory.
- XML sitemap auto-generated, segmented by content type.
- `robots.txt` allows all except `/legal/` staging paths.
- Hreflang tags for `en` (default) and `fil` (Filipino) versions.
- 301 redirect map for the legacy domain if any.
- Schema: Organization, LocalBusiness, Product (per commodity), Service (per construction service), BreadcrumbList (on all non-home pages).

## 5.5 Content-driven SEO
- Publish **2 long-form articles per month** in the Insights blog, each targeting one Tier-2 or Tier-3 keyword.
- Each product page should have a 300–500 word "About {commodity} in the Philippine market" intro paragraph — original copy, not a copy-paste spec sheet.
- Backlink strategy: list ECONARES on PH-DTI directory, PCAB licensee registry, Philippine Constructors Association, local Cebu Chamber of Commerce, and trade publications (Cebu Business Daily, Philippine Daily Inquirer B2B section).

---

# 6. Content Requirements for Each Section

## 6.1 Homepage

**Above the fold:**
- **Hero:** split layout. Left: H1 *"Industrial Fuels, Minerals & Construction — From One Philippine Partner."* Sub: *"SEC-registered supplier to cement, sugar, and power plants, with a PCAB-licensed construction arm."* Two CTAs: **Request Fuel Quote** (primary) and **Discuss a Project** (secondary).
- **Right:** rotating 4-image carousel showing (1) coal stockpile, (2) vessel loading, (3) construction site, (4) minerals yard.
- **Trust strip:** SEC-Registered · DTI 2015 · DTI 2019 · PCAB Licensed · 15+ Years in PH Heavy Industry.

**Section 2 — What we supply:** Three icon-cards:
- 🛢️ **Industrial Fuels** — steam coal, metallurgical coke, PKS, woodchips
- ⛏️ **Metallic & Non-Metallic Minerals** — aggregates, marine sand, limestone, chromite, nickel, iron sand, etc.
- 🏗️ **Construction & Engineering** — land development, ports, industrial plants, civil/mech/electrical

**Section 3 — Featured projects:** 6-card grid (Republic Cement coal, Century Peak aggregates, Carrascal nickel, TBC Port, Mandani Bay, PDODC Housing).

**Section 4 — Why ECONARES:** 4-quadrant — Integrated Supply + Build, Cebu HQ + National Reach, Quality Tested & Inspected, PCAB-Licensed Engineering.

**Section 5 — Insights teaser:** 3 latest blog posts.

**Section 6 — Final CTA band:** *"Ready to source fuels, minerals, or build a project? Talk to our team today."* with phone + WhatsApp + RFQ button.

## 6.2 About page

- **Company background** (300 words): founding, SEC registration, subsidiary structure (ECE Resources 2015, ECE Construction 2019).
- **Vision & Mission** (verbatim from profile, with the ECE acronym expanded: *Excellent products & services, Corporate social and environmental responsibility, Economic development share*).
- **Leadership / Org structure:** President/CEO + 5 departments (Admin & HR, Operations, Accounting & Finance, Sales & Marketing, Supply Chain). An org-chart graphic + named heads if available (otherwise roles only).
- **Subsidiaries:** ECE Resources and General Services · ECE Construction Services · Parent trading arm.
- **Certifications & registrations:** SEC certificate, DTI 2015, DTI 2019, PCAB contractor license, BIR registration.

## 6.3 Products pages

Each commodity page uses a fixed template:

1. **H1:** Product name + "Supplier in the Philippines"
2. **Hero photo** of the product (real photo, not stock)
3. **50-word elevator** paragraph
4. **Typical specifications table** (calorific value, moisture, ash, sulfur, size, origin — example below for steam coal)
5. **Primary applications** (bullet list)
6. **Packaging & delivery** (bulk, vessel, 25kg sacks, etc.)
7. **MOQ & lead time** (e.g., 5,000 MT for bulk, 30 days lead)
8. **Related products** (cross-sell)
9. **RFQ CTA**

Example spec table for steam coal:

| Property | Typical Value |
|---|---|
| Net Calorific Value (NCV) | 5,500–6,500 kcal/kg (ARB) |
| Total Moisture | 12–15% max |
| Ash | 6–12% |
| Volatile Matter | 25–35% |
| Sulfur | 0.6–1.0% max |
| Size | 0–50 mm |
| Origin | Indonesia / Australia / South Africa |

## 6.4 Services pages

Construction services get a different template:

1. **H1:** Service category
2. **Overview** (100 words)
3. **Sub-services list** (e.g., for Marine Services: LCT/Tug & Barge, Vessel Piling Barge, Crane Cutter Suction/3-in-1 Dredger)
4. **Past project gallery** with captions
5. **Typical project value range / lead time** (without disclosing client data)
6. **PCAB license classification** displayed
7. **CTA:** "Discuss a project" → service-RFQ form

## 6.5 Projects / Portfolio

- Filter by industry (Cement, Nickel, Power, Real Estate, Public Works).
- Each project card: project name, client industry, year, scope summary, 3–6 photos.
- 9 reference projects from the profile: Republic Cement Coal, Century Peak Aggregates, Carrascal Nickel, TBC Port, PDODC Housing, Geordanson Complex Warehouse, The Mason-Maria Luisa Land Dev't, LPDC Land Dev't, ALS Deep Well Water Drilling, Mandani Bay, Dawis Residential Subdivision, Pardo MRB.

## 6.6 Contact page

- Two RFQ forms: **RFQ — Product** (commodity, quantity, delivery location, delivery date) and **RFQ — Service** (service type, project location, estimated value, timeline).
- Office info: G/F BT & T Bldg., Hollow Block Road, Tabunok, Talisay City, Cebu 6045 · (+63 32) 232 6280 · ece.eleguinresources@yahoo.com.
- Embedded Google Map of the BT & T Bldg location.
- Sales team direct contacts: split by division — Mine Mineral Products, Fuel Products, Construction Products & Services, Shipping & Equipment Rental.

## 6.7 Insights / Blog

- Article template: 1,200–1,800 words, H1, intro, H2 sections, table or diagram, conclusion + CTA to RFQ.
- Topics driven by Tier-2/Tier-3 keyword list (Section 5.1).

---

# 7. Suggested Technologies and Platforms

## 7.1 Recommended stack — **Astro + Tailwind CSS + Decap CMS**, hosted on **Cloudflare Pages**, with **Sanity** as optional headless CMS alternative.

**Why this stack (one-line each):**
- **Astro:** static-first → fastest possible LCP, ships zero JS by default, ideal for SEO.
- **Tailwind:** utility classes match the brand-token system in Section 4.2 perfectly; ships small CSS.
- **Decap CMS (formerly Netlify CMS):** free, Git-based, non-technical marketing team can edit pages and blog posts without a developer.
- **Cloudflare Pages:** global CDN, free SSL, $0 hosting at this traffic level, automatic deployments from Git.
- **Form handling:** **Formspree** or **Cloudflare Workers + Turnstile** (no CAPTCHA spam) for the two RFQ forms.
- **Analytics:** **Plausible** or **Umami** (privacy-friendly, no cookie banner needed).
- **Email:** transactional via **Resend** or **Postmark** (deliverability for RFQ notifications).

**Domain & email:** `.com` (econares.com or econstrading.com) on Cloudflare Registrar; email forwarding to `ece.eleguinresources@yahoo.com` initially, with a custom mailbox (e.g., `sales@econares.com` via Google Workspace) added in v2.

## 7.2 Alternative stacks (if constraints change)

| Need | Alternative | Trade-off |
|---|---|---|
| Marketing team wants a familiar CMS backend | **WordPress** with **GeneratePress** or **Kadence** theme | Heavier, slower, but easier for non-technical editors |
| Heavy e-commerce / quote-cart in future | **WordPress + WooCommerce** in catalogue mode (no checkout) | Add complexity only if needed |
| Shopify-style ease | **Shopify** | Overkill — no checkout needed; vendor lock-in |
| All-in-one no-code | **Webflow** + **Memberstack** | Visually flexible but expensive at scale |
| Local PH agency-style build | **Wix** or **Squarespace** | Not recommended for SEO at this scale |

**Recommended default: Astro static site + Decap CMS.** This gives ECONARES a fast, secure, SEO-strong, low-maintenance site for under $100/yr in hosting, with the option to migrate to a heavier CMS later if requirements change.

## 7.3 Phased build plan

| Phase | Deliverable | Timeline |
|---|---|---|
| 0 | Brand tokens, sitemap, wireframes (low-fi) | Week 1 |
| 1 | Design system + homepage + about + contact in Figma | Week 2–3 |
| 2 | Astro build, 1 product + 1 service template fully populated | Week 4 |
| 3 | All 4 industrial fuels + all 17 minerals + all construction services populated | Week 5–6 |
| 4 | Projects portfolio (12 reference projects) | Week 7 |
| 5 | Insights blog + 2 launch articles | Week 8 |
| 6 | SEO technical pass + Lighthouse 90+ + schema + sitemap | Week 9 |
| 7 | Accessibility audit + load testing + launch | Week 10 |

**Total: ~10 weeks for a full v1 launch.**

## 7.4 Cost estimate (v1, USD)

| Item | Cost |
|---|---|
| Domain (`.com`) | $12/yr |
| Hosting (Cloudflare Pages) | $0 |
| CMS (Decap) | $0 |
| Email (Formspree free tier or Workers) | $0–$20/mo |
| Analytics (Plausible) | $9/mo |
| Logo / photo shoot (if needed) | $300–$800 one-time |
| Content writing (10 articles + 17 product specs) | $1,500–$3,000 one-time |
| **Total first-year estimate** | **$2,500–$4,500** |

---

# 8. Execution Brief for the Agentic Build App

This section is consumed directly by the build agent. It collapses the plan above into deterministic inputs.

## 8.1 Site identity
- **Brand:** ECONARES
- **Legal:** ECE Construction and Resources OPC
- **Tagline (from logo):** CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING
- **Acronym meaning (ECE):** Excellent products & services · Corporate social and environmental responsibility · Economic development share
- **HQ:** G/F BT & T Bldg., Hollow Block Road, Tabunok, Talisay City, Cebu 6045 Philippines
- **Phone:** (+63 32) 232 6280
- **Email:** ece.eleguinresources@yahoo.com
- **Primary CTAs:** "Request Fuel Quote" · "Discuss a Project" · "Call Now" · "WhatsApp"

## 8.2 Brand tokens (CSS variables)

```css
:root {
  --brand-red:    #F5251D;
  --brand-orange: #F78D1E;
  --brand-yellow: #FDE126;
  --brand-sky:    #6DA6E3;
  --brand-blue:   #0033FF;
  --brand-green:  #6AFE01;
  --brand-deep:   #002A54;
  --brand-slate:  #2E343B;
  --brand-sky-mute:#4F6876;
  --brand-tan:    #A98F7A;
  --brand-khaki:  #DCD3A6;
  --neutral-0:    #FFFFFF;
  --neutral-100:  #F5F5F5;
  --neutral-900:  #0E1116;
}
```

## 8.3 Type scale
- Display: **Montserrat ExtraBold** (logo-style)
- Body: **Inter** (400 / 600 / 700)
- Tag labels: **Barlow Condensed Bold**

## 8.4 Routing (Section 3.2) — implement the full sitemap.

## 8.5 Page templates
- **Product page template** (Section 6.3) — implement once, drive all 21 products from a JSON/YAML data file.
- **Service page template** (Section 6.4) — implement once, drive all services from a JSON/YAML data file.
- **Project page template** — implement once, drive all 12 reference projects from a data file.
- **Blog post template** — implement once, MDX-driven.

## 8.6 Data files to create

```yaml
# src/data/products.yaml
products:
  - slug: steam-coal
    name: Steam Coal
    category: industrial-fuels
    origin: [Indonesia, Australia, South Africa]
    specs:
      ncv: "5,500–6,500 kcal/kg (ARB)"
      moisture: "12–15% max"
      ash: "6–12%"
      volatile_matter: "25–35%"
      sulfur: "0.6–1.0% max"
      size: "0–50 mm"
    applications: [Cement kilns, Power generation, Industrial boilers]
    packaging: "Bulk vessel"
    moq: "5,000 MT"
    rfq_type: product
  # ... 20 more
```

Same pattern for `services.yaml` and `projects.yaml`.

## 8.7 Forms
- Two RFQ forms. Submission writes to: (1) email notification to `ece.eleguinresources@yahoo.com`, (2) optional `submissions.json` or database row.
- Required fields for product RFQ: name, company, email, phone, commodity, quantity (MT), delivery location, delivery date, message.
- Required fields for service RFQ: name, company, email, phone, service type, project location, estimated value, timeline, message.
- Spam protection: Cloudflare Turnstile (free, no CAPTCHA friction).

## 8.8 SEO implementation
- Per-page `<title>` and `<meta description>` from Section 5.3.
- JSON-LD: Organization (all pages), LocalBusiness (contact), Product (per commodity), Service (per construction service), BreadcrumbList (all non-home), Article (blog posts).
- Auto-generated `sitemap.xml` and `robots.txt`.
- `lang="en"` default with optional `lang="fil"` Filipino pages for top-level pages only in v1.

## 8.9 Accessibility checklist
- All images: descriptive `alt` text (not "image1.jpg").
- Color contrast: never use `--brand-sky` or `--brand-green` for body text on white.
- Skip-to-content link first in `<body>`.
- All interactive elements keyboard-reachable with visible focus.
- Forms: persistent labels, inline errors, ARIA-described help.

## 8.10 Performance budget
- Homepage: < 100KB JS, < 50KB CSS, hero image < 200KB.
- Total page weight: < 1MB on first load.
- All images: WebP/AVIF, responsive `srcset`, lazy below the fold.

## 8.11 Acceptance criteria (definition of done)
- Lighthouse: Perf ≥ 90, A11y ≥ 95, BP ≥ 95, SEO ≥ 95 on every page template.
- All 21 commodity pages, all service pages, all 12 projects, and 2 launch blog posts live.
- Both RFQ forms tested end-to-end; submission reaches the Yahoo inbox.
- Schema.org validates with zero errors in Google Rich Results Test.
- Site loads in < 2s on 4G (Lighthouse throttling) in Cebu and Manila.
- Mobile usability: zero horizontal scroll at 320px viewport.

## 8.12 Launch checklist
1. Domain DNS pointed to Cloudflare Pages.
2. SSL provisioned (auto, free).
3. Google Business Profile created/claimed with matching NAP.
4. Google Search Console + Bing Webmaster Tools verified.
5. Plausible analytics installed.
6. Two launch blog posts published.
7. Sitemap submitted to Google + Bing.
8. Cross-link from LinkedIn company page, DTI registry entries, PCAB licensee profile.

---

*End of plan. Ready for execution.*
