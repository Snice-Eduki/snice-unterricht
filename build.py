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
            f'<a href="{root}lesespurgeschichten.html">Lesespurgeschichten</a>'
            f'<a href="{root}herbst.html">Herbst</a>'
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
<p><a href="{root}index.html">Materialien</a> · <a href="{root}ueber-mich.html">Über mich</a> · <a href="{root}impressum.html">Impressum</a> · <a href="{root}datenschutz.html">Datenschutz</a></p>
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


EDUKI_MAT = "https://eduki.com/de/material"


def grade_nums(grades):
    ns = []
    for g in grades or []:
        m = re.match(r"(\d+)", str(g))
        if m:
            ns.append(int(m.group(1)))
    return sorted(set(ns))


def klasse_label(grades):
    ns = grade_nums(grades)
    if not ns:
        return ""
    return f"Kl. {ns[0]}" if len(ns) == 1 else f"Kl. {ns[0]}–{ns[-1]}"


def cat_card_html(m):
    """Karte fuer ein Katalog-Material – Direktlink zu eduki."""
    t = html.escape(m["title"])
    fach = m.get("fach", "")
    schul = (m.get("school_types") or [""])[0]
    kl = klasse_label(m.get("grades"))
    meta = " · ".join(x for x in (fach, kl) if x)
    nums = grade_nums(m.get("grades"))
    kdata = "," + ",".join(str(n) for n in nums) + "," if nums else ""
    search = html.escape(" ".join([m["title"], fach, schul, kl, m.get("desc", "")]).lower(), quote=True)
    url = f'{EDUKI_MAT}/{m["id"]}/{html.escape(m.get("slug",""), quote=True)}'
    if m.get("cover"):
        img = f'<div class="card-img"><img loading="lazy" src="{html.escape(m["cover"])}" alt="{t}"></div>'
    else:
        img = f'<div class="card-img"><div class="ph">{t}</div></div>'
    badge = '<span class="badge">Gratis</span>' if m.get("is_free") else ''
    return (f'<a class="card reveal" href="{url}" target="_blank" rel="noopener" '
            f'data-fach="{html.escape(fach, quote=True)}" data-kl="{kdata}" data-s="{search}">'
            f'{img}{badge}<div class="card-body"><h3>{t}</h3>'
            f'{f"<p class=card-meta>{html.escape(meta)}</p>" if meta else ""}</div></a>')


INDEX_JS = """<script>
(function(){
 var q=document.getElementById('q'),grid=document.getElementById('grid'),
 cnt=document.getElementById('cnt'),nores=document.getElementById('nores');
 if(!grid)return;
 var cards=[].slice.call(grid.querySelectorAll('.card'));
 var f={fach:'',kl:''},term='';
 function apply(){
   var n=0;
   for(var i=0;i<cards.length;i++){var c=cards[i];
     var ok=(!f.fach||c.getAttribute('data-fach')===f.fach)
          &&(!f.kl||c.getAttribute('data-kl').indexOf(','+f.kl+',')>-1)
          &&(!term||c.getAttribute('data-s').indexOf(term)>-1);
     c.style.display=ok?'':'none';if(ok)n++;}
   if(cnt)cnt.textContent=n+(n===1?' Material':' Materialien');
   if(nores)nores.style.display=n?'none':'block';
 }
 var _t;
 if(q)q.addEventListener('input',function(e){var v=e.target.value.trim().toLowerCase();
   clearTimeout(_t);_t=setTimeout(function(){term=v;apply();},180);});
 [].forEach.call(document.querySelectorAll('.chip'),function(ch){
   ch.addEventListener('click',function(){
     var ty=ch.getAttribute('data-type'),val=ch.getAttribute('data-val');
     f[ty]=val;  // ty = 'fach' | 'kl'
     [].forEach.call(document.querySelectorAll('.chip[data-type="'+ty+'"]'),function(x){
       x.classList.toggle('on',x===ch);});
     apply();
   });
 });
 // Scroll-Reveal nur bei ueberschaubarer Menge (Performance bei tausenden Karten)
 if(cards.length<=400 && 'IntersectionObserver' in window){
   var io=new IntersectionObserver(function(es){es.forEach(function(e){
     if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},
     {rootMargin:'0px 0px -6% 0px'});
   cards.forEach(function(c,i){c.style.transitionDelay=(Math.min(i,10)*35)+'ms';io.observe(c);});
 } else {cards.forEach(function(c){c.classList.add('in');});}
})();
</script>"""


def load_katalog():
    kp = os.path.join(OUT, "_katalog_live.json")
    if not os.path.exists(kp):
        return []
    kat = json.load(open(kp, encoding="utf-8"))
    return [m for m in kat if m.get("active") and m.get("slug")]


def render_index(posts):
    materials = load_katalog()
    # mit Cover zuerst, dann Fach, dann Titel
    materials.sort(key=lambda x: (0 if x.get("cover") else 1, x.get("fach", ""), x.get("title", "")))
    fach_c = collections.Counter(m["fach"] for m in materials if m.get("fach"))
    # Klasse-Chips = einzelne Jahrgangsstufen (Material kann mehrere haben)
    kl_c = collections.Counter()
    for m in materials:
        for n in grade_nums(m.get("grades")):
            kl_c[n] += 1

    def fach_chips(counter):
        s = '<button class="chip on" data-type="fach" data-val="">Alle</button>'
        for val, n in sorted(counter.items(), key=lambda x: -x[1]):
            s += (f'<button class="chip" data-type="fach" data-val="{html.escape(val, quote=True)}">'
                  f'{html.escape(val)}<span class="n">{n}</span></button>')
        return s

    def kl_chips(counter):
        s = '<button class="chip on" data-type="kl" data-val="">Alle</button>'
        for n in sorted(counter):
            s += (f'<button class="chip" data-type="kl" data-val="{n}">'
                  f'{n}. Kl.<span class="n">{counter[n]}</span></button>')
        return s

    nfmt = f"{len(materials):,}".replace(",", ".")
    out = head(f"{SITE_NAME} — {TAGLINE}",
               f"{TAGLINE}. Über {nfmt} Arbeitsblätter, Lückentexte und Hörverständnis-Übungen mit Lösungen für alle Fächer und Klassen.",
               SITE + "/", "")
    out += f"""<section class="hero">
<h1>Materialien, die den<br>Unterricht leichter machen.</h1>
<p class="sub">Über {nfmt} fertige Arbeitsblätter, Lückentexte und Hörverständnis-Übungen – mit Lösungen. Such dein Thema, filtere nach Fach und Klasse.</p>
<div class="searchwrap">
<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
<input id="q" type="search" placeholder="Suchen: z. B. Ägypten, Vulkan, Photosynthese …" autocomplete="off" aria-label="Materialien durchsuchen">
</div>
<p class="count"><span id="cnt">{nfmt} Materialien</span> · Klick führt direkt zu eduki</p>
</section>

<div class="filters">
<div class="row"><span class="flabel">Fach</span>{fach_chips(fach_c)}</div>
<div class="row"><span class="flabel">Klasse</span>{kl_chips(kl_c)}</div>
</div>

<main>
<div class="grid" id="grid">
{chr(10).join(cat_card_html(m) for m in materials)}
</div>
<p class="noresults" id="nores">Keine Materialien gefunden – versuch einen anderen Suchbegriff oder Filter.</p>
</main>
{INDEX_JS}
""" + foot()
    out = out.replace(",", ".") if False else out  # (Tausendertrennung bleibt wie f-string)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)
    idx = [{"id": m["id"], "title": m["title"], "fach": m.get("fach", ""),
            "grades": m.get("grades", []), "cover": m.get("cover", ""),
            "eduki": f'{EDUKI_MAT}/{m["id"]}/{m.get("slug","")}'} for m in materials]
    open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8").write(
        json.dumps(idx, ensure_ascii=False))
    return len(materials)


def render_page(slug, title, inner):
    out = head(title, title, f"{SITE}/{slug}.html", "") + '<main class="article-wrap">' + inner + "</main>" + foot()
    open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8").write(out)


EXTRA_URLS = []
LS_INTRO = ("Eine Lesespurgeschichte ist ein differenziertes Lese- und Sachmaterial: Die Klasse liest eine Geschichte "
            "in drei Niveaustufen (leicht, mittel, schwer), folgt den Hinweisen über einen Lageplan von Station zu "
            "Station und sammelt dabei Buchstaben für ein Lösungswort. Jedes Paket enthält Anleitung, drei "
            "Geschichten, Lageplan, Hörverstehen mit QR-Code, Rätselseite, Ausmalbild und Lösungen – in Farbe und als "
            "kopierfreundliche Schwarz-Weiß-Version. Die Themen orientieren sich an den Lehrplänen aller Bundesländer "
            "und passen für alle Schularten (Grundschule, Mittel-, Haupt-, Real-, Ober-, Gesamt- und "
            "Gemeinschaftsschule, Gymnasium).")


def is_lesespur(m):
    return "lesespur" in (m.get("title", "") + " " + m.get("desc", "")).lower()


def _ls_page(slug, title, h1, desc, intro, mats, links_html=""):
    """Landingpage mit Karten-Grid (gleiche Karten wie der Finder, ohne JS-Filter)."""
    mats = sorted(mats, key=lambda x: (0 if x.get("cover") else 1, x.get("title", "")))
    url = f"{SITE}/{slug}.html"
    n = len(mats)
    out = head(title, desc, url, mats[0].get("cover", "") if mats else "")
    out += f"""<section class="hero small">
<h1>{html.escape(h1)}</h1>
<p class="sub">{html.escape(intro)}</p>
<p class="count">{n} {'Lesespurgeschichte' if n == 1 else 'Lesespurgeschichten'} · Klick führt direkt zu eduki</p>
</section>
{links_html}
<main><div class="grid" id="grid">
{chr(10).join(cat_card_html(m) for m in mats)}
</div></main>
<script>[].forEach.call(document.querySelectorAll('.card'),function(c){{c.classList.add('in');}});</script>
""" + foot()
    open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8").write(out)
    EXTRA_URLS.append(url)
    return url


SAISON = {
    "herbst": {
        "title": "Herbst-Materialien für den Unterricht",
        "h1": "Herbst im Unterricht",
        "desc": "Arbeitsblätter, Lesespurgeschichten und Hörverstehen rund um den Herbst: Kürbis, Kastanie, Igel, "
                "Zugvögel, Nebel, Ernte, Kartoffel und Wald – für Grundschule und Sekundarstufe, mit Lösungen.",
        "intro": "Der Herbst bringt die schönsten Sachthemen ins Klassenzimmer: Kastanien und Kürbisse, Igel und "
                 "Zugvögel, Nebelmorgen und Erntezeit. Hier findest du alle passenden Materialien auf einen Blick – "
                 "Lesespurgeschichten in drei Niveaustufen, Lückentexte mit Hörverstehen und Steckbriefe, jeweils mit "
                 "Lösungen und direktem Link zu eduki.",
        "kw": r"\bherbst|kürbis|kastanie|\bigel\b|\bigel[ -]|zugvögel|\bkranich|storch|\bpilz|ernte|\bnebel\b|laubbaum|laubblatt|herbstlaub|"
              r"\bapfel\b|apfelbaum|kartoffel|\bdrachen\b|eichhörnchen|\beichel|haselnuss|walnuss|wetterstation|jahreszeiten|"
              r"winterschlaf|erntedank|laterne|sankt martin|waldkauz|waldtiere|lebensraum wald|\bwald\b|tiere des waldes|\bwolf\b|"
              r"\bhirsch\b|\breh\b|wildschwein|\bfuchs\b|\bhase\b|\bmais\b|weizen|\bwein(lese|bau)|trauben|zwiebel|\brübe|federweiße",
        "block": r"kreis|stadt\b|-stadt|regierungsbezirk|buchführung|blaubär|kalifornien|kokosnuss|regenwald|worksheet|"
                 r"bayerischer wald|oberpfälzer|thüringer wald|teutoburger|rübezahl|dissen",
    },
}


def render_saison_pages():
    """Saisonale Landingpages (z. B. Herbst): Keyword-Auswahl aus dem Katalog, alle Fächer/Klassen."""
    mats = load_katalog()
    n_total = 0
    for slug, s in SAISON.items():
        sel = [m for m in mats
               if re.search(s["kw"], m["title"].lower()) and not re.search(s["block"], m["title"].lower())]
        if not sel:
            continue
        n_total += len(sel)
        links = ('<div class="filters"><div class="row">'
                 '<a class="chip" href="lesespurgeschichten.html">Alle Lesespurgeschichten</a>'
                 '<a class="chip" href="index.html">Alle Materialien</a></div></div>')
        _ls_page(slug, s["title"], s["h1"], s["desc"], s["intro"], sel, links)
    return n_total


def render_lesespur_pages():
    """Hub + Landingpages je Fach und je Klasse fuer Lesespurgeschichten (SEO-Suchintention
    'Lesespurgeschichte Klasse 8 Physik'). Alle Karten verlinken direkt zum eduki-Material."""
    mats = [m for m in load_katalog() if is_lesespur(m)]
    if not mats:
        return 0
    by_fach = collections.defaultdict(list)
    by_kl = collections.defaultdict(list)
    for m in mats:
        if m.get("fach"):
            by_fach[m["fach"]].append(m)
        for n in grade_nums(m.get("grades")):
            by_kl[n].append(m)
    fach_links = "".join(
        f'<a class="chip" href="lesespurgeschichten-{slugify(f)}.html">{html.escape(f)}<span class="n">{len(v)}</span></a>'
        for f, v in sorted(by_fach.items(), key=lambda x: -len(x[1])))
    kl_links = "".join(
        f'<a class="chip" href="lesespurgeschichten-klasse-{n}.html">{n}. Kl.<span class="n">{len(by_kl[n])}</span></a>'
        for n in sorted(by_kl))
    links = (f'<div class="filters"><div class="row"><span class="flabel">Fach</span>{fach_links}</div>'
             f'<div class="row"><span class="flabel">Klasse</span>{kl_links}</div></div>')
    hub_link = '<div class="filters"><div class="row"><a class="chip" href="lesespurgeschichten.html">← Alle Lesespurgeschichten</a></div></div>'
    _ls_page("lesespurgeschichten", "Lesespurgeschichten für alle Fächer und Klassen",
             "Lesespurgeschichten",
             f"{len(mats)} Lesespurgeschichten mit drei Niveaustufen, Lageplan, Hörverstehen (QR) und Lösungswort – "
             "für Grundschule bis Sekundarstufe, alle Fächer, alle Bundesländer.",
             LS_INTRO, mats, links)
    for f, v in by_fach.items():
        _ls_page(f"lesespurgeschichten-{slugify(f)}", f"Lesespurgeschichten {f}",
                 f"Lesespurgeschichten {f}",
                 f"{len(v)} Lesespurgeschichten für das Fach {f}: differenziert in drei Niveaustufen, mit Lageplan, "
                 "Hörverstehen und Lösungswort – lehrplanorientiert für alle Bundesländer und Schularten.",
                 f"Lesespurgeschichten für den {f}-Unterricht. " + LS_INTRO, v, hub_link)
    for n, v in by_kl.items():
        _ls_page(f"lesespurgeschichten-klasse-{n}", f"Lesespurgeschichten Klasse {n}",
                 f"Lesespurgeschichten Klasse {n}",
                 f"{len(v)} Lesespurgeschichten für die {n}. Klasse: drei Niveaustufen, Lageplan, Hörverstehen mit "
                 "QR-Code und Lösungswort – passend zu den Lehrplänen aller Bundesländer und Schularten.",
                 f"Lesespurgeschichten für die {n}. Jahrgangsstufe, sprachlich und inhaltlich auf das Alter abgestimmt. " + LS_INTRO,
                 v, hub_link)
    return len(mats)


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
         f"<url><loc>{SITE}/ueber-mich.html</loc></url>",
         f"<url><loc>{SITE}/datenschutz.html</loc></url>"]
    u += [f"<url><loc>{x}</loc><priority>0.8</priority></url>" for x in EXTRA_URLS]
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
    nls = render_lesespur_pages()
    nsa = render_saison_pages()
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
    render_page("datenschutz", "Datenschutzerklärung", f"""<h1>Datenschutzerklärung</h1>
<p><strong>Verantwortlicher:</strong> {INHABER}, E-Mail: {EMAIL} (Anschrift siehe <a href="impressum.html">Impressum</a>).</p>
<h2>Hosting</h2>
<p>Diese Website wird als statische Seite über <strong>GitHub Pages</strong> (GitHub, Inc., 88 Colin P. Kelly Jr. St, San Francisco, CA 94107, USA)
ausgeliefert. Beim Aufruf verarbeitet GitHub technisch notwendige Verbindungsdaten (IP-Adresse, Zeitpunkt, aufgerufene Seite, Browser)
in Server-Logs, um die Seite auszuliefern und die Sicherheit des Dienstes zu gewährleisten (Art. 6 Abs. 1 lit. f DSGVO).
Details: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">GitHub Privacy Statement</a>.
GitHub ist nach dem EU-US Data Privacy Framework zertifiziert.</p>
<h2>Keine Cookies, kein Tracking</h2>
<p>Diese Website setzt keine Cookies, verwendet keine Analyse- oder Werbedienste und bindet keine Schriftarten oder Skripte von Drittanbietern ein.
Die Suche und die Filter laufen vollständig in deinem Browser; dabei werden keine Daten übertragen.</p>
<h2>Externe Links und eingebundene Bilder</h2>
<p>Die Vorschaubilder der Materialien werden direkt vom Marktplatz <strong>eduki</strong> (eduki GmbH, Berlin) geladen; dabei erhält eduki deine IP-Adresse.
Über die Links „Material auf eduki" gelangst du auf eduki.com; dort gelten die
<a href="https://eduki.com/de/datenschutz" rel="noopener">Datenschutzhinweise von eduki</a>.</p>
<h2>Kontakt per E-Mail</h2>
<p>Wenn du mir eine E-Mail schreibst, verarbeite ich deine Angaben ausschließlich zur Bearbeitung deiner Anfrage (Art. 6 Abs. 1 lit. b bzw. f DSGVO)
und lösche sie, sobald sie nicht mehr benötigt werden.</p>
<h2>Deine Rechte</h2>
<p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO)
sowie das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde. Wende dich dazu an die oben genannte E-Mail-Adresse.</p>
<p><small>Stand: September 2026</small></p>""")
    render_page("404", "Seite nicht gefunden", f"""<h1>Seite nicht gefunden</h1>
<p>Diese Seite gibt es nicht (mehr). Vielleicht hilft dir die Suche auf der <a href="/index.html">Startseite</a> weiter –
dort findest du alle Materialien nach Fach und Klasse.</p>
<p><a class="btn" href="/index.html">Zur Startseite</a> · <a href="/lesespurgeschichten.html">Lesespurgeschichten</a> · <a href="{SHOP}" rel="noopener">Snice-Shop auf eduki</a></p>""")
    write_feed(posts); write_meta(posts)
    print(f"OK: {len(posts)} Seiten, {nmat} Materialien im Finder (mit eduki-Link), "
          f"{sum(1 for p in posts if p['cover'])} mit Cover, {nls} Lesespuren, {nsa} Saison-Treffer, {len(EXTRA_URLS)} Landingpages.")


if __name__ == "__main__":
    main()
