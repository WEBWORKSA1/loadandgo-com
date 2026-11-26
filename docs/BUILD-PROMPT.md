# Phase-by-phase build prompt for LoadandGo.com

Paste one phase at a time into a capable coding assistant with repository access. Each phase ends with a check; do not start the next until the check passes. Constants used throughout:

- Domain: `LoadandGo.com` ("Load and Go"). Repo: `WEBWORKSA1/loadandgo-com`, branch `main`, GitHub Pages free plan.
- AdSense publisher: `ca-pub-6620975821265271`.
- Top bar on every page, linked to the owner's contact page: "Contact, if you are interested in this website / domain name / sponsorship / advertisement / partnership".
- One inbox for every form, never visible in any page or source file in readable form.

---

## Phase 0. Research and name clearance

> Search public trademark records for "Load and Go", "Load & Go" and "Load N Go". List each live mark with its goods or services. Then open and read at least 38 leading sites across truck and container rental, van lines, moving marketplaces, junk hauling, freight platforms and load boards, load-planning software, calculator libraries and official regulators. For each, record what the page actually shows: tools, form fields, monetization, content types, trust signals. Do not count a site you could not open. Write the findings to `docs/RESEARCH.md` and end with the gap the new site should fill and the fields it must stay out of.

**Check:** 38 or more sites logged from direct reads; trademark conflicts listed; positioning stated in one sentence.

## Phase 1. Concept and information architecture

> Position LoadandGo.com as an independent publisher of free load-planning calculators and guides for three audiences: households moving, pickup and trailer owners, and small carriers. It must not rent trucks, sell boxes or act as mover, broker or carrier. Define the sitemap: home, calculators hub and one page per calculator, guides hub and one page per guide, fuel prices, videos, news, glossary, official resources, quote request, provider sign-up, advertise, support, contests, careers, about and methods, contact, privacy, cookies, terms, disclaimer, 404. Use relative links everywhere so the build works at the custom domain and at the github.io project path.

**Check:** every page has one job and a unique title and description.

## Phase 2. Design system

> Design from the subject's own materials: the yellow door-jamb load placard, the weigh-station ticket and ratchet-strap blue. Palette: placard yellow #FFD21F, ink #1D2327, steel grey #E9EDEE, white, strap blue #1857C4 for actions, red #C8281E only for overload warnings. Type: Barlow Condensed for headings, Barlow for text. The hero is a working truck sizer, not a slogan with a stock image. List calculators as a manifest table, not a card grid. Results print as a "load ticket" with a capacity gauge. Sentence case, no decorative labels, visible keyboard focus, reduced-motion support, responsive to 360 px, print styles for tickets and the checklist.

**Check:** screenshots at 1280 px and 390 px; no horizontal scroll; contrast passes.

## Phase 3. Static generator

> Write `scripts/build.py` (Python, only `markdown` as a dependency) that renders `src/pages/*.html`, `src/guides/*.md` and the calculator definitions in `src/content.json` into `path/index.html` files at the repo root, with a shared layout: top contact bar, sticky header, footer with the non-affiliation notice, AdSense Auto ads script and `google-adsense-account` meta tag in every head, canonical and Open Graph tags, JSON-LD (WebSite, FAQPage, Article). Also write `sitemap.xml`, `robots.txt`, `feed.xml`, the manifest and `404.html`. Calculator forms are generated from field definitions so a new tool needs no HTML.

**Check:** build runs clean; a link checker finds no broken internal links and no unreplaced tokens.

## Phase 4. Calculators

> In `assets/js/tools.js`, implement one function per calculator returning a ticket (label, headline figure, gauge, rows, notes, warning). Build: moving truck size, DIY moving cost, packing boxes, moving checklist, payload, towing capacity, tie-downs (49 CFR 393.106 and 393.110), gravel/soil/mulch loads, trip fuel cost, cubic feet, freight class (13-step density scale in force since July 2025), pallets per trailer, box fit, cost per mile with a load profit check. Inputs persist in local storage, results can be copied, shared as a link and printed. Fuel fields prefill from the latest data file. State every assumption on the page; defaults are placeholders, never presented as market prices.

**Check:** run each tool headless with defaults and with a known worked example; figures match hand calculation.

## Phase 5. Content

> Write one original guide per calculator theme (twelve to start), 500 to 700 words each, plus a how-it-works section, worked example and FAQ on every calculator page, a glossary of 35 terms, a seven-stage moving checklist and 21 rotating daily tips. Cite rules and data by source name. No copied text, no invented statistics, no fake reviews or ratings.

**Check:** every numeric example recomputed; every external link opens.

## Phase 6. Lead generation

> Build `/quote/` as a three-step form: job type and details; where and when; contact and consent. Add a quote call-to-action under every calculator and guide. Add `/partners/` for providers to apply. State plainly that the site is a publisher that introduces providers, may be paid by them, and is not a party to any contract. Deliver every form by AJAX to a form-forwarding service at an inbox that is stored encoded in `config.js` and assembled only at send time. Include a honeypot field and client-side validation.

**Check:** end-to-end form test with a mocked relay; search the built site for the plain inbox address and find nothing.

## Phase 7. Monetization and AdSense readiness

> Put `ads.txt` at the root. Keep ads out of the way of form controls and results. Publish privacy, cookies, terms, disclaimer, about and contact pages that describe advertising cookies, consent for EEA/UK/Swiss visitors, data sharing for quote requests and user rights. Ensure every indexable page has substantial original content and working navigation. Add `/advertise/` with labelled sponsorship options and a sponsor form.

**Check:** walk Google's AdSense programme-policy and site-readiness lists against the built site.

## Phase 8. Support, contests and hiring

> Build `/support/` explaining what reader support funds (operations, new tools, paying contributors, contest prizes, promotion), with payment buttons that appear only when links are set in `config.js` and a pledge form otherwise. Build `/contests/` as a monthly skill contest with free entry, judging criteria and rules; show a prize only when one is confirmed in `config.js`. Build `/careers/` for writers, developers, video makers and trade reviewers.

**Check:** no page promises a payment method, prize or paid role that is not configured.

## Phase 9. Automation

> Write `scripts/update.py` to refresh weekly gasoline and diesel prices (EIA public data), headlines (RSS list in `data/sources.json`) and videos (YouTube channel feeds, resolved from handles, filtered to on-topic titles). Each source is optional; on failure keep the old data and log to `data/status.json`. Add `.github/workflows/refresh.yml` to run update and build every 6 hours and on source changes, then commit to `main`.

**Check:** run the updater against mocked sources including failures; confirm the workflow commit appears.

## Phase 10. Legal notices

> Add the trademark and copyright disclosure: the name is a domain and descriptive phrase; similar marks are owned by unrelated businesses; no affiliation; the site does not offer the goods or services those marks cover; third-party names belong to their owners; how to send a trademark or copyright concern. Put a short version in every footer.

**Check:** disclosure visible on every page; nothing on the site imitates another brand.

## Phase 11. Publish

> Push to `WEBWORKSA1/loadandgo-com` on `main`. Enable GitHub Pages from `main` / root. Confirm the site loads at the Pages address. Then add the custom domain and DNS records, enforce HTTPS, activate the form relay with one test submission, and submit the site and sitemap to AdSense and Search Console.

**Check:** live home page, one calculator, the quote form and `ads.txt` all load over HTTPS.

## Phase 12. Growth backlog

> Next calculators: car shipping cost, storage unit size, moving labor hours, axle weight distribution, trailer hitch drop, ramp length, lumber and sheet-goods load. Next content: state-by-state unsecured-load rules, city parking permits for moving trucks, rental truck spec comparisons from official spec sheets. Next features: saved load lists, printable load plan, embeddable calculators for partner sites with a credit link, Spanish edition.
