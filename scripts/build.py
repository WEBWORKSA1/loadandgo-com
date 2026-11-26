#!/usr/bin/env python3
"""Build LoadandGo.com: turns src/ and data/ into static pages at the repo root.

Every link is relative, so the same build works at a custom domain and at
username.github.io/repo/. Run after scripts/update.py.
"""
import datetime as dt
import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC, DATA = ROOT / "src", ROOT / "data"
SITE, NAME, PUB = "https://loadandgo.com", "LoadandGo.com", "ca-pub-6620975821265271"
NOW = dt.datetime.now(dt.timezone.utc)
TODAY = NOW.date()
C = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
E = html.escape
URLS = []
REGIONS = {"US": "U.S. average", "R10": "East Coast", "R20": "Midwest", "R30": "Gulf Coast",
           "R40": "Rocky Mountain", "R50": "West Coast"}


def load(name, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


FUEL = load("fuel.json", {})
NEWS = load("news.json", {"items": []})
VIDEOS = load("videos.json", {"items": []})
TOOLS = C["tools"]
TOOL = {t["slug"]: t for t in TOOLS}


def nice_date(iso):
    try:
        d = dt.date.fromisoformat(iso[:10])
        return f"{d.day} {d.strftime('%b %Y')}"
    except Exception:  # noqa: BLE001
        return ""


# ------------------------------------------------------------------ guides
def read_guides():
    out = []
    for p in sorted((SRC / "guides").glob("*.md")):
        head, _, body = p.read_text(encoding="utf-8").partition("\n\n")
        meta = dict(l.split(": ", 1) for l in head.splitlines() if ": " in l)
        meta["slug"] = p.stem
        meta["html"] = markdown.markdown(body, extensions=["tables"])
        meta["mins"] = max(2, round(len(body.split()) / 220))
        out.append(meta)
    return sorted(out, key=lambda g: int(g.get("order", 99)))


GUIDES = read_guides()


# ------------------------------------------------------------------ components
def lead():
    return ('<aside class="lead"><div><h2>Rather have someone else lift it?</h2>'
            '<p>Tell us what is moving and where. We read every request and introduce you to movers, '
            'haulers or carriers that fit the job. Free, and you choose who to talk to.</p></div>'
            '<a class="btn" href="{{root}}quote/">Request free quotes</a></aside>')


def tools_list(limit=None):
    rows = []
    for t in TOOLS[:limit]:
        rows.append(f'<tr><th scope="row"><a href="{{{{root}}}}tools/{t["slug"]}/">{E(t["name"])}</a></th>'
                    f'<td>{E(t["q"])}</td><td class="grp">{E(t["group"])}</td></tr>')
    return ('<table class="manifest"><thead><tr><th scope="col">Calculator</th><th scope="col">Answers</th>'
            '<th scope="col">For</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


def guides_list(limit=None):
    items = []
    for g in GUIDES[:limit]:
        items.append(f'<li><a href="{{{{root}}}}guides/{g["slug"]}/">{E(g["title"])}</a>'
                     f'<p>{E(g["desc"])}</p><span>{g["mins"]} min read</span></li>')
    return '<ul class="guide-list">' + "".join(items) + "</ul>"


def fuel_bits():
    lat, prev = FUEL.get("latest", {}), FUEL.get("prev", {})
    out = {}
    for kind in ("diesel", "gas"):
        v, p = lat.get(kind, {}).get("US"), prev.get(kind, {}).get("US")
        if v is None:
            continue
        delta = ""
        if p is not None:
            d = v - p
            delta = "unchanged from the week before" if abs(d) < 0.0005 else (
                f'{"up" if d > 0 else "down"} {abs(d) * 100:.1f}¢ from the week before')
        out[kind] = (v, delta)
    return out


def brief():
    parts = []
    fb = fuel_bits()
    if fb:
        cells = "".join(
            f'<div><p class="num">${v:.3f}</p><p>{"Diesel" if k == "diesel" else "Regular gasoline"} per gallon, '
            f'U.S. average{", " + d if d else ""}</p></div>' for k, (v, d) in fb.items())
        parts.append(f'<div class="brief-fuel">{cells}<p class="src">Week of {nice_date(FUEL.get("week", ""))}. '
                     f'Source: U.S. Energy Information Administration. <a href="{{{{root}}}}fuel-prices/">All regions</a></p></div>')
    tip = C["tips"][TODAY.toordinal() % len(C["tips"])]
    parts.append(f'<div class="brief-tip"><h3>Today\'s loading tip</h3><p>{tip}</p></div>')
    heads = NEWS.get("items", [])[:5]
    if heads:
        lis = "".join(f'<li><a href="{E(h["link"])}" rel="nofollow noopener" target="_blank">{E(h["title"])}</a> '
                      f'<span>{E(h["source"])}</span></li>' for h in heads)
        parts.append(f'<div class="brief-news"><h3>On the wire</h3><ul>{lis}</ul>'
                     f'<p><a href="{{{{root}}}}news/">More moving, towing and freight headlines</a></p></div>')
    return '<div class="brief">' + "".join(parts) + "</div>"


def fuel_table():
    lat, prev = FUEL.get("latest", {}), FUEL.get("prev", {})
    if not lat:
        return '<p class="empty">Prices load on the next data refresh.</p>'
    rows = []
    for code, label in REGIONS.items():
        tds = ""
        for kind in ("gas", "diesel"):
            v, p = lat.get(kind, {}).get(code), prev.get(kind, {}).get(code)
            if v is None:
                tds += "<td>n/a</td><td></td>"
                continue
            ch = ""
            if p is not None:
                d = (v - p) * 100
                ch = "0.0¢" if abs(d) < 0.05 else f'{"+" if d > 0 else "−"}{abs(d):.1f}¢'
            tds += f"<td>${v:.3f}</td><td class='chg'>{ch}</td>"
        rows.append(f'<tr><th scope="row">{label}</th>{tds}</tr>')
    return ('<table class="data"><thead><tr><th scope="col">Region</th><th scope="col">Regular gasoline</th>'
            '<th scope="col">Week change</th><th scope="col">Diesel</th><th scope="col">Week change</th></tr></thead><tbody>'
            + "".join(rows) + f'</tbody></table><p class="src">Dollars per gallon, week of {nice_date(FUEL.get("week", ""))}. '
            'Source: U.S. Energy Information Administration weekly retail survey.</p>')


def fuel_chart():
    hist = FUEL.get("history", {})
    series = {k: hist.get(k, [])[-52:] for k in ("diesel", "gas")}
    if not all(len(s) > 3 for s in series.values()):
        return ""
    vals = [v for s in series.values() for _, v in s]
    lo, hi = min(vals) - 0.1, max(vals) + 0.1
    W, H, L, R, T, B = 760, 300, 46, 120, 14, 30

    def pts(s):
        n = len(s) - 1
        return [(L + (W - L - R) * i / n, T + (H - T - B) * (1 - (v - lo) / (hi - lo))) for i, (_, v) in enumerate(s)]

    g = []
    for i in range(5):
        val = lo + (hi - lo) * i / 4
        y = T + (H - T - B) * (1 - i / 4)
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                 f'<text x="{L - 8}" y="{y + 4:.1f}" text-anchor="end">${val:.2f}</text>')
    for kind, label in (("diesel", "Diesel"), ("gas", "Gasoline")):
        p = pts(series[kind])
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in p)
        g.append(f'<polyline class="ln {kind}" points="{path}"/>'
                 f'<text class="end" x="{p[-1][0] + 8:.1f}" y="{p[-1][1] + 4:.1f}">{label} ${series[kind][-1][1]:.2f}</text>')
    first, last = series["diesel"][0][0], series["diesel"][-1][0]
    g.append(f'<text x="{L}" y="{H - 8}">{nice_date(first)}</text>'
             f'<text x="{W - R}" y="{H - 8}" text-anchor="end">{nice_date(last)}</text>')
    return (f'<figure class="chart"><svg viewBox="0 0 {W} {H}" role="img" aria-label="U.S. average diesel and regular '
            f'gasoline prices over the past year">{"".join(g)}</svg><figcaption>U.S. average retail price per gallon, '
            'weekly, past 12 months.</figcaption></figure>')


def videos_grid(limit=None):
    items = VIDEOS.get("items", [])[:limit]
    if not items:
        return '<p class="empty">Videos load on the next data refresh.</p>'
    cards = []
    for v in items:
        cards.append(
            f'<article class="vid"><button type="button" class="vid-play" data-yt="{E(v["id"])}" '
            f'aria-label="Play video: {E(v["title"])}"><img loading="lazy" width="480" height="360" alt="" '
            f'src="https://i.ytimg.com/vi/{E(v["id"])}/hqdefault.jpg"><span>Play</span></button>'
            f'<h3>{E(v["title"])}</h3><p>{E(v["channel"])} on YouTube'
            f'{", " + nice_date(v["date"]) if v.get("date") else ""}</p></article>')
    return '<div class="vid-grid">' + "".join(cards) + "</div>"


def news_list():
    items = NEWS.get("items", [])
    if not items:
        return '<p class="empty">Headlines load on the next data refresh.</p>'
    out = []
    for cat, label in C["news_cats"]:
        its = [i for i in items if i.get("cat") == cat][:14]
        if not its:
            continue
        lis = "".join(
            f'<li><a href="{E(i["link"])}" rel="nofollow noopener" target="_blank">{E(i["title"])}</a>'
            f'<span>{E(i["source"])}, {nice_date(i["date"])}</span></li>' for i in its)
        out.append(f'<section><h2 id="{cat}">{E(label)}</h2><ul class="wire">{lis}</ul></section>')
    return "".join(out)


def glossary():
    terms = sorted(C["glossary"], key=lambda t: t[0].lower())
    return '<dl class="glossary">' + "".join(
        f'<dt id="{re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")}">{E(t)}</dt><dd>{d}</dd>' for t, d in terms) + "</dl>"


def checklist():
    out = ['<div class="checklist" data-checklist="moving"><p class="progress"><span class="bar"><i></i></span>'
           '<span class="count"></span></p>']
    n = 0
    for title, items in C["checklist"]:
        out.append(f"<h2>{E(title)}</h2><ul>")
        for it in items:
            n += 1
            out.append(f'<li><label><input type="checkbox" data-check="c{n}"> <span>{it}</span></label></li>')
        out.append("</ul>")
    out.append('<p class="actions"><button type="button" class="btn alt" onclick="window.print()">Print checklist</button> '
               '<button type="button" class="btn alt" data-reset>Clear all ticks</button></p></div>')
    return "".join(out)


def form(fid):
    f = C["forms"][fid]
    steps = any(x[2] == "step" for x in f["fields"])
    out = [f'<form class="form js-form{" steps" if steps else ""}" data-form="{fid}" data-subject="{E(f["subject"])}" '
           f'data-done="{E(f["done"])}" novalidate>']
    open_fs = False
    for x in f["fields"]:
        n, label, t = x[0], x[1], x[2]
        req = len(x) > 3 and x[3]
        ex = x[4] if len(x) > 4 else ""
        if t == "step":
            if open_fs:
                out.append("</fieldset>")
            out.append(f"<fieldset><legend>{E(label)}</legend>")
            open_fs = True
            continue
        r = " required" if req else ""
        fid_ = f"{fid}-{n}"
        if t == "check":
            out.append(f'<label class="check"><input type="checkbox" name="{n}" value="yes"{r}> <span>{label}</span></label>')
            continue
        lab = f'<label for="{fid_}">{E(label)}{"" if req else " <small>optional</small>"}</label>'
        if t == "select":
            ctl = (f'<select id="{fid_}" name="{n}"{r}><option value="">Choose one</option>'
                   + "".join(f"<option>{E(o)}</option>" for o in ex) + "</select>")
        elif t == "textarea":
            ctl = f'<textarea id="{fid_}" name="{n}" rows="4"{r} placeholder="{E(ex)}"></textarea>'
        else:
            ctl = f'<input id="{fid_}" name="{n}" type="{t}"{r} placeholder="{E(ex)}">'
        out.append(f'<div class="field">{lab}{ctl}</div>')
    if open_fs:
        out.append("</fieldset>")
    out.append('<input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">')
    out.append(f'<div class="form-foot"><button class="btn" type="submit">{E(f["button"])}</button>'
               '<p class="form-msg" role="status"></p></div></form>')
    return "".join(out)


COMPONENTS = {
    "lead": lead, "tools_list": tools_list, "tools_top": lambda: tools_list(7), "guides_list": guides_list,
    "guides_top": lambda: guides_list(4), "brief": brief, "fuel_table": fuel_table, "fuel_chart": fuel_chart,
    "videos_grid": videos_grid, "videos_top": lambda: videos_grid(3), "news_list": news_list,
    "glossary": glossary, "checklist": checklist,
    "updated": lambda: f"{TODAY.day} {TODAY.strftime('%B %Y')}", "year": lambda: str(TODAY.year),
    "tool_count": lambda: str(len(TOOLS)), "guide_count": lambda: str(len(GUIDES)),
}


def render(body, root):
    def sub(m):
        k = m.group(1)
        if k == "root":
            return root
        if k.startswith("form:"):
            return form(k[5:])
        fn = COMPONENTS.get(k)
        return fn() if fn else m.group(0)
    for _ in range(3):
        body = re.sub(r"\{\{([\w:-]+)\}\}", sub, body)
    return body


# ------------------------------------------------------------------ layout
NAV = [("tools/", "Calculators"), ("guides/", "Guides"), ("fuel-prices/", "Fuel prices"),
       ("videos/", "Videos"), ("news/", "News")]
FOOT = [
    ("Plan a load", [("tools/", "All calculators"), ("tools/moving-checklist/", "Moving checklist"),
                     ("guides/", "Guides"), ("glossary/", "Glossary"), ("resources/", "Official resources")]),
    ("Stay current", [("fuel-prices/", "Fuel prices"), ("news/", "News wire"), ("videos/", "Videos"),
                      ("contests/", "Contests")]),
    ("Work with us", [("quote/", "Request quotes"), ("partners/", "For movers and carriers"),
                      ("advertise/", "Advertise and sponsor"), ("support/", "Support the site"),
                      ("careers/", "Join the crew")]),
    ("About", [("about/", "About and methods"), ("contact/", "Contact"), ("privacy/", "Privacy"),
               ("cookies/", "Cookies and ads"), ("terms/", "Terms"), ("disclaimer/", "Disclaimer and trademarks")]),
]


def layout(path, title, desc, body, root, head="", og_type="website"):
    canon = SITE + "/" + (path + "/" if path and path != "404" else "")
    full = title if NAME in title else f"{title} | {NAME}"
    nav = "".join(f'<a href="{root}{h}"{" aria-current=\"page\"" if path and h.startswith(path.split("/")[0] + "/") else ""}>{t}</a>'
                  for h, t in NAV)
    foot = "".join("<div><h2>" + h + "</h2><ul>" + "".join(f'<li><a href="{root}{u}">{t}</a></li>' for u, t in links)
                   + "</ul></div>" for h, links in FOOT)
    base = ""
    if path == "404":
        base = ("<script>document.write('<base href=\"'+(location.hostname.indexOf('github.io')>-1?'/'+"
                "location.pathname.split('/')[1]+'/':'/')+'\">')</script>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{base}<title>{E(full)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FFD21F">
<meta name="google-adsense-account" content="{PUB}">
<link rel="icon" href="{root}assets/img/icon.svg" type="image/svg+xml">
<link rel="manifest" href="{root}manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{NAME} guides" href="{root}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/site.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUB}" crossorigin="anonymous"></script>
{head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<a class="topbar" href="https://web.works/contact" rel="noopener">Contact, if you are interested in this website / domain name / sponsorship / advertisement / partnership</a>
<header class="site-head">
<div class="wrap">
<a class="logo" href="{root}" aria-label="{NAME} home"><img src="{root}assets/img/icon.svg" alt="" width="34" height="34"><span>LoadandGo<i>.com</i></span></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
<nav id="nav" aria-label="Main">{nav}<a class="btn small" href="{root}quote/">Request quotes</a></nav>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
<div class="wrap">
<div class="foot-cols">{foot}</div>
<p class="fine">{NAME} is an independent publisher of free load-planning calculators and guides. We are not a moving company, truck rental company, freight broker or carrier, and we do not sell boxes or equipment. "Load and go" is used here as an everyday phrase and as the name of this website only; the site is not affiliated with, sponsored by or endorsed by any business or trademark owner using similar words, or by any brand, agency or publisher mentioned or linked. Calculator results are planning estimates, not professional or legal advice. Always confirm ratings on your own vehicle, equipment and paperwork. <a href="{root}disclaimer/">Full disclaimer and trademark notice</a>.</p>
<p class="fine">© {TODAY.year} {NAME}. Original text, calculators and design are protected by copyright. Headlines and videos belong to their publishers and creators and link to the originals. Pages rebuilt {TODAY.day} {TODAY.strftime('%B %Y')}.</p>
</div>
</footer>
<div class="cookie" hidden><p>This site uses cookies for ads and to remember your calculator inputs on this device. <a href="{root}cookies/">How it works</a></p><button type="button" class="btn small">OK</button></div>
<script src="{root}assets/js/config.js"></script>
<script src="{root}assets/js/site.js" defer></script>
</body>
</html>
"""


def write(path, title, desc, body, head="", og_type="website", tail=""):
    root = "" if path in ("", "404") else "../" * (path.count("/") + 1)
    page = layout(path, title, desc, render(body, root) + tail.replace("{{root}}", root), root, head, og_type)
    out = ROOT / "404.html" if path == "404" else ROOT / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    if path != "404":
        URLS.append(path + "/" if path else "")


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


# ------------------------------------------------------------------ pages
def build_pages():
    for p in sorted((SRC / "pages").glob("*.html")):
        first, _, body = p.read_text(encoding="utf-8").partition("\n")
        meta = json.loads(first.strip()[4:-3])
        head = ""
        if meta["path"] == "":
            head = ld({"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/",
                       "description": meta["desc"]})
        write(meta["path"], meta["title"], meta["desc"], body, head)


def field_html(slug, f):
    n, label, t = f[0], f[1], f[2]
    if t == "h":
        return f'<h3 class="calc-h">{E(label)}</h3>'
    default = f[3] if len(f) > 3 else ""
    unit = f[4] if len(f) > 4 else ""
    extra = f[5] if len(f) > 5 else ""
    fid = f"f-{n}"
    if t == "c":
        return (f'<label class="check"><input type="checkbox" name="{n}" id="{fid}"{" checked" if default else ""}> '
                f'<span>{E(label)}</span></label>')
    hint = f'<small id="{fid}-h">{E(extra)}</small>' if isinstance(extra, str) and extra else ""
    desc = f' aria-describedby="{fid}-h"' if hint else ""
    if t == "s":
        opts = "".join(f'<option value="{E(str(v))}"{" selected" if str(v) == str(default) else ""}>{E(l)}</option>'
                       for v, l in extra)
        ctl = f'<select name="{n}" id="{fid}">{opts}</select>'
        hint = ""
    elif t == "t":
        ctl = f'<input type="text" name="{n}" id="{fid}" value="{E(str(default))}"{desc}>'
    else:
        ctl = (f'<span class="unit"><input type="number" inputmode="decimal" min="0" step="any" name="{n}" id="{fid}" '
               f'value="{default}"{desc}>{f"<i>{E(unit)}</i>" if unit else ""}</span>')
    return f'<div class="field"><label for="{fid}">{E(label)}</label>{ctl}{hint}</div>'


def build_tools():
    fuel_js = "<script>window.LG_FUEL=" + json.dumps(FUEL.get("latest", {})) + ";</script>"
    for t in TOOLS:
        slug = t["slug"]
        if t.get("custom"):
            calc = "{{" + t["custom"] + "}}"
        else:
            fields = "".join(field_html(slug, f) for f in t["fields"])
            calc = (f'<div class="calc"><form class="calc-form" data-tool="{slug}" novalidate>{fields}'
                    '<p class="calc-note">Results update as you type and stay on this device.</p></form>'
                    '<section id="ticket" class="ticket" aria-live="polite" aria-label="Result">'
                    '<p class="tk-wait">Turn on JavaScript to run this calculator.</p></section></div>')
        faq = "".join(f"<dt>{E(q)}</dt><dd>{a}</dd>" for q, a in t.get("faq", []))
        rel = "".join(f'<li><a href="{{{{root}}}}tools/{s}/">{E(TOOL[s]["name"])}</a></li>' for s in t.get("related", []))
        g = next((x for x in GUIDES if x["slug"] == t.get("guide")), None)
        guide = (f'<p class="readnext">Read the guide: <a href="{{{{root}}}}guides/{g["slug"]}/">{E(g["title"])}</a></p>'
                 if g else "")
        body = (f'<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="{{{{root}}}}tools/">Calculators</a> '
                f'<span>{E(t["group"])}</span></nav><h1>{E(t["name"])}</h1><p class="lede">{E(t["desc"])}</p>{calc}'
                f'<div class="prose"><h2>How this works</h2>{t["how"]}{guide}'
                + (f'<h2>Questions people ask</h2><dl class="faq">{faq}</dl>' if faq else "")
                + (f'<h2>Related calculators</h2><ul class="rel">{rel}</ul>' if rel else "")
                + '</div>{{lead}}</div>')
        head = ""
        if t.get("faq"):
            head = ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
                for q, a in t["faq"]]})
        tail = "" if t.get("custom") else fuel_js + '<script src="{{root}}assets/js/tools.js" defer></script>'
        write(f"tools/{slug}", t["title"], t["desc"], body, head, tail=tail)


def build_guides():
    for i, g in enumerate(GUIDES):
        t = TOOL.get(g.get("tool", ""))
        box = (f'<aside class="toolbox"><p>Run the numbers for your own load.</p>'
               f'<a class="btn" href="{{{{root}}}}tools/{t["slug"]}/">Open the {E(t["short"].lower())} calculator</a></aside>'
               if t else "")
        nxt = GUIDES[(i + 1) % len(GUIDES)]
        body = (f'<div class="wrap narrow"><nav class="crumbs" aria-label="Breadcrumb"><a href="{{{{root}}}}guides/">Guides</a></nav>'
                f'<article class="prose"><h1>{E(g["title"])}</h1><p class="lede">{E(g["desc"])}</p>'
                f'<p class="byline">By the {NAME} editors. Reviewed {nice_date(g.get("date", TODAY.isoformat()))}. {g["mins"]} min read.</p>'
                f'{g["html"]}{box}<p class="readnext">Next guide: <a href="{{{{root}}}}guides/{nxt["slug"]}/">{E(nxt["title"])}</a></p>'
                '</article>{{lead}}</div>')
        head = ld({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
                   "dateModified": g.get("date", TODAY.isoformat()), "author": {"@type": "Organization", "name": NAME},
                   "publisher": {"@type": "Organization", "name": NAME}, "mainEntityOfPage": f'{SITE}/guides/{g["slug"]}/'})
        write(f'guides/{g["slug"]}', g["title"], g["desc"], body, head, og_type="article")


def build_meta():
    sm = "".join(f"<url><loc>{SITE}/{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n" for u in sorted(set(URLS)))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + sm + "</urlset>\n",
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    items = "".join(
        f"<item><title>{E(g['title'])}</title><link>{SITE}/guides/{g['slug']}/</link><guid>{SITE}/guides/{g['slug']}/</guid>"
        f"<description>{E(g['desc'])}</description></item>\n" for g in GUIDES)
    (ROOT / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{NAME} guides</title><link>{SITE}/</link>'
        f"<description>Load planning guides for movers, haulers and small carriers.</description>\n{items}</channel></rss>\n",
        encoding="utf-8")
    (ROOT / "manifest.webmanifest").write_text(json.dumps({
        "name": NAME, "short_name": "LoadandGo", "start_url": "./", "display": "standalone",
        "background_color": "#E9EDEE", "theme_color": "#FFD21F",
        "icons": [{"src": "assets/img/icon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_pages()
    build_tools()
    build_guides()
    build_meta()
    print(f"built {len(URLS)} pages")
