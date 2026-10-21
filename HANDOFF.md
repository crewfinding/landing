# CrewFinding marketing site: handoff

Static site, plain HTML/CSS/JS. No build step, no framework, no page builder (rule: custom code only). Open `index.html` in a browser to preview, or run `python -m http.server` in this folder.

## What it is
Marketing site for CrewFinding, a crew-operations app for service businesses (GPS, time clock, e-sign, job costing, timesheets, payments, dispatch and job tracking, review requests). One conversion: app download. Brand: navy + gold, Instrument Sans, night/ivory bands.

## Pages
- `index.html` homepage (hero, dispatch + tracking with the "See it for" switcher, roofing photo story, timeline, filed docs, live feature cards, ledger, AI, card summary, founder, pricing, close)
- `moving/`, `landscaping/`, `junk-removal/`, `trucking-logistics/` service pages
- `pricing/`, `what-is-crewfinding/`, `privacy/`, `terms/`
- `llms.txt`, `robots.txt`, `sitemap.xml`

## Shared code
- `assets/cf.css` base design system and tokens (colors are CSS variables on `:root`)
- `assets/cf-dispatch.css` / `cf-dispatch.js` dispatch board, job-tracking card, switcher styles
- `assets/cf-live.css` / `cf-live.js` the live feature cards and the photo story. Declarative: `data-at`, `data-until`, `data-say`, `data-num`
- `assets/cf-universal.js` switcher data. **Generated** by `add_universal.py`
- `assets/cf-clips.js` card video loops. Homepage animation uses GSAP + ScrollTrigger + Lenis from `libs/`

## Generators (idempotent, run from this folder)
- `add_universal.py` writes the dispatch + tracking sections on the homepage and on moving / landscaping / junk-removal, and writes `assets/cf-universal.js`. Edit the `V` dict at the top to change examples per service.
- `build_trucking.py` then `add_clips.py` then `add_dispatch.py` rebuild the trucking page (freight version of dispatch).
- Do not hand-edit text between the `UNIVERSAL-START` / `UNIVERSAL-END` comments, edit the script instead.

## Rules that must hold
- Neutral wording on home and service pages: crew, job sheet, items, partner or subcontractor, recipient, proof of delivery. Freight words (BOL, carrier, 3PL, load) only on `trucking-logistics/`.
- Pricing is CAD, tiered by truck: $40 up to 2, $60 for 3, $80 up to 5, 6+ contact us. Competitor prices stay USD and footnoted.
- No "all-in-one" headline, no "solutions / streamline / empower / seamless / unlock". No invented numbers presented as real proof. Example data in the cards is illustrative.
- Check contrast and mobile (390px) after any visual change. Respect `prefers-reduced-motion`.

## Open items (nothing is deployed)
1. **Hosting + domain** decision, then deploy.
2. **Store URLs**: `IOS_URL` / `AND_URL` near the bottom of `index.html` and the badge links (`TODO real store URL`).
3. **Analytics**: GA4 `G-XXXXXXXXXX`, Google Ads `AW-XXXXXXXXXX`, Meta pixel are placeholders in the `<head>` of `index.html`. Wire `download_click` events.
4. **Login page**: does not exist yet. Needs a definition (member login for the web dashboard? app deep link?) before building.
5. Contact email `hello@crewfinding.com` (pricing page, "Let's talk" card) is a placeholder. Confirm the real address.
6. `terms/` still has `[CONFIRM TAXES]`. Taxes unconfirmed.
7. Assumed tiers: 1 truck = $40 and 4 trucks = $80. Confirm.
8. Real app screenshots to replace/add to the illustrative cards. Real review destination (Google or other) is unconfirmed, the copy never names one.
9. French mirror (bilingual EN/FR is a day-one requirement). Layouts were designed for longer French strings.
10. Roofing and construction have switcher tabs and a homepage photo story but no dedicated pages yet.
11. Jobber intro rates used in the pricing comparison expire Oct 30: re-check.
12. OG image `assets/og.png` and favicon are in place, re-check once the domain is set.

## Not included in this package
Source image masters (`assets-hf/`), screenshots, older page backups, and the image-generation scripts (they contained a billed API key). Ask Matthew if you need the masters.
