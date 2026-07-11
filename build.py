# -*- coding: utf-8 -*-
"""build.py - Statischer SEO-Blog-Generator fuer snice-unterricht.de.
Liest Markdown-Posts (Marketing\\blog\\*.md) + Meta-JSONs (daten/blog_html/<pid>.json),
erzeugt fertiges statisches HTML (GitHub-Pages, .nojekyll). SEO: Title, Meta-Description,
Canonical, OpenGraph, JSON-LD, Sitemap, robots.txt, RSS, interne Verlinkung (Passende
Beitraege), Navigation, Impressum + Ueber-mich, Startseite nach Fach. Cover per eduki-Hotlink.
Aufruf: python build.py"""
import os, re, json, glob, html, datetime
import markdown as md

SITE = "https://snice-unterricht.de"
SITE_NAME = "Snice Unterricht"
TAGLINE = "Materialien, Ideen & Arbeitsblätter für den Unterricht"
SHOP = "https://eduki.com/de/shop/400839"
BLOG = r"C:\Claude-Arbeitsblätter\Marketing\blog"
META = r"C:\Claude-Arbeitsblätter\Marketing\daten\blog_html"
OUT = r"C:\Claude-Arbeitsblätter\snice-unterricht"
POSTS_DIR = os.path.join(OUT, "posts")
INHABER = "Matthias Ender"
EMAIL = "snice.lehrermarktplatz@gmail.com"
# Impressum-Anschrift: MUSS vom Nutzer ergänzt werden (ladungsfähige Anschrift, Pflicht §5 DDG)
ANSCHRIFT = "[Straße & Hausnummer bitte ergänzen]<br>[PLZ Ort bitte ergänzen]"

STOP = set("und der die das ein eine einen im in für mit auf von zu den dem des als auch ist sind "
           "auch homeschooling material arbeitsblatt arbeitsblätter unterricht klasse thema mehr "
           "sowie oder aber wie was wer wann wo bei aus nach über unter durch dass sich".split())

NAV = (f'<nav class="nav"><a href="{{root}}index.html">Start</a>'
       f'<a href="{{root}}index.html#alle">Alle Beiträge</a>'
       f'<a href="{SHOP}" rel="noopener">eduki-Shop</a>'
       f'<a href="{{root}}impressum.html">Impressum</a></nav>')

def slugify(s):
    s = s.lower()
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("é","e"),("è","e")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80] or "post"

def first_para(text):
    for line in text.split("\n"):
        t = line.strip()
        if t and not t.startswith(("#", "!", "---")):
            t = re.sub(r"[*_`>#\[\]]", "", t)
            return re.sub(r"\(https?://[^)]+\)", "", t).strip()
    return TAGLINE

def tokens(p):
    ws = re.findall(r"[a-zäöüß]{4,}", (p["title"] + " " + p["fach"]).lower())
    return set(w for w in ws if w not in STOP)

def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join(BLOG, "*.md"))):
        base = os.path.basename(f)[:-3]; pid = base.split("_", 1)[0]
        raw = open(f, encoding="utf-8", errors="replace").read().strip()
        if not raw: continue
        m = re.match(r"#\s+(.+)", raw)
        if m: title, body_md = m.group(1).strip(), raw[m.end():].strip()
        else: title, body_md = base.split("_", 1)[-1].replace("-", " ").title(), raw
        meta = {}
        mp = os.path.join(META, pid + ".json")
        if os.path.exists(mp):
            try: meta = json.load(open(mp, encoding="utf-8"))
            except Exception: pass
        posts.append({
            "pid": pid, "title": meta.get("titel") or title, "body_md": body_md,
            "desc": first_para(body_md)[:157], "slug": slugify(meta.get("permalink") or base.split("_", 1)[-1] or title),
            "cover": meta.get("cover", ""), "eduki": meta.get("url", ""), "fach": meta.get("fach", ""),
            "klasse": meta.get("klasse", ""), "labels": meta.get("labels", ""),
            "date": datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat(),
        })
    seen = {}
    for p in posts:
        s = p["slug"]
        if s in seen: seen[s] += 1; p["slug"] = f"{s}-{p['pid']}"
        else: seen[s] = 1
    # Related: max. 4 mit größter Token-Überschneidung (+ gleiches Fach bevorzugt)
    tok = {p["pid"]: tokens(p) for p in posts}
    for p in posts:
        me = tok[p["pid"]]
        scored = []
        for q in posts:
            if q["pid"] == p["pid"]: continue
            s = len(me & tok[q["pid"]]) + (2 if p["fach"] and p["fach"] == q["fach"] else 0)
            if s: scored.append((s, q))
        scored.sort(key=lambda x: (-x[0], x[1]["title"]))
        p["related"] = [q for _, q in scored[:4]]
    return posts

def head(title, desc, url, cover, root="", date=None, article=False):
    desc = html.escape(desc.replace("\n", " ").strip()); t = html.escape(title)
    og_img = cover or f"{SITE}/assets/logo.png"
    jsonld = {"@context": "https://schema.org", "@type": "BlogPosting" if article else "WebSite",
              ("headline" if article else "name"): title, "description": desc, "url": url,
              "author": {"@type": "Organization", "name": SITE_NAME},
              "publisher": {"@type": "Organization", "name": SITE_NAME}}
    if article:
        jsonld["datePublished"] = date; jsonld["dateModified"] = date
        if cover: jsonld["image"] = cover
    return f"""<!doctype html>
<html lang="de"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="{SITE_NAME}"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{SITE}/feed.xml">
<link rel="stylesheet" href="{root}assets/style.css">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head><body>
<header class="site"><a class="brand" href="{root}index.html">{SITE_NAME}</a>
<span class="tag">{TAGLINE}</span></header>
{NAV.replace('{root}', root)}
<main>"""

def foot(root=""):
    return f"""</main>
<footer class="site"><p><strong>{SITE_NAME}</strong> — {TAGLINE}</p>
<p>Alle Materialien im <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a> · <a href="{root}impressum.html">Impressum</a> · <a href="{root}ueber-mich.html">Über mich</a></p></footer>
</body></html>"""

def render_post(p):
    url = f"{SITE}/posts/{p['slug']}.html"
    body_html = md.markdown(p["body_md"], extensions=["extra", "sane_lists", "nl2br"])
    cover = f'<img class="cover" src="{html.escape(p["cover"])}" alt="{html.escape(p["title"])}" loading="lazy">' if p["cover"] else ""
    meta_line = " · ".join(x for x in (p["fach"], p["klasse"]) if x)
    rel = ""
    if p["related"]:
        items = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["title"])}</a></li>' for q in p["related"])
        rel = f'<section class="related"><h2>Passende Beiträge</h2><ul>{items}</ul></section>'
    out = head(p["title"], p["desc"], url, p["cover"], "../", p["date"], True)
    out += f"""<article><h1>{html.escape(p['title'])}</h1>
{f'<p class="meta">{html.escape(meta_line)}</p>' if meta_line else ''}{cover}
{body_html}
<p class="cta"><a class="btn" href="{html.escape(p['eduki'] or SHOP)}" rel="noopener">➜ Passendes Material auf eduki ansehen</a></p>
</article>{rel}""" + foot("../")
    open(os.path.join(POSTS_DIR, p["slug"] + ".html"), "w", encoding="utf-8").write(out)
    return url

def render_index(posts):
    out = head(f"{SITE_NAME} — {TAGLINE}", TAGLINE, SITE + "/", "")
    out += f'<h1>{SITE_NAME}</h1>\n<p class="lead">{TAGLINE}. Sachinfos, Unterrichtsideen und fertige Arbeitsblätter für Lehrkräfte – kostenlos lesen, passendes Material direkt auf eduki.</p>\n'
    # nach Fach gruppieren (nur Posts mit Fach)
    faecher = {}
    for p in posts:
        if p["fach"]: faecher.setdefault(p["fach"], []).append(p)
    if faecher:
        out += '<h2>Nach Fach</h2>\n<div class="fachgrid">\n'
        for fach in sorted(faecher):
            top = sorted(faecher[fach], key=lambda x: x["title"])[:6]
            lis = "".join(f'<li><a href="posts/{p["slug"]}.html">{html.escape(p["title"][:70])}</a></li>' for p in top)
            out += f'<div class="fachcard"><h3>{html.escape(fach)} <span class=meta>({len(faecher[fach])})</span></h3><ul>{lis}</ul></div>\n'
        out += '</div>\n'
    out += f'<h2 id="alle">Alle Beiträge ({len(posts)})</h2>\n<ul class="postlist">\n'
    for p in sorted(posts, key=lambda x: x["title"]):
        meta_line = " · ".join(x for x in (p["fach"], p["klasse"]) if x)
        out += f'<li><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a>{f" <span class=meta>{html.escape(meta_line)}</span>" if meta_line else ""}</li>\n'
    out += "</ul>" + foot()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)

def render_page(slug, title, inner):
    out = head(title, title, f"{SITE}/{slug}.html", "") + inner + foot()
    open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8").write(out)

def write_feed(posts):
    latest = sorted(posts, key=lambda x: x["date"], reverse=True)[:50]
    items = ""
    for p in latest:
        items += (f"<item><title>{html.escape(p['title'])}</title>"
                  f"<link>{SITE}/posts/{p['slug']}.html</link>"
                  f"<guid>{SITE}/posts/{p['slug']}.html</guid>"
                  f"<description>{html.escape(p['desc'])}</description></item>\n")
    feed = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f'<title>{SITE_NAME}</title><link>{SITE}/</link>'
            f'<description>{TAGLINE}</description><language>de</language>\n{items}</channel></rss>')
    open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8").write(feed)

def write_meta(posts):
    u = [f"<url><loc>{SITE}/</loc></url>", f"<url><loc>{SITE}/impressum.html</loc></url>",
         f"<url><loc>{SITE}/ueber-mich.html</loc></url>"]
    for p in posts:
        u.append(f"<url><loc>{SITE}/posts/{p['slug']}.html</loc><lastmod>{p['date']}</lastmod></url>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(u) + "\n</urlset>")
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    posts = load_posts()
    for p in posts: render_post(p)
    render_index(posts)
    render_page("impressum", "Impressum", f"""<h1>Impressum</h1>
<p>Angaben gemäß § 5 DDG:</p>
<p>{INHABER}<br>{ANSCHRIFT}</p>
<p><strong>Kontakt:</strong><br>E-Mail: {EMAIL}</p>
<p><strong>Verantwortlich für den Inhalt</strong> nach § 18 Abs. 2 MStV: {INHABER} (Anschrift wie oben).</p>
<p>Dieser Blog verweist auf eigene Unterrichtsmaterialien im <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a>.</p>""")
    render_page("ueber-mich", "Über mich", f"""<h1>Über mich</h1>
<p>Hinter <strong>{SITE_NAME}</strong> steht {INHABER} – ich erstelle praxiserprobte Unterrichtsmaterialien
für Lehrkräfte: Arbeitsblätter, Lückentexte und Hörverständnis-Übungen inklusive Musterlösungen.</p>
<p>In diesem Blog teile ich Sachinformationen, Unterrichtsideen und methodische Anregungen zu vielen Themen.
Passende fertige Materialien findest du direkt in meinem <a href="{SHOP}" rel="noopener">Shop auf eduki</a>.</p>""")
    write_feed(posts); write_meta(posts)
    with_eduki = sum(1 for p in posts if p["eduki"])
    with_fach = sum(1 for p in posts if p["fach"])
    print(f"OK: {len(posts)} Posts, {with_eduki} mit eduki-Link, {with_fach} mit Fach, +Impressum/Über-mich/RSS/interne Verlinkung.")

if __name__ == "__main__":
    main()
