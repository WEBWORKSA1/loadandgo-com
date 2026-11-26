# LoadandGo.com

Source and published build of **LoadandGo.com**: free load-planning calculators (truck size, DIY moving cost, payload, towing, tie-downs, bulk materials, fuel, pallets, box fit, freight class, cost per mile), guides, a weekly fuel price page, a news wire, a video library, and quote-request, sponsorship, support, contest and hiring funnels. Static HTML, CSS and plain JavaScript, hosted free on GitHub Pages from the `main` branch.

## How it stays fresh

`.github/workflows/refresh.yml` runs every 6 hours, and on every push that changes `scripts/`, `src/`, `assets/` or `data/sources.json`:

1. `scripts/update.py` pulls weekly gasoline and diesel prices from the U.S. Energy Information Administration, headlines from the RSS feeds in `data/sources.json`, and new uploads from the YouTube channels listed there. A failing source is skipped and logged in `data/status.json`; old data is kept so pages never go empty.
2. `scripts/build.py` rebuilds every page from `src/` and `data/`, plus `sitemap.xml`, `robots.txt`, `feed.xml` and the web manifest. The home page tip rotates daily.
3. The workflow commits the result and GitHub Pages republishes.

Run it by hand any time: **Actions > Refresh site content > Run workflow**.

## Layout

| Path | What |
|---|---|
| `src/content.json` | Calculator definitions (fields, explanations, FAQs), all forms, glossary, tips, checklist |
| `src/pages/*.html` | Page bodies with a one-line JSON header (path, title, description) |
| `src/guides/*.md` | Guides with a small front-matter header |
| `assets/js/tools.js` | The maths for every calculator |
| `assets/js/site.js` | Menu, forms, video players, checklist, home page sizer |
| `assets/js/config.js` | Encoded form inbox, optional payment links, contest prize text |
| `data/sources.json` | News feeds and YouTube channels (edit to add or remove) |
| `scripts/` | `update.py`, `build.py`, `og.py`, `encode_inbox.py` |
| `docs/RESEARCH.md` | Trademark check and the 42-site benchmark study |
| `docs/BUILD-PROMPT.md` | The phase-by-phase prompt this site was built from |
| `docs/refresh.yml` | Copy of the workflow, in case it has to be re-created by hand |

Everything else at the repo root is generated output. Edit `src/`, not the generated HTML.

Local build: `pip install feedparser markdown xlrd pillow && python scripts/update.py && python scripts/build.py && python scripts/og.py`, then serve the folder with any static server. All links are relative, so the build works at the custom domain and at `webworksa1.github.io/loadandgo-com/` alike.

## Add a calculator

1. Add an entry to `tools` in `src/content.json` (slug, name, fields, explanation, FAQ).
2. Add a function with the same slug to `T` in `assets/js/tools.js` that returns `{label, big, gauge, rows, notes, warn}`.
3. Push. The workflow rebuilds the site, the list pages and the sitemap.

## One-time setup

1. **Workflow:** if `.github/workflows/refresh.yml` is missing, create it in the GitHub web editor with the contents of `docs/refresh.yml`. Committing it starts the first build.
2. **GitHub Pages:** Settings > Pages > Source: *Deploy from a branch* > `main` / `(root)`.
3. **Custom domain:** Settings > Pages > Custom domain > `loadandgo.com`. At the DNS host, point the apex to GitHub Pages (A records 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and `www` as a CNAME to `webworksa1.github.io`. Tick *Enforce HTTPS* once the certificate is issued. AdSense reads `ads.txt` from the domain root, so the custom domain must be live before applying.
4. **Forms:** every form posts through FormSubmit to the inbox encoded in `assets/js/config.js`. The first submission from the live domain triggers a one-time activation email from FormSubmit; click *Activate* and every later submission is delivered. To change the inbox: `python scripts/encode_inbox.py "new-address"` and paste the output into `config.js`.
5. **AdSense:** the Auto ads script and the `google-adsense-account` meta tag are in the `<head>` of every page and `ads.txt` is at the root. Add the site in AdSense, then turn on the Google-certified consent message under *Privacy & messaging* for EEA, UK and Swiss visitors (the privacy and cookie pages already describe it).
6. **Payments (optional):** paste PayPal, Stripe, Ko-fi or Buy Me a Coffee links into `config.js` > `payments` to show pay buttons on `/support/`. Until then, pledges arrive by form and you reply with a payment link.
7. **Contest prize (optional):** edit `contestPrize` in `config.js` when a prize is confirmed.
8. **EIA key (optional):** fuel prices are read from EIA's public spreadsheets with no key. If that ever fails, add a free EIA API key as the repository secret `EIA_API_KEY` and the refresher uses the API instead.

## Trademark and copyright

"LoadandGo.com" is used only as the domain name and title of this website, and "load and go" in its ordinary descriptive sense. Unrelated businesses hold registered marks built from similar words (for example for truck rental, shipping boxes and truck bodies). This site is not affiliated with any of them and does not rent vehicles, sell boxes or equipment, or provide transport under this name. Original content and code © LoadandGo.com. Headlines and videos belong to their publishers and creators and link to the originals. See `/disclaimer/`.
