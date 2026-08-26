# -*- coding: utf-8 -*-
"""build.py - Statischer Generator fuer snice-unterricht.eu.
Apple-inspirierte Startseite = Material-Finder (Sofortsuche + Fach/Klasse-Filter + Scroll-Reveal,
alles vanilla JS, progressiv: funktioniert auch ohne JS). Dazu 1012 SEO-Artikelseiten,
Sitemap, robots.txt, RSS, Impressum, Ueber-mich. Cover per eduki-Hotlink. Aufruf: python build.py"""
import os, re, json, glob, html, datetime, collections
import markdown as md

SITE = "https://snice-unterricht.eu"
SITE_NAME = "Snice Unterricht"
TAGLINE = "Materialien, die den Unterricht leichter machen"
SHOP = "https://eduki.com/de/shop/400839"
BLOG = r"C:\Claude-Arbeitsblätter\Marketing\blog"
META = r"C:\Claude-Arbeitsblätter\Marketing\daten\blog_html"
OUT = r"C:\Claude-Arbeitsblätter\snice-unterricht"
POSTS_DIR = os.path.join(OUT, "posts")
INHABER = "Matthias Ender"
EMAIL = "snice.lehrermarktplatz@gmail.com"
ANSCHRIFT = "[Straße & Hausnummer bitte ergänzen]<br>[PLZ Ort bitte ergänzen]"

STOP = set("und der die das ein eine einen im in für mit auf von zu den dem des als auch ist sind "
           "auch homeschooling material arbeitsblatt arbeitsblätter unterricht klasse thema mehr "
           "sowie oder aber wie was wer wann wo bei aus nach über unter durch dass sich".split())


def slugify(s):
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), ("é", "e"), ("è", "e")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80] or "post"


def clean_title(raw, fallback=""):
    """SEO-ueberladene Titel saeubern: '(auch Homeschooling)' weg, doppelte Komma-Segmente
    und wiederholte Woerter entfernen. 'Ägypten, Hieroglyphen Ägypten, (auch Homeschooling) Ägypten'
    -> 'Ägypten, Hieroglyphen'."""
    t = (raw or fallback or "").strip()
    t = re.sub(r"\(?\s*auch\s+homeschooling\s*\)?", "", t, flags=re.I)
    segs, seen = [], set()
    for s in t.split(","):
        s = s.strip()
        if s and s.lower() not in seen:
            seen.add(s.lower()); segs.append(s)
    t = ", ".join(segs) if segs else t
    words, seenw, out = t.split(), set(), []
    for w in words:
        lw = re.sub(r"[^a-zäöüß0-9]", "", w.lower())
        if lw and lw in seenw:
            continue
        seenw.add(lw); out.append(w)
    t = " ".join(out).strip(" ,;-")
    return (t[:78].rstrip(" ,;-") if len(t) > 78 else t) or fallback


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
        if not raw:
            continue
        m = re.match(r"#\s+(.+)", raw)
        if m:
            title, body_md = m.group(1).strip(), raw[m.end():].strip()
        else:
            title, body_md = base.split("_", 1)[-1].replace("-", " ").title(), raw
        meta = {}
        mp = os.path.join(META, pid + ".json")
        if os.path.exists(mp):
            try:
                meta = json.load(open(mp, encoding="utf-8"))
            except Exception:
                pass
        thema = (meta.get("thema") or "").strip()
        disp = clean_title(meta.get("titel") or title, thema or title)
        posts.append({
            "pid": pid, "title": disp, "raw_title": meta.get("titel") or title, "body_md": body_md,
            "desc": first_para(body_md)[:157],
            "slug": slugify(meta.get("permalink") or base.split("_", 1)[-1] or title),
            "cover": meta.get("cover", ""), "eduki": meta.get("url", ""), "fach": meta.get("fach", ""),
            "klasse": meta.get("klasse", ""), "thema": thema, "labels": meta.get("labels", ""),
            "date": datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat(),
        })
    seen = {}
    for p in posts:
        s = p["slug"]
        if s in seen:
            seen[s] += 1; p["slug"] = f"{s}-{p['pid']}"
        else:
            seen[s] = 1
    tok = {p["pid"]: tokens(p) for p in posts}
    for p in posts:
        me = tok[p["pid"]]
        scored = []
        for q in posts:
            if q["pid"] == p["pid"]:
                continue
            s = len(me & tok[q["pid"]]) + (2 if p["fach"] and p["fach"] == q["fach"] else 0)
            if s:
                scored.append((s, q))
        scored.sort(key=lambda x: (-x[0], x[1]["title"]))
        p["related"] = [q for _, q in scored[:4]]
    return posts


def topnav(root=""):
    return (f'<header class="topnav" id="topnav">'
            f'<a class="brand" href="{root}index.html" aria-label="{SITE_NAME} – Startseite">'
            f'<img src="{root}assets/logo-h.png" alt="{SITE_NAME}" width="303" height="97"></a>'
            f'<nav class="links">'
            f'<a href="{root}index.html">Materialien</a>'
            f'<a href="{SHOP}" rel="noopener">eduki-Shop</a>'
            f'<a href="{root}ueber-mich.html">Über mich</a>'
            f'<a href="{root}impressum.html">Impressum</a>'
            f'</nav></header>')


def head(title, desc, url, cover, root="", date=None, article=False):
    desc = html.escape(desc.replace("\n", " ").strip()); t = html.escape(title)
    og_img = cover or f"{SITE}/assets/logo.png"
    jsonld = {"@context": "https://schema.org", "@type": "BlogPosting" if article else "WebSite",
              ("headline" if article else "name"): title, "description": desc, "url": url,
              "author": {"@type": "Organization", "name": SITE_NAME},
              "publisher": {"@type": "Organization", "name": SITE_NAME}}
    if article:
        jsonld["datePublished"] = date; jsonld["dateModified"] = date
        if cover:
            jsonld["image"] = cover
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
<meta name="theme-color" content="#fbfbfd" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme:dark)">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{SITE}/feed.xml">
<link rel="icon" type="image/png" href="{root}assets/logo.png">
<link rel="apple-touch-icon" href="{root}assets/logo.png">
<link rel="stylesheet" href="{root}assets/style.css">
<script>document.documentElement.className+=' js';</script>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head><body>
{topnav(root)}
"""


NAV_SCRIPT = """<script>
(function(){var t=document.getElementById('topnav');if(!t)return;
var on=function(){t.classList.toggle('scrolled',window.scrollY>8)};on();
addEventListener('scroll',on,{passive:true});})();
</script>"""


def foot(root=""):
    return f"""<footer class="site">
<p class="big">{SITE_NAME}</p>
<p>{TAGLINE}. Alle Materialien im <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a>.</p>
<p><a href="{root}index.html">Materialien</a> · <a href="{root}ueber-mich.html">Über mich</a> · <a href="{root}impressum.html">Impressum</a></p>
</footer>
{NAV_SCRIPT}
</body></html>"""


def render_post(p):
    url = f"{SITE}/posts/{p['slug']}.html"
    body_html = md.markdown(p["body_md"], extensions=["extra", "sane_lists", "nl2br"])
    cover = (f'<img class="cover" src="{html.escape(p["cover"])}" alt="{html.escape(p["title"])}" loading="lazy">'
             if p["cover"] else "")
    meta_line = " · ".join(x for x in (p["fach"], p["klasse"]) if x)
    rel = ""
    if p["related"]:
        items = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["title"])}</a></li>' for q in p["related"])
        rel = f'<section class="related"><h2>Passende Materialien</h2><ul>{items}</ul></section>'
    out = head(p["title"], p["desc"], url, p["cover"], "../", p["date"], True)
    out += f"""<main class="article-wrap"><article><h1>{html.escape(p['title'])}</h1>
{f'<p class="meta">{html.escape(meta_line)}</p>' if meta_line else ''}{cover}
{body_html}
<p class="cta"><a class="btn" href="{html.escape(p['eduki'] or SHOP)}" rel="noopener">Material auf eduki ansehen →</a></p>
</article>{rel}</main>""" + foot("../")
    open(os.path.join(POSTS_DIR, p["slug"] + ".html"), "w", encoding="utf-8").write(out)
    return url


def card_html(m):
    t = html.escape(m["title"])
    meta = " · ".join(x for x in (m["fach"], m["klasse"]) if x)
    search = html.escape(" ".join((m["title"], m["fach"], m["klasse"], m["thema"], m["labels"])).lower(), quote=True)
    if m["cover"]:
        img = f'<div class="card-img"><img loading="lazy" src="{html.escape(m["cover"])}" alt="{t}"></div>'
    else:
        img = f'<div class="card-img"><div class="ph">{t}</div></div>'
    return (f'<a class="card reveal" href="posts/{m["slug"]}.html" '
            f'data-fach="{html.escape(m["fach"], quote=True)}" data-klasse="{html.escape(m["klasse"], quote=True)}" '
            f'data-s="{search}">{img}<div class="card-body"><h3>{t}</h3>'
            f'{f"<p class=card-meta>{html.escape(meta)}</p>" if meta else ""}</div></a>')


INDEX_JS = """<script>
(function(){
 var q=document.getElementById('q'),grid=document.getElementById('grid'),
 cnt=document.getElementById('cnt'),nores=document.getElementById('nores');
 if(!grid)return;
 var cards=[].slice.call(grid.querySelectorAll('.card'));
 var f={fach:'',klasse:''},term='';
 function apply(){
   var n=0;
   for(var i=0;i<cards.length;i++){var c=cards[i];
     var ok=(!f.fach||c.getAttribute('data-fach')===f.fach)
          &&(!f.klasse||c.getAttribute('data-klasse')===f.klasse)
          &&(!term||c.getAttribute('data-s').indexOf(term)>-1);
     c.style.display=ok?'':'none';if(ok)n++;}
   if(cnt)cnt.textContent=n+(n===1?' Material':' Materialien');
   if(nores)nores.style.display=n?'none':'block';
 }
 if(q)q.addEventListener('input',function(e){term=e.target.value.trim().toLowerCase();apply();});
 [].forEach.call(document.querySelectorAll('.chip'),function(ch){
   ch.addEventListener('click',function(){
     var ty=ch.getAttribute('data-type'),val=ch.getAttribute('data-val');
     f[ty]=val;
     [].forEach.call(document.querySelectorAll('.chip[data-type="'+ty+'"]'),function(x){
       x.classList.toggle('on',x===ch);});
     apply();
   });
 });
 // Scroll-Reveal (gestaffelt)
 if('IntersectionObserver' in window){
   var io=new IntersectionObserver(function(es){es.forEach(function(e){
     if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},
     {rootMargin:'0px 0px -6% 0px'});
   cards.forEach(function(c,i){c.style.transitionDelay=(Math.min(i,10)*35)+'ms';io.observe(c);});
 } else {cards.forEach(function(c){c.classList.add('in');});}
})();
</script>"""


def render_index(posts):
    materials = [p for p in posts if p["eduki"]]
    # mit Cover zuerst (visueller), dann nach Fach/Titel
    materials.sort(key=lambda x: (0 if x["cover"] else 1, x["fach"], x["title"]))
    fach_c = collections.Counter(m["fach"] for m in materials if m["fach"])
    klasse_c = collections.Counter(m["klasse"] for m in materials if m["klasse"])

    def chips(counter, typ):
        s = f'<button class="chip on" data-type="{typ}" data-val="">Alle</button>'
        for val, n in sorted(counter.items(), key=lambda x: -x[1]):
            s += (f'<button class="chip" data-type="{typ}" data-val="{html.escape(val, quote=True)}">'
                  f'{html.escape(val)}<span class="n">{n}</span></button>')
        return s

    out = head(f"{SITE_NAME} — {TAGLINE}", TAGLINE + ". Sachthemen-Arbeitsblätter, Lückentexte und Hörverständnis mit Lösungen für Klasse 4–10.", SITE + "/", "")
    out += f"""<section class="hero">
<h1>Materialien, die den<br>Unterricht leichter machen.</h1>
<p class="sub">Fertige Arbeitsblätter, Lückentexte und Hörverständnis-Übungen – mit Lösungen. Such dein Thema, filtere nach Fach und Klasse.</p>
<div class="searchwrap">
<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
<input id="q" type="search" placeholder="Suchen: z. B. Ägypten, Vulkan, Bruchrechnen …" autocomplete="off" aria-label="Materialien durchsuchen">
</div>
<p class="count"><span id="cnt">{len(materials)} Materialien</span> · direkt auf eduki erhältlich</p>
</section>

<div class="filters">
<div class="row"><span class="flabel">Fach</span>{chips(fach_c, 'fach')}</div>
<div class="row"><span class="flabel">Klasse</span>{chips(klasse_c, 'klasse')}</div>
</div>

<main>
<div class="grid" id="grid">
{chr(10).join(card_html(m) for m in materials)}
</div>
<p class="noresults" id="nores">Keine Materialien gefunden – versuch einen anderen Suchbegriff oder Filter.</p>
</main>
{INDEX_JS}
""" + foot()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)
    # Such-Index als JSON (fuer spaetere Nutzung / Tools)
    idx = [{"pid": m["pid"], "title": m["title"], "fach": m["fach"], "klasse": m["klasse"],
            "thema": m["thema"], "cover": m["cover"], "url": f"{SITE}/posts/{m['slug']}.html",
            "eduki": m["eduki"]} for m in materials]
    open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8").write(
        json.dumps(idx, ensure_ascii=False))
    return len(materials)


def render_page(slug, title, inner):
    out = head(title, title, f"{SITE}/{slug}.html", "") + '<main class="article-wrap">' + inner + "</main>" + foot()
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
    u = [f"<url><loc>{SITE}/</loc><priority>1.0</priority></url>",
         f"<url><loc>{SITE}/impressum.html</loc></url>",
         f"<url><loc>{SITE}/ueber-mich.html</loc></url>"]
    for p in posts:
        u.append(f"<url><loc>{SITE}/posts/{p['slug']}.html</loc><lastmod>{p['date']}</lastmod></url>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(u) + "\n</urlset>")
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    posts = load_posts()
    for p in posts:
        render_post(p)
    nmat = render_index(posts)
    render_page("impressum", "Impressum", f"""<h1>Impressum</h1>
<p>Angaben gemäß § 5 DDG:</p>
<p>{INHABER}<br>{ANSCHRIFT}</p>
<p><strong>Kontakt:</strong><br>E-Mail: {EMAIL}</p>
<p><strong>Verantwortlich für den Inhalt</strong> nach § 18 Abs. 2 MStV: {INHABER} (Anschrift wie oben).</p>
<p>Dieser Blog verweist auf eigene Unterrichtsmaterialien im <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a>.</p>""")
    render_page("ueber-mich", "Über mich", f"""<h1>Über mich</h1>
<p>Hinter <strong>{SITE_NAME}</strong> steht {INHABER} – ich erstelle praxiserprobte Unterrichtsmaterialien
für Lehrkräfte: Arbeitsblätter, Lückentexte und Hörverständnis-Übungen inklusive Musterlösungen.</p>
<p>Auf dieser Seite findest du alle Materialien schnell über Suche und Filter. Passende fertige Materialien
gibt es direkt in meinem <a href="{SHOP}" rel="noopener">Shop auf eduki</a>.</p>""")
    write_feed(posts); write_meta(posts)
    print(f"OK: {len(posts)} Seiten, {nmat} Materialien im Finder (mit eduki-Link), "
          f"{sum(1 for p in posts if p['cover'])} mit Cover. Startseite neu (Suche+Filter+Reveal).")


if __name__ == "__main__":
    main()
