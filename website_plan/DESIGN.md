---
version: alpha
name: ECONARES
description: Industrial gravitas meets colorful Cebu energy — a SEC-registered Philippine supplier of fuels, minerals, and construction, with a PCAB-licensed engineering arm.
colors:
  primary: "#002A54"
  secondary: "#2E343B"
  tertiary: "#F5251D"
  accent: "#F78D1E"
  highlight: "#FDE126"
  sky: "#6DA6E3"
  blue: "#0033FF"
  green: "#6AFE01"
  neutral: "#FFFFFF"
  surface: "#F5F5F5"
  border: "#D0D5DB"
  ink: "#0E1116"
  muted: "#4F6876"
typography:
  h1:
    fontFamily: "Montserrat"
    fontSize: "3.5rem"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: "Montserrat"
    fontSize: "2.5rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  h3:
    fontFamily: "Montserrat"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
  body-lg:
    fontFamily: "Inter"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: "Inter"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  body-sm:
    fontFamily: "Inter"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  tag:
    fontFamily: "Barlow Condensed"
    fontSize: "0.875rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.08em"
  button:
    fontFamily: "Inter"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.04em"
  spec-table:
    fontFamily: "Inter"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  2xl: "64px"
  3xl: "96px"
shadows:
  card: "0 1px 3px rgba(14,17,22,0.08), 0 1px 2px rgba(14,17,22,0.04)"
  card-hover: "0 10px 25px rgba(14,17,22,0.10), 0 4px 10px rgba(14,17,22,0.04)"
  sticky-header: "0 2px 8px rgba(14,17,22,0.06)"
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
    typography: "{typography.button}"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
    typography: "{typography.button}"
  button-secondary:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.primary}"
    borderColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
    typography: "{typography.button}"
  button-secondary-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
    typography: "{typography.button}"
  nav-link:
    textColor: "{colors.ink}"
    typography: "{typography.tag}"
  nav-link-active:
    textColor: "{colors.tertiary}"
    typography: "{typography.tag}"
  card-product:
    backgroundColor: "{colors.neutral}"
    borderColor: "{colors.border}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  card-product-hover:
    backgroundColor: "{colors.neutral}"
    borderColor: "{colors.tertiary}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  spec-row-header:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    typography: "{typography.tag}"
  spec-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.spec-table}"
  trust-badge:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.green}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
    typography: "{typography.tag}"
  hero-title:
    textColor: "{colors.primary}"
    typography: "{typography.h1}"
  hero-subtitle:
    textColor: "{colors.ink}"
    typography: "{typography.body-lg}"
  section-eyebrow:
    textColor: "{colors.tertiary}"
    typography: "{typography.tag}"
  section-title:
    textColor: "{colors.primary}"
    typography: "{typography.h2}"
  footer-bg:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
  footer-link:
    textColor: "{colors.sky}"
    typography: "{typography.body-sm}"
  footer-link-hover:
    textColor: "{colors.highlight}"
    typography: "{typography.body-sm}"
---

## Overview

ECONARES — trade name of **ECE Construction and Resources OPC** — is a SEC-registered Philippine construction-and-trading company headquartered in Talisay City, Cebu. The brand carries two visual registers that must coexist on every surface:

1. **Industrial gravitas** — the deep navy (`#002A54`) and slate (`#2E343B`) of the logo's industrial illustration. This is the "we move tonnage, we pour concrete" voice: dense, serious, accountable.
2. **Cebu energy** — the multicolored wordmark (red → orange → yellow → sky → blue) and the lime-green tagline. This is the "we are a real Philippine company, we are reachable, we answer the phone" voice.

The whole design system is built on the tension between those two registers: solid navy + slate structure, with brand-color accents that land on the moments of conversion (CTAs, trust strips, RFQ buttons) — never on body copy. Three of the brand colors (sky, green, yellow) fail WCAG AA on white and are reserved for backgrounds, tags, and large display only.

## Colors

- **Primary `#002A54` (Deep Sea Blue)** — the "N" in ECONARES, hero text, footer background, sticky header on scroll. The structural color of the site. AA on white for headlines.
- **Secondary `#2E343B` (Dark Slate)** — body text, borders, darkest shadow areas. 12:1 contrast on white — AAA for all text sizes.
- **Tertiary `#F5251D` (Vibrant Red)** — the "EC" in ECONARES, primary CTA buttons, urgent/error states, section eyebrows. The single most important accent for conversion. 5.4:1 on white — AA.
- **Accent `#F78D1E` (Bright Orange)** — the "O" in ECONARES, primary CTA hover state, secondary CTAs, focus rings. 3.0:1 on white — not for body copy, fine for buttons and large display.
- **Highlight `#FDE126` (Sunny Yellow)** — the "NA" in ECONARES, highlight badges, ribbon accents, decorative panels. 1.4:1 on white — background-only, never body copy.
- **Sky `#6DA6E3`** — the "R" in ECONARES, informational section accents, secondary links in footer. 2.6:1 on white — background-only.
- **Blue `#0033FF` (Royal Blue)** — the "ES" in ECONARES, footer link emphasis, link text in body (8.6:1 on white — AAA). Use for in-body hyperlinks.
- **Green `#6AFE01` (Lime Green)** — the tagline color, "verified" / trust tags, success states. 1.6:1 on white — always on dark backgrounds.
- **Neutral `#FFFFFF` (Pure White)** — page background, button text on dark, primary text on dark.
- **Surface `#F5F5F5` (Light Gray)** — alternating section backgrounds, card backgrounds, spec-row striping.
- **Border `#D0D5DB` (Mid Gray)** — hairlines, card borders, input borders.
- **Ink `#0E1116` (Near-Black)** — body text on light backgrounds, replaces pure black for less harsh reading.
- **Muted `#4F6876` (Industrial Sky)** — section backgrounds, muted captions, helper text. 6.2:1 on white — AA for body.

**Composition rule:** navy/slate/ink/white/muted carry the structure (≥ 80% of any page). Brand colors (red/orange/yellow/sky/blue/green) carry the conversion moments (≤ 20% of any page). Never two competing brand colors in the same row — one accent per call to action.

## Typography

Three families, each with a specific job:

- **Montserrat ExtraBold (800)** for h1/h2/h3 — closest Google Font to the logo's blocky rounded display. Web-friendly, ships small subset.
- **Inter (400 / 600 / 700)** for body, buttons, spec tables — the workhorse. Optimized for screen reading at 14–18px.
- **Barlow Condensed Bold (700), all-caps, +0.08em tracking** for tags, eyebrows, nav, and the "CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING" service labels. Wide, geometric, all-caps feel — matches the tagline energy.

**Type scale (desktop, mobile in parens):** h1 56/36px, h2 40/28px, h3 28/22px, body-lg 18/18px, body-md 16/16px, body-sm 14/14px, tag 14/13px, button 16/16px.

**Line-height:** display 1.1, headings 1.15–1.2, body 1.5–1.6, tags/buttons 1.0.

**Rationale:** the colorful wordmark is the visual focus of the brand. Body type must disappear. Montserrat ExtraBold gives the logo a digital cousin; Inter's neutrality keeps the colorful brand tokens as the visual focus; Barlow Condensed is the only "tag" voice that matches the tagline's energy.

## Layout

- **Container:** max-width 1280px, side padding 24px mobile / 40px desktop.
- **Grid:** 12-column on desktop (with 24px gutter), 6-column on tablet, 4-column on mobile (16px gutter). No fixed pixel columns — use CSS grid with `repeat(auto-fit, minmax(280px, 1fr))` for product cards.
- **Section vertical rhythm:** 96px top/bottom on desktop, 64px on mobile. One section per visual idea.
- **Hero:** split layout. Left 50%: H1, subtitle, two CTAs. Right 50%: rotating image carousel (4 photos). Min-height 600px desktop, 500px mobile.
- **Cards:** product/service cards use a 1:1 thumbnail + 1.5x text height ratio. Use `--rounded.lg` (12px) for industry feel, not the consumer-tech 24px.

## Elevation

- **Flat by default.** No drop shadows on the navy header or footer — they're already dark.
- **Cards:** subtle two-stop shadow on rest, larger on hover (the `--shadows.card` / `--shadows.card-hover` tokens). No glassmorphism.
- **Sticky header:** one subtle shadow on scroll (`--shadows.sticky-header`).
- **Modals/overlays:** 0 20px 50px rgba(0,0,0,0.20).

## Shapes

- **Buttons:** 8px radius — feels industrial, not consumer-app.
- **Cards:** 12px radius.
- **Tags/badges:** fully pill (`--rounded.pill`).
- **Input fields:** 8px radius.
- **No blob shapes, no wavy hero dividers, no organic SVG backgrounds.**

## Components

### Buttons

- **Primary (red):** red background, white text, uppercase Inter SemiBold 16px with 0.04em tracking. 14px × 28px padding. Hover swaps to orange with ink text — the only allowed two-color hover transition.
- **Secondary (white with navy border):** white background, navy text and border, 2px solid. Hover fills with navy, inverts text to white.
- **Focus ring:** 2px solid orange (`#F78D1E`), 2px offset, always visible on keyboard focus. Never remove the outline.

### Navigation (sticky header)

- White background, 80px height desktop / 64px mobile, bottom border `--border` 1px.
- Left: ECONARES logo wordmark (SVG from `logo-wordmark.svg`).
- Center: 6 main nav items (HOME, ABOUT, PRODUCTS, SERVICES, PROJECTS, CONTACT). Active item is red (`--tertiary`).
- Right: phone icon + "(+63 32) 232 6280" link, plus a "Request Quote" red button.
- Mobile: hamburger → full-screen overlay nav.

### Cards

- **Product card:** 1:1 thumbnail top, 16px padding bottom. Category eyebrow (Barlow Condensed, red), product name (h3, navy), 1-line spec summary, "Specs & RFQ →" link (red).
- **Service card:** icon top-left (24px, navy), name (h3, navy), 2-line description, "View services →" link.
- **Project card:** 4:3 thumbnail top, overlay gradient bottom 30%, project name (white, h3), industry + year caption (Barlow Condensed, white 80%).

### Spec table (product detail page)

- Header row: navy background, white Barlow Condensed text, all caps.
- Body rows: alternating white / `--surface` (light gray).
- First column: Barlow Condensed tag (red), all caps.
- Second column: Inter 15px, ink text.
- Border between rows: 1px `--border`.

### Trust badges / credentials strip

- Pill shape, 6px × 14px padding, navy background, lime-green Barlow Condensed text.
- 4-5 badges per strip: "SEC-Registered · DTI 2015 · DTI 2019 · PCAB Licensed · 15+ Years in PH Heavy Industry".

### Hero (homepage)

- H1: navy text, max 3 lines. Subtitle: ink 18px, max 2 lines.
- Two CTAs stacked or side-by-side. Primary red "Request Fuel Quote" (links to /contact?type=product). Secondary navy-bordered "Discuss a Project" (links to /contact?type=service).
- Right: 4-image carousel (coal stockpile, vessel loading, construction site, minerals yard) with 5s autoplay and 4s fade.

### Footer

- Navy background, white headings, sky-blue body links (hover highlight yellow).
- 4 columns: Company / Products / Services / Contact.
- Bottom strip: 1px sky-blue border top, "© 2026 ECE Construction and Resources OPC" + SEC registration number + links to Privacy and Terms.

## Do's and Don'ts

**Do:**
- Use red (`--tertiary`) for the single most important action on every page.
- Use Barlow Condensed for the "CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING" service labels in any icon row or footer summary.
- Keep body type Inter. Headlines Montserrat ExtraBold.
- Use real photos of coal, vessels, and construction sites (not stock photos) on the homepage and project pages.
- Display the landline `(+63 32) 232 6280` and the Yahoo email in the sticky header — Filipino B2B buyers call.
- Add a sticky bottom-bar on mobile with "Call Now" (red) and "WhatsApp" (green) buttons.

**Don't:**
- Use the brand red, orange, yellow, sky, or green for body copy on white — they fail WCAG AA. Body text is always ink, slate, or muted on light; white on navy.
- Stack more than two brand colors in the same row.
- Use glassmorphism, blur effects, or aggressive gradient backgrounds. The brand is industrial.
- Use decorative SVG illustrations or icon-spam card grids.
- Use fake metrics, placeholder testimonials, or AI-fluff section names like "Insights", "Growth", "Scale".
- Use the logo on `--highlight` (yellow), `--green`, or `--sky` backgrounds — insufficient contrast.
- Strip the outline on focus. Always visible.
- Hide the phone number behind a "Contact us" link.
