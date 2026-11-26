#!/usr/bin/env python3
"""Fetch fresh data for LoadandGo.com. Runs in GitHub Actions on a schedule.

Every source is optional: when one fails, the previous data is kept and the failure
is recorded in data/status.json, so pages never go empty.

Writes data/fuel.json (EIA weekly retail prices), data/news.json (headlines),
data/videos.json (latest uploads from the channels in data/sources.json), data/status.json.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import feedparser

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
NOW = dt.datetime.now(dt.timezone.utc)
STATUS = {"run_at": NOW.isoformat(timespec="seconds"), "sources": []}
TOPIC = re.compile(r"mov|load|truck|trailer|tow|haul|pack|hitch|freight|cargo|storage|strap|tie|box|container|"
                   r"ship|driv|rental|pallet|weigh|payload|fuel|diesel", re.I)


def fetch(url, timeout=30):
    last = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + attempt * 3)
    raise last


def load(name, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def clean(s, words=30):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    parts = s.split(" ")
    return " ".join(parts[:words]).rstrip(",.;:") + "…" if len(parts) > words else s


def to_iso(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return dt.datetime(*t[:6], tzinfo=dt.timezone.utc).isoformat(timespec="seconds")
    return NOW.isoformat(timespec="seconds")


# ---------------------------------------------------------------- fuel
SERIES = {"diesel": "EMD_EPD2D_PTE_{}_DPG", "gas": "EMM_EPMR_PTE_{}_DPG"}
AREAS = {"US": "NUS", "R10": "R10", "R20": "R20", "R30": "R30", "R40": "R40", "R50": "R50"}


def eia_xls(series):
    """Weekly history from EIA's public spreadsheet (no key needed)."""
    import xlrd
    raw = fetch(f"https://www.eia.gov/dnav/pet/hist_xls/{series}w.xls")
    book = xlrd.open_workbook(file_contents=raw)
    rows = []
    for sh in book.sheets():
        if not sh.name.lower().startswith("data"):
            continue
        for r in range(sh.nrows):
            a, b = sh.cell_value(r, 0), sh.cell_value(r, 1)
            if isinstance(a, float) and isinstance(b, float) and a > 20000:
                rows.append([xlrd.xldate_as_datetime(a, book.datemode).date().isoformat(), round(b, 3)])
    return sorted(rows)


def eia_api(series, key):
    """Same series from the EIA open data API, used when an EIA_API_KEY secret is set."""
    q = urllib.parse.urlencode({"api_key": key, "frequency": "weekly", "data[0]": "value", "facets[series][]": series,
                                "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 60})
    rows = json.loads(fetch("https://api.eia.gov/v2/petroleum/pri/gnd/data/?" + q))["response"]["data"]
    return sorted([r["period"], round(float(r["value"]), 3)] for r in rows if r.get("value") is not None)


def update_fuel():
    old = load("fuel.json", {})
    key = os.environ.get("EIA_API_KEY", "").strip()
    latest, prev, history, ok, week = {}, {}, {}, 0, ""
    for kind, pattern in SERIES.items():
        latest[kind], prev[kind] = {}, {}
        for code, area in AREAS.items():
            series = pattern.format(area)
            rec = {"kind": "fuel", "name": f"EIA {kind} {code}", "ok": False, "count": 0}
            try:
                try:
                    rows = eia_api(series, key) if key else eia_xls(series)
                except Exception:  # noqa: BLE001
                    rows = eia_xls(series) if key else []
                    if not rows:
                        raise
                if len(rows) < 2:
                    raise ValueError("no rows parsed")
                latest[kind][code], prev[kind][code] = rows[-1][1], rows[-2][1]
                if code == "US":
                    history[kind] = rows[-60:]
                    week = max(week, rows[-1][0])
                rec.update(ok=True, count=len(rows))
                ok += 1
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)[:160]
                if old.get("latest", {}).get(kind, {}).get(code) is not None:
                    latest[kind][code] = old["latest"][kind][code]
                    if old.get("prev", {}).get(kind, {}).get(code) is not None:
                        prev[kind][code] = old["prev"][kind][code]
            STATUS["sources"].append(rec)
            print(f"fuel {rec['ok']!s:5} {rec['count']:5}  {series}", file=sys.stderr)
        if kind not in history and old.get("history", {}).get(kind):
            history[kind] = old["history"][kind]
    if not ok:
        return  # keep the old file untouched
    save("fuel.json", {"updated": NOW.isoformat(timespec="seconds"), "week": week or old.get("week", ""),
                       "source": "U.S. Energy Information Administration", "latest": latest, "prev": prev, "history": history})


# ---------------------------------------------------------------- news
def update_news(sources):
    old = load("news.json", {"items": []})
    items = []
    for src in sources:
        rec = {"kind": "news", "name": src["name"], "url": src["url"], "ok": False, "count": 0}
        try:
            feed = feedparser.parse(fetch(src["url"]))
            got = []
            for e in feed.entries[:25]:
                title, link, source = clean(e.get("title", "")), e.get("link", ""), src["name"]
                if not title or not link.startswith("http"):
                    continue
                if "news.google.com" in src["url"]:
                    m = re.match(r"^(.*) - ([^-]{2,60})$", title)
                    if m:
                        title, source = m.group(1).strip(), m.group(2).strip()
                if src.get("filter") and not TOPIC.search(title):
                    continue
                got.append({"title": title, "link": link, "source": source, "date": to_iso(e), "cat": src["cat"]})
            items.extend(got)
            rec.update(ok=bool(got), count=len(got))
        except Exception as e:  # noqa: BLE001
            rec["error"] = str(e)[:160]
        STATUS["sources"].append(rec)
        print(f"news {rec['ok']!s:5} {rec['count']:3}  {src['name']}", file=sys.stderr)
    items.extend(old.get("items", []))
    cutoff = NOW - dt.timedelta(days=21)
    seen, per_cat, out = set(), {}, []
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        k = re.sub(r"[^a-z0-9]+", "", it["title"].lower())[:80]
        try:
            when = dt.datetime.fromisoformat(it["date"])
        except ValueError:
            continue
        if not k or k in seen or when < cutoff:
            continue
        if when > NOW + dt.timedelta(hours=6):
            it["date"] = NOW.isoformat(timespec="seconds")
        per_cat[it["cat"]] = per_cat.get(it["cat"], 0) + 1
        if per_cat[it["cat"]] <= 30:
            seen.add(k)
            out.append(it)
    save("news.json", {"updated": NOW.isoformat(timespec="seconds"), "items": out})
    return len(out)


# ---------------------------------------------------------------- videos
def channel_id(src, cache):
    if src.get("channel"):
        return src["channel"]
    h = src["handle"].lstrip("@")
    if h in cache:
        return cache[h]
    page = fetch(f"https://www.youtube.com/@{h}").decode("utf-8", "replace")
    m = (re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"', page)
         or re.search(r'"externalId":"(UC[\w-]{22})"', page) or re.search(r'"channelId":"(UC[\w-]{22})"', page))
    if not m:
        raise ValueError("channel id not found for handle")
    cache[h] = m.group(1)
    return cache[h]


def update_videos(channels):
    old = load("videos.json", {"items": []})
    cache = load("channels.json", {})
    items = []
    for ch in channels:
        rec = {"kind": "video", "name": ch["name"], "ok": False, "count": 0}
        try:
            cid = channel_id(ch, cache)
            feed = feedparser.parse(fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"))
            got = []
            for e in feed.entries[:12]:
                vid = e.get("yt_videoid") or e.get("id", "").split(":")[-1]
                title = clean(e.get("title", ""), 22)
                if not vid or not title or "#shorts" in title.lower() or not TOPIC.search(title):
                    continue
                got.append({"id": vid, "title": title, "channel": ch["name"], "date": to_iso(e)})
            items.extend(got[:4])
            rec.update(ok=bool(got), count=len(got[:4]))
        except Exception as e:  # noqa: BLE001
            rec["error"] = str(e)[:160]
        STATUS["sources"].append(rec)
        print(f"video {rec['ok']!s:5} {rec['count']:3}  {ch['name']}", file=sys.stderr)
    save("channels.json", cache)
    items.extend(old.get("items", []))
    seen, out = set(), []
    for it in sorted(items, key=lambda x: x.get("date", ""), reverse=True):
        if it["id"] not in seen:
            seen.add(it["id"])
            out.append(it)
    save("videos.json", {"updated": NOW.isoformat(timespec="seconds"), "items": out[:36]})
    return len(out[:36])


def main():
    DATA.mkdir(exist_ok=True)
    src = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    update_fuel()
    STATUS["news_items"] = update_news(src["news"])
    STATUS["video_items"] = update_videos(src["videos"])
    STATUS["ok_sources"] = sum(1 for s in STATUS["sources"] if s.get("ok"))
    STATUS["total_sources"] = len(STATUS["sources"])
    save("status.json", STATUS)
    print(f"done: {STATUS['ok_sources']}/{STATUS['total_sources']} sources ok", file=sys.stderr)


if __name__ == "__main__":
    main()
