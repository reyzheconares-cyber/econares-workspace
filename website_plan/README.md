# ECONARES Website Plan — Build Package

This folder is the **execution-ready spec** for the agentic build app. It is designed to be consumed in two passes:

1. **Pass 1 (design + prototype)** — visual approval, done here in Open Design / hand-coded HTML.
2. **Pass 2 (production build)** — Astro + Tailwind + Decap CMS, fed by the data files in this folder.

## Files in priority order

| File | Purpose | Read first? |
|---|---|---|
| `WEBSITE_DEVELOPMENT_PLAN.md` | The full 7-section plan, plus an 8th section that is the build-agent brief. | ✓ Read first |
| `DESIGN.md` | Machine-readable brand spec in Google's DESIGN.md format. Lint passes, zero WCAG warnings. Open Design, Tailwind, and W3C DTCG all consume this file directly. | ✓ Read second |
| `BRAND_TOKENS.md` | Human-readable design rationale, color palette notes, contrast warnings, typography stack, logo usage rules. Companion to DESIGN.md. | ✓ Read second |
| `products.yaml` | All 21 commodities (4 industrial fuels + 17 metallic/non-metallic minerals). Drives `/products/**` pages. | ✓ Read third |
| `services.yaml` | 3 service categories with sub-services. Drives `/services/**` pages. | ✓ Read third |
| `projects.yaml` | 14 reference projects (5 marine/material shipments + 9 construction). Drives `/projects/**` pages. | ✓ Read third |
| `prototypes/home.html` | Self-contained HTML prototype of the homepage. Open in any browser. | ✓ Visual reference |
| `prototypes/product-steam-coal.html` | Self-contained HTML prototype of a product page (canonical template — drive all 21 products from this layout). | ✓ Visual reference |
| `prototypes/contact.html` | Self-contained HTML prototype of the contact page with both RFQ forms (product + service). | ✓ Visual reference |
| `prototypes/_preview-home.png` | Screenshot of the rendered homepage prototype. | Visual reference |
| `logo_source.png` | The original approved logo (7200×7200) for vectorization and asset generation. | For asset pipeline only |
| `profile.txt` | Plain-text extract of the source company profile PDF, for reference. | Optional |

## How the Open Design integration works

**Open Design 0.10.1** is installed at `C:\Users\reyma\AppData\Local\Programs\Open Design\`. It is the open-source Claude Design alternative from nexu-io/open-design (Apache-2.0). It is a desktop-first, agent-native design tool with 21 coding-agent adapters, 129 design systems, and 31+ skills.

**The right Open Design workflow for ECONARES is:**

1. **Author `DESIGN.md`** (done — see file in this folder). Open Design's `design-md` skill consumes this format directly.
2. **Use Open Design's `landing-page` skill** with `DESIGN.md` as the brand context to generate alternative homepage concepts. Compare against the prototype in `prototypes/home.html`.
3. **Use Open Design's `article-magazine` or `web-prototype` skill** to drive product and service page variants.
4. **Use Open Design's `dashboards` / `contact-widget` skills** for the RFQ form area.
5. **Export HTML** from Open Design and reconcile with the prototypes here.

The HTML prototypes in `prototypes/` are the **canonical baseline** — they implement the DESIGN.md tokens exactly, with the ECONARES content blocks already wired up. Use Open Design to **explore alternatives**, not to start from scratch.

## How to use these files in Open Design

Open Design is invoked from the desktop. The brand context it needs is the `DESIGN.md` file in this folder. To point Open Design at ECONARES:

1. Launch Open Design: `C:\Users\reyma\AppData\Local\Programs\Open Design\Open Design.exe`
2. Create a new project named "ECONARES Website"
3. Paste the contents of `DESIGN.md` as the project's brand spec
4. Invoke the `landing-page` skill with this prompt: *"Generate a homepage for ECONARES — a SEC-registered Philippine supplier of industrial fuels, minerals, and PCAB-licensed construction services. Use the brand tokens in DESIGN.md. The site must feel industrial (we move tonnage) but also feel like a real Philippine company (we answer the phone). Three sections above the fold: hero with split CTA, trust strip, three-division overview."*
5. Compare the output to `prototypes/home.html` and iterate

## Stack (recommended default for the production build)

**Astro** (static-first, fastest LCP) · **Tailwind CSS** (consume `tailwind.theme.json` exported from DESIGN.md — re-run `npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json` to regenerate) · **Decap CMS** (free, Git-based, non-technical editors) · **Cloudflare Pages** (free hosting, global CDN) · **Formspree** or **Cloudflare Workers + Turnstile** (form handling) · **Plausible** (privacy-friendly analytics).

Full rationale and alternatives are in `WEBSITE_DEVELOPMENT_PLAN.md` Section 7.

## Phased build plan

Weeks 1–10. Per-week deliverables and acceptance criteria are in `WEBSITE_DEVELOPMENT_PLAN.md` Section 7.3 and 8.11.

## Definition of done

Lighthouse Perf ≥ 90, A11y ≥ 95, BP ≥ 95, SEO ≥ 95 on every page template. All 21 commodity pages, all service pages, all 14 projects, and 2 launch blog posts live. Both RFQ forms tested end-to-end. Schema.org validates with zero errors. DESIGN.md lints clean (re-run `npx -y @google/design.md lint DESIGN.md`).

## Verification status of prototypes (as of 2026-06-16)

- `prototypes/home.html` — **canonical, industrial concept A**. 65 elements, 0 console errors. Screenshot at `_preview-home.png`.
- `prototypes/home-alternative-kami.html` — **alternative, editorial concept B**. 44 elements, 0 console errors. Parchment canvas, ink-blue accent, single serif typeface, print-grade long-form. Screenshot at `_preview-home-kami.png`. Visual QA: "highly disciplined, credibility-enhancing for heavy-industry B2B". Use this when targeting buyers who value substance over flash (cement procurement, power plant contracts, port authorities).
- `prototypes/product-steam-coal.html` — **53 elements**, proper `<table>` semantics, 7 spec rows, 0 console errors. The canonical template for all 21 product pages.
- `prototypes/contact.html` — **76 elements**, proper ARIA tablist, proper `<select>` with `<optgroup>` containing all 21 commodities, both forms complete, 0 console errors.
- `DESIGN.md` — `@google/design.md lint` passes with 0 errors, 0 WCAG warnings.

## Choosing between concept A (canonical) and concept B (kami)

| Dimension | Concept A — `home.html` | Concept B — `home-alternative-kami.html` |
|---|---|---|
| Aesthetic | Bold industrial, colorful brand accents on white | Editorial print, parchment canvas, ink-blue on cream |
| Type | Montserrat ExtraBold + Inter + Barlow Condensed | Charter serif at one weight |
| Hero | Split with image carousel | Massive display headline with ink-blue accent word |
| Section structure | 3 service cards, 6 project cards, 4-tile why-grid | Manifesto + 4 numbered chapters (01–04) + closing |
| Data presentation | Color-coded cards | Spec table inside chapter 02 |
| CTAs | Two-button row per section | Dark closing band with single primary + secondary |
| Trust signals | Navy strip with 5 pill badges | Tabular-num hero tokens + 4-metric row |
| Brand-color usage | Red, orange, yellow, sky, lime spread across cards | Ink-blue only (≤ 5% surface) |
| Best for | Maximize visual impact and brand recall | Maximize substance, gravitas, and spec density |
| Risk | Could read "generic industrial B2B" if execution slips | Could read "literary magazine" if imagery falls behind |
| Trust posture | "We move tonnage and we have energy" | "We have substance and we have been here since 2015" |

**Default recommendation: build concept A** (the canonical `home.html`) for v1, and treat concept B as the **/about or /capabilities** content route — a long-form editorial page that anchors the SEO content strategy. Both prototypes are wired to the same DESIGN.md tokens and same data files, so the build agent can implement either or both.
