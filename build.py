# -*- coding: utf-8 -*-
"""build.py - Statischer SEO-Blog-Generator fuer snice-unterricht.de.
Liest 1012 Markdown-Posts (C:\\...\\Marketing\\blog\\*.md) + Meta-JSONs
(daten/blog_html/<pid>.json) und erzeugt fertiges statisches HTML (GitHub-Pages-tauglich,
kein Build noetig, .nojekyll). SEO: Title, Meta-Description, Canonical, OpenGraph,
JSON-LD BlogPosting, Sitemap, robots.txt, RSS. Cover per eduki-Hotlink (Repo bleibt klein).
Aufruf: python build.py
"""
import os, re, json, glob, html, datetime
import markdown as md

SITE = "https://snice-unterricht.de"
SITE_NAME = "Snice Unterricht"
TAGLINE = "Materialien, Ideen & Arbeitsblätter für den Unterricht"
SHOP = "https://eduki.com/de/shop/400839"  # Snice-Shop (Fallback-CTA)
BLOG = r"C:\Claude-Arbeitsblätter\Marketing\blog"
META = r"C:\Claude-Arbeitsblätter\Marketing\daten\blog_html"
OUT = r"C:\Claude-Arbeitsblätter\snice-unterricht"
POSTS_DIR = os.path.join(OUT, "posts")

def slugify(s):
    s = s.lower()
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("é","e"),("è","e")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "post"

def first_para(text):
    for line in text.split("\n"):
        t = line.strip()
        if t and not t.startswith("#") and not t.startswith("!") and not t.startswith("---"):
            t = re.sub(r"[*_`>#\[\]]", "", t)
            t = re.sub(r"\(https?://[^)]+\)", "", t)
            return t.strip()
    return TAGLINE

def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join(BLOG, "*.md"))):
        base = os.path.basename(f)[:-3]
        pid = base.split("_", 1)[0]
        raw = open(f, encoding="utf-8", errors="replace").read().strip()
        if not raw:
            continue
        # Titel = erste H1, Body = Rest ohne diese H1
        m = re.match(r"#\s+(.+)", raw)
        if m:
            title = m.group(1).strip()
            body_md = raw[m.end():].strip()
        else:
            title = base.split("_", 1)[-1].replace("-", " ").title()
            body_md = raw
        meta = {}
        mp = os.path.join(META, pid + ".json")
        if os.path.exists(mp):
            try: meta = json.load(open(mp, encoding="utf-8"))
            except Exception: meta = {}
        slug = slugify(meta.get("permalink") or base.split("_", 1)[-1] or title)
        posts.append({
            "pid": pid, "title": meta.get("titel") or title, "body_md": body_md,
            "desc": first_para(body_md)[:157],
            "slug": slug, "cover": meta.get("cover", ""),
            "eduki": meta.get("url", ""), "fach": meta.get("fach", ""),
            "klasse": meta.get("klasse", ""), "labels": meta.get("labels", ""),
            "date": datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat(),
        })
    # eindeutige Slugs
    seen = {}
    for p in posts:
        s = p["slug"]
        if s in seen:
            seen[s] += 1; p["slug"] = f"{s}-{p['pid']}"
        else:
            seen[s] = 1
    return posts

def head(title, desc, url, cover, date=None, article=False):
    desc = html.escape(desc.replace("\n", " ").strip())
    t = html.escape(title)
    og_img = cover or f"{SITE}/assets/logo.png"
    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting" if article else "WebSite",
        "headline" if article else "name": title,
        "description": desc, "url": url,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
    }
    if article:
        jsonld["datePublished"] = date; jsonld["dateModified"] = date
        if cover: jsonld["image"] = cover
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{'../' if article else ''}assets/style.css">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<header class="site"><a class="brand" href="{'../' if article else ''}index.html">{SITE_NAME}</a>
<span class="tag">{TAGLINE}</span></header>
<main>"""

FOOT = f"""</main>
<footer class="site">
<p><strong>{SITE_NAME}</strong> — {TAGLINE}</p>
<p>Alle Materialien im <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a>.</p>
</footer>
</body></html>"""

def render_post(p):
    url = f"{SITE}/posts/{p['slug']}.html"
    body_html = md.markdown(p["body_md"], extensions=["extra", "sane_lists", "nl2br"])
    cta_url = p["eduki"] or SHOP
    cover = f'<img class="cover" src="{html.escape(p["cover"])}" alt="{html.escape(p["title"])}" loading="lazy">' if p["cover"] else ""
    meta_line = " · ".join([x for x in (p["fach"], p["klasse"]) if x])
    out = head(p["title"], p["desc"], url, p["cover"], p["date"], article=True)
    out += f"""<article>
<h1>{html.escape(p['title'])}</h1>
{f'<p class="meta">{html.escape(meta_line)}</p>' if meta_line else ''}
{cover}
{body_html}
<p class="cta"><a class="btn" href="{html.escape(cta_url)}" rel="noopener">➜ Passendes Material auf eduki ansehen</a></p>
</article>"""
    out += FOOT
    open(os.path.join(POSTS_DIR, p["slug"] + ".html"), "w", encoding="utf-8").write(out)
    return url

def render_index(posts):
    out = head(f"{SITE_NAME} — {TAGLINE}", TAGLINE, SITE + "/", "")
    out += f'<h1>{SITE_NAME}</h1>\n<p class="lead">{TAGLINE}. Sachinfos, Unterrichtsideen und fertige Arbeitsblätter für Lehrkräfte.</p>\n<ul class="postlist">\n'
    for p in posts:
        meta_line = " · ".join([x for x in (p["fach"], p["klasse"]) if x])
        out += f'<li><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a>{f" <span class=meta>{html.escape(meta_line)}</span>" if meta_line else ""}</li>\n'
    out += "</ul>" + FOOT
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)

def write_sitemap(posts):
    u = [f"<url><loc>{SITE}/</loc></url>"]
    for p in posts:
        u.append(f"<url><loc>{SITE}/posts/{p['slug']}.html</loc><lastmod>{p['date']}</lastmod></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(u) + "\n</urlset>"
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(OUT, "CNAME"), "w", encoding="utf-8").write("snice-unterricht.de\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    posts = load_posts()
    for p in posts:
        render_post(p)
    render_index(posts)
    write_sitemap(posts)
    with_eduki = sum(1 for p in posts if p["eduki"])
    print(f"OK: {len(posts)} Posts generiert, davon {with_eduki} mit eduki-Materiallink.")
    print(f"Ausgabe: {OUT}")

if __name__ == "__main__":
    main()
