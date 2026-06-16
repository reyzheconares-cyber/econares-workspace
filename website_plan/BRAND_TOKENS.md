# ECONARES Brand Tokens

> Generated 2026-06-16 from `APPROVED Logo.png` (7200×7200, 4.3 MB, non-interlaced PNG).
> Source file preserved at `C:\Users\reyma\.hermes\desktop-attachments\APPROVED Logo.png` and `logo_source.png` in this folder.

## Logo description

**Mark:** Emblem-style logo. Top 60% is an industrial illustration — construction site (scaffolding, tower crane, cement mixer) on the left, city skyline + cargo ship in the center, mountainous terrain with excavator and dump truck on the right, set against a dusky blue-gray sky. Bottom 40% is the **ECONARES** wordmark with the tagline **CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING** below it. The whole logo is enclosed in a thick dark-gray rounded rectangular border.

**Symbolism:** Comprehensive service (construction, shipping, trading, earthmoving) under one brand. Duality of professional/grounded illustration + dynamic colorful typography = reliable + innovative.

## Primary color palette (brand name + tagline)

| Token | Hex | Use |
|---|---|---|
| `--brand-red` | `#F5251D` | "EC" in ECONARES, primary CTA buttons, error / urgent |
| `--brand-orange` | `#F78D1E` | "O" in ECONARES, hover states, secondary CTAs |
| `--brand-yellow` | `#FDE126` | "NA" in ECONARES, highlights, badges, ribbons |
| `--brand-sky` | `#6DA6E3` | "R" in ECONARES, informational sections, link |
| `--brand-blue` | `#0033FF` | "ES" in ECONARES, footer bg, link emphasis, primary brand blue |
| `--brand-green` | `#6AFE01` | Tagline text, "verified" / trust tags, success |
| `--brand-deep` | `#002A54` | "N" and text panel bg, hero text, dark sections |
| `--neutral-0` | `#FFFFFF` | Page background, contrast text on dark |

## Secondary / neutral palette (illustration)

| Token | Hex | Use |
|---|---|---|
| `--brand-slate` | `#2E343B` | Body text, borders, darkest shadows |
| `--brand-sky-mute` | `#4F6876` | Section backgrounds, muted text |
| `--brand-mountain` | `#20293B` | Mount, dark illustration |
| `--brand-tan` | `#A98F7A` | Construction-service accents |
| `--brand-khaki` | `#DCD3A6` | Marine-service accents, machinery |
| `--brand-city` | `#5A7995` | City buildings |
| `--neutral-100` | `#F5F5F5` | Card backgrounds |
| `--neutral-900` | `#0E1116` | Body text on light bg |
| `--neutral-300` | `#D0D5DB` | Borders, dividers |

## Contrast / accessibility notes

The following brand colors **fail WCAG AA on white background for body text** and must be used only as decorative/background tints or for large display text ≥ 24px:

- `--brand-sky` (`#6DA6E3`) — contrast vs white ~ 2.6:1
- `--brand-green` (`#6AFE01`) — contrast vs white ~ 1.6:1
- `--brand-yellow` (`#FDE126`) — contrast vs white ~ 1.4:1

These all pass AA on the dark `--brand-deep` background and are appropriate for the logo on its own dark panel. For body copy and form labels, use:

- `--brand-slate` (`#2E343B`) on white — contrast ~ 12:1 ✓ AAA
- `--brand-blue` (`#0033FF`) on white — contrast ~ 8.6:1 ✓ AAA
- `--neutral-900` (`#0E1116`) on white — contrast ~ 19:1 ✓ AAA

## Typography

| Role | Font | Weight | Size (desktop / mobile) |
|---|---|---|---|
| Display / H1 | **Montserrat** | ExtraBold (800) | 56 / 36 px |
| H2 | Montserrat | Bold (700) | 40 / 28 px |
| H3 | Montserrat | Bold (700) | 28 / 22 px |
| Body | **Inter** | Regular (400) | 16 / 16 px |
| Body strong | Inter | Semibold (600) | 16 / 16 px |
| Small / captions | Inter | Regular (400) | 14 / 14 px |
| Tag labels / nav | **Barlow Condensed** | Bold (700) | 14 / 14 px, uppercase, letter-spacing 0.05em |
| Spec table headers | Barlow Condensed | Bold (700) | 14 / 14 px, uppercase |
| Buttons | Inter | Semibold (600) | 16 / 16 px, uppercase, letter-spacing 0.04em |

**Why Montserrat:** closest Google-Font match to the logo's blocky rounded display style. Alternatives: Poppins Black, Nunito Black.

**Why Inter:** modern, optimized for screens, neutral — keeps the colorful logo and brand tokens as the visual focus.

**Why Barlow Condensed:** wide, geometric, all-caps feel — matches the tagline "CONSTRUCTION · TRADING · SHIPPING · EARTHMOVING" energy.

## Logo usage rules

- **Clear space:** minimum clear space = height of the "E" in ECONARES, on all sides.
- **Minimum size:** 120 px wide on screen, 25 mm wide on print.
- **Backgrounds:** use on `--brand-deep` (preferred) or white. Never on `--brand-yellow`, `--brand-green`, or `--brand-sky` (insufficient contrast).
- **Don'ts:** don't recolor, don't stretch non-uniformly, don't outline, don't place on busy photography without a solid background panel.

## Asset deliverables checklist

For the build agent to produce:
- [ ] `logo-full.svg` — full emblem logo (vector, primary)
- [ ] `logo-mark.svg` — just the icon part (top 60%) for favicons and small uses
- [ ] `logo-wordmark.svg` — just "ECONARES" wordmark with tagline for headers
- [ ] `logo-mono-white.svg` — single-color white version for dark backgrounds
- [ ] `logo-mono-slate.svg` — single-color slate version for light backgrounds
- [ ] `favicon.ico` — 32×32 from the icon mark
- [ ] `apple-touch-icon.png` — 180×180 from the icon mark
- [ ] `og-default.jpg` — 1200×630 social-share image with logo + tagline

## Source image

The original `APPROVED Logo.png` is 7200×7200, 4.3 MB, 8-bit RGB. A copy is preserved in this folder as `logo_source.png`. For favicon and OG-card rendering, the icon mark should be cropped from the top 60% of the original.
