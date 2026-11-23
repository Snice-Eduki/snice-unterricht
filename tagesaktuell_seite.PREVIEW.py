# -*- coding: utf-8 -*-
"""23.11.2026 v4 (ersetzt v3): Seite tagesaktuell.html + Startseitenblock. Aufruf aus build.py: render(globals()), home_block(), NAV_LABEL.
Datenquelle: _tagesaktuell.json. Fassungen: themen[].stufen {kl5-6|kl7-10: {farbig|sw: {pdf, loesung}}}; Eintraege ohne stufen werden einfach gelistet.
Auswahl Klasse/Fassung wird aktiv, sobald alle Themen des neuesten Tages stufen haben."""
import html, json, os, datetime

H = os.path.dirname(os.path.abspath(__file__))
WT = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
NAV_LABEL = "Gratis-News-Blätter"
STUFEN = (("kl5-6", "Klasse 5–6"), ("kl7-10", "Klasse 7–10"))
e = html.escape
CSS = """<style>
.ta .lead{font-size:1.08rem}.ta h2{margin-top:2rem}.ta .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin:1rem 0}
.ta .tk{border:1px solid var(--line,#d0d0d8);border-radius:14px;overflow:hidden;background:var(--surface,transparent);display:flex;flex-direction:column;scroll-margin-top:90px}
.ta .tk img{width:100%;height:auto;aspect-ratio:1/1.41;object-fit:cover;background:#e8f0fa;display:block}
.ta .tk .b{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}.ta .tk h3{margin:0;font-size:1.05rem;line-height:1.3}
.ta .tk .fach{font-size:.82rem;color:var(--muted,#666)}.ta .tk p{margin:0;font-size:.92rem}
.ta .tk .st{display:flex;flex-direction:column;gap:6px;margin-top:auto}
.ta .tk .st a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:10px;border:1px solid var(--line,#999);text-decoration:none;font-weight:600;font-size:.92rem}
.ta .tk .st a.pri{background:#1f5fa8;color:#fff;border-color:#1f5fa8}
.ta .tk .st .row{display:flex;flex-wrap:wrap;gap:8px}.ta .tk .st .lab{font-size:.8rem;color:var(--muted,#666)}
.ta .tk .nach{font-size:.8rem;color:var(--muted,#666)}
.ta .hinweis{border-left:4px solid #e0b100;background:rgba(224,177,0,.12);padding:.7rem 1rem;border-radius:8px;margin:1rem 0}
.ta .sprung{display:flex;flex-wrap:wrap;gap:8px;margin:1rem 0}.ta .sprung a{padding:8px 14px;border-radius:999px;border:1px solid var(--line,#999);text-decoration:none;font-weight:600}
.ta .wahl{display:flex;flex-wrap:wrap;gap:14px 28px;padding:12px 16px;border:1px solid var(--line,#d0d0d8);border-radius:14px;margin:1rem 0}
.ta .wahl fieldset{border:0;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.ta .wahl legend{font-weight:700;padding:0;margin-bottom:6px}
.ta .wahl button{min-height:44px;padding:0 16px;border-radius:999px;border:1px solid var(--line,#999);background:transparent;color:inherit;font-weight:600;font-size:.95rem;cursor:pointer}
.ta .wahl button[aria-pressed=true]{background:#1f5fa8;color:#fff;border-color:#1f5fa8}
.ta[data-k="kl5-6"] [data-k="kl7-10"],.ta[data-k="kl7-10"] [data-k="kl5-6"],.ta[data-f="farbig"] [data-f="sw"],.ta[data-f="sw"] [data-f="farbig"]{display:none!important}
.ta details{margin:.6rem 0}.ta summary{cursor:pointer;font-weight:600;padding:.5rem 0;min-height:44px;display:flex;align-items:center}
.ta li{margin:.35rem 0}
@media(max-width:640px){.ta .cards{grid-template-columns:1fr}}</style>"""
HCSS = """<style>
.tablock{max-width:1180px;margin:16px auto 0;padding:24px 26px;border-radius:var(--radius);background:var(--surface);border:1px solid var(--line);border-top:5px solid var(--accent);box-shadow:var(--shadow);box-sizing:border-box}
@media(max-width:1224px){.tablock{margin:12px 14px 0;padding:18px 16px}}
.tablock .eb{margin:0 0 6px;font-size:14px;font-weight:600;color:var(--accent);letter-spacing:.04em;text-transform:uppercase}
.tablock h2{margin:0 0 4px;font-size:clamp(24px,3.2vw,34px);line-height:1.1;letter-spacing:-.03em;font-weight:700;color:var(--text)}
.tablock .dt{margin:0 0 14px;color:var(--muted);font-size:16px}
.tablock .wb{display:flex;flex-wrap:wrap;gap:8px 18px;margin:0 0 16px}.tablock .wb div{display:flex;flex-wrap:wrap;gap:8px}
.tablock .wb button{min-height:44px;padding:0 18px;border-radius:999px;border:1px solid var(--line);background:var(--chip);color:var(--text);font:inherit;font-size:15px;font-weight:600;cursor:pointer}
.tablock .wb button[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
.tablock .kach{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0 0 18px}
@media(max-width:760px){.tablock .kach{grid-template-columns:repeat(2,1fr);gap:10px}}
.tablock .k{background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.tablock .k img{width:100%;height:120px;object-fit:cover;object-position:top;display:block;background:var(--chip)}
.tablock .k .kb{padding:10px 12px 12px;display:flex;flex-direction:column;gap:8px;flex:1}
.tablock .k .t{font-weight:650;font-size:15px;line-height:1.25;color:var(--text)}
.tablock .k .d{margin-top:auto;display:flex;align-items:center;justify-content:center;min-height:44px;border-radius:12px;background:var(--accent);color:#fff;font-weight:600;font-size:15px}
.tablock .k .d:hover{background:var(--accent2)}
.tablock[data-k="kl5-6"] [data-k="kl7-10"],.tablock[data-k="kl7-10"] [data-k="kl5-6"],.tablock[data-f="farbig"] [data-f="sw"],.tablock[data-f="sw"] [data-f="farbig"]{display:none!important}
.tablock .alle{display:inline-flex;align-items:center;min-height:48px;padding:0 24px;border-radius:999px;background:var(--chip);color:var(--text);font-weight:600;border:1px solid var(--line)}
.tablock .alle:hover{background:var(--line)}
.schnell{max-width:1180px;margin:18px auto 0;padding:0 22px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;box-sizing:border-box}
@media(max-width:760px){.schnell{grid-template-columns:repeat(2,1fr);gap:10px;padding:0 14px}}
.schnell a{display:flex;flex-direction:column;justify-content:center;gap:2px;min-height:84px;padding:14px 18px;border-radius:16px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s}
.schnell a:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
.schnell b{font-size:18px;letter-spacing:-.01em;font-weight:650}.schnell span{color:var(--muted);font-size:14px}
.schnell a.g{background:var(--accent);border-color:var(--accent);color:#fff}.schnell a.g span{color:rgba(255,255,255,.85)}
.topnav .links a.hl{background:var(--accent);color:#fff!important;border-radius:999px;padding:0 12px;font-weight:650;display:inline-flex;align-items:center}
footer.site a.hl{font-weight:700;color:var(--accent)}
</style>"""


def _datum(d):
    x = datetime.date.fromisoformat(d); return f"{WT[x.weekday()]}, {x.day}. {MON[x.month - 1]} {x.year}"


def _tage():
    p = os.path.join(H, "_tagesaktuell.json")
    if not os.path.exists(p): return []
    return sorted(json.load(open(p, encoding="utf-8"))["tage"], key=lambda t: t["datum"], reverse=True)


def _hat_stufen(t): return bool(t["themen"]) and all("stufen" in th for th in t["themen"])


def _cid(t, th): return f'b{t["datum"]}-{th["id"]}'


def home_block(root=""):
    tage = _tage()
    if not tage: return ""
    t = tage[0]; ks = ""
    for th in t["themen"][:4]:
        if "stufen" in th:
            ln = "".join(f'<a class="d" data-k="{k}" data-f="{f}" href="{root}{e(th["stufen"][k][f]["pdf"])}" download>Arbeitsblatt (PDF)</a>' for k, _ in STUFEN for f in ("farbig", "sw"))
        else:
            ln = f'<a class="d" href="{root}{e(th["pdf"])}" download>Arbeitsblatt (PDF)</a>'
        ks += (f'<div class="k"><a href="{root}tagesaktuell.html#{_cid(t, th)}" tabindex="-1" aria-hidden="true"><img src="{root}{e(th["thumb"])}" alt="" loading="eager" width="212" height="110"></a>'
               f'<div class="kb"><a class="t" href="{root}tagesaktuell.html#{_cid(t, th)}">{e(th["titel"])}</a>{ln}</div></div>')
    wb = ""
    if _hat_stufen(t):
        wb = ('<div class="wb"><div role="group" aria-label="Klassenstufe"><button type="button" data-set="k" data-v="kl5-6" aria-pressed="true">Klasse 5–6</button><button type="button" data-set="k" data-v="kl7-10" aria-pressed="false">Klasse 7–10</button></div>'
              '<div role="group" aria-label="Fassung"><button type="button" data-set="f" data-v="farbig" aria-pressed="true">Farbig</button><button type="button" data-set="f" data-v="sw" aria-pressed="false">Schwarz-weiß</button></div></div>'
              '<script>(function(){var s=document.getElementById("tablock"),bs=s.querySelectorAll(".wb button");'
              'function set(a,v){s.setAttribute("data-"+a,v);[].forEach.call(bs,function(b){if(b.dataset.set===a)b.setAttribute("aria-pressed",b.dataset.v===v?"true":"false")});try{localStorage.setItem("ta_"+a,v)}catch(x){}}'
              '[].forEach.call(bs,function(b){b.addEventListener("click",function(){set(b.dataset.set,b.dataset.v)})});'
              'try{["k","f"].forEach(function(a){var v=localStorage.getItem("ta_"+a);if(v&&v!=="alle")set(a,v)})}catch(x){}})();</script>')
    return (HCSS + f'<section class="tablock" id="tablock" data-k="kl5-6" data-f="farbig" aria-label="Gratis: Arbeitsblätter zu den Nachrichten von heute"><p class="eb">Gratis · jeden Tag neu</p><h2>Gratis: Arbeitsblätter zu den Nachrichten von heute</h2>'
            f'<p class="dt">{_datum(t["datum"])}</p>{wb}<div class="kach">{ks}</div><a class="alle" href="{root}tagesaktuell.html">Alle Nachrichten-Blätter</a></section>')


def schnell(root=""):
    t = [("g", "Gratis-News-Blätter", "Heute aktuell", "tagesaktuell.html"), ("", "Kostenloses Material", "Nach Fach und Klasse", "kostenlos.html"),
         ("", "Alle Materialien", "Suchen und filtern", "materialien.html"), ("", "Neu erschienen", "Die neuesten Blätter", "neu.html"),
         ("", "Lehrplan-Themen", "Von Bruchrechnung bis Wald", "lehrplan-themen.html"), ("", "Andere Sprachen", "English, Español, Français, Italiano", "material-in-anderen-sprachen.html")]
    return '<nav class="schnell" aria-label="Schnellzugang">' + "".join(f'<a class="{c}" href="{root}{h}"><b>{a}</b><span>{b}</span></a>' for c, a, b, h in t) + "</nav>"


def _stufen_html(th):
    if "stufen" not in th:
        return (f'<div class="st"><div class="row"><a class="pri" href="{e(th["pdf"])}" download>Arbeitsblatt (PDF)</a>'
                f'<a href="{e(th["loesung"])}" download>Lösung für Lehrkräfte</a></div></div>')
    z = '<div class="st">'
    for sk, sn in STUFEN:
        s_ = th["stufen"][sk]
        z += f'<div data-k="{sk}"><span class="lab">Arbeitsblatt {sn}</span><div class="row">'
        for fk, fn in (("farbig", "farbig"), ("sw", "schwarz/weiß")):
            z += f'<a data-f="{fk}" class="pri" href="{e(s_[fk]["pdf"])}" download>{fn}</a>'
        z += '</div><span class="lab">Lösung für Lehrkräfte</span><div class="row">'
        for fk, fn in (("farbig", "farbig"), ("sw", "schwarz/weiß")):
            z += f'<a data-f="{fk}" href="{e(s_[fk]["loesung"])}" download>{fn}</a>'
        z += '</div></div>'
    return z + '</div>'


def _alt(th):
    if "stufen" not in th: return f'<a href="{e(th["pdf"])}" download>Arbeitsblatt</a> · <a href="{e(th["loesung"])}" download>Lösung</a>'
    return " · ".join(f'{n}: <a href="{e(th["stufen"][k]["farbig"]["pdf"])}" download>farbig</a>, <a href="{e(th["stufen"][k]["sw"]["pdf"])}" download>s/w</a> '
                      f'(Lösung <a href="{e(th["stufen"][k]["farbig"]["loesung"])}" download>farbig</a>, <a href="{e(th["stufen"][k]["sw"]["loesung"])}" download>s/w</a>)' for k, n in STUFEN)


def render(g):
    tage = _tage()
    if not tage: print("Tagesaktuell: keine Daten", flush=True); return 0
    SITE = g["SITE"]; url = SITE + "/tagesaktuell.html"
    heute = tage[0]; v3 = _hat_stufen(heute)
    desc = ("Kostenlose News-Arbeitsblätter für die Schule: täglich neue Arbeitsblätter zu aktuellen Nachrichten für Klasse 5–6 und 7–10, "
            "farbig und schwarz/weiß kopierfreundlich, mit Lösungsblatt für Lehrkräfte.")
    g["PAGE_DESC"]["tagesaktuell"] = desc
    karten = ""
    for th in heute["themen"]:
        karten += (f'<article class="tk" id="{_cid(heute, th)}"><img src="{e(th["thumb"])}" alt="Deckblatt: {e(th["titel"])}" loading="lazy" width="424" height="600">'
                   f'<div class="b"><span class="fach">{e(th["fach"])}</span><h3>{e(th["titel"])}</h3><p>{e(th["teaser"])}</p>'
                   + _stufen_html(th) + f'<span class="nach">Foto: {e(th["foto"])}</span></div></article>')
    wahl = ""
    if v3:
        wahl = ('<div class="wahl" id="wahl"><fieldset><legend>Klassenstufe</legend><button type="button" data-set="k" data-v="alle" aria-pressed="true">Beide</button>'
                '<button type="button" data-set="k" data-v="kl5-6" aria-pressed="false">Klasse 5–6</button><button type="button" data-set="k" data-v="kl7-10" aria-pressed="false">Klasse 7–10</button></fieldset>'
                '<fieldset><legend>Fassung</legend><button type="button" data-set="f" data-v="alle" aria-pressed="true">Beide</button>'
                '<button type="button" data-set="f" data-v="farbig" aria-pressed="false">farbig</button><button type="button" data-set="f" data-v="sw" aria-pressed="false">schwarz/weiß</button></fieldset></div>'
                '<script>(function(){var ta=document.querySelector(".ta"),bs=document.querySelectorAll("#wahl button");'
                'function set(a,v){ta.setAttribute("data-"+a,v);[].forEach.call(bs,function(b){if(b.dataset.set===a)b.setAttribute("aria-pressed",b.dataset.v===v?"true":"false")});try{localStorage.setItem("ta_"+a,v)}catch(x){}}'
                '[].forEach.call(bs,function(b){b.addEventListener("click",function(){set(b.dataset.set,b.dataset.v)})});'
                'try{["k","f"].forEach(function(a){var v=localStorage.getItem("ta_"+a);if(v)set(a,v)})}catch(x){}})();</script>')
    alt = "".join(f'<details><summary>{_datum(t["datum"])}</summary><ul>' + "".join(f'<li>{e(th["titel"])}: {_alt(th)}</li>' for th in t["themen"]) + "</ul></details>" for t in tage[1:])
    archiv = f'<h2 id="archiv">Archiv: die letzten Tage</h2>{alt}' if alt else ""
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "News-Arbeitsblätter – kostenlos und tagesaktuell", "url": url, "inLanguage": "de",
          "isAccessibleForFree": True, "description": desc,
          "hasPart": [{"@type": "LearningResource", "name": th["titel"], "description": th["teaser"], "learningResourceType": "Arbeitsblatt",
                       "educationalLevel": "Klasse 5–6 und 7–10", "inLanguage": "de", "isAccessibleForFree": True,
                       "datePublished": heute["datum"], "teaches": th["fach"],
                       "url": f'{url}#{_cid(heute, th)}',
                       "encoding": {"@type": "MediaObject", "encodingFormat": "application/pdf",
                                    "contentUrl": f'{SITE}/' + (th["stufen"]["kl7-10"]["farbig"]["pdf"] if "stufen" in th else th["pdf"])}}
                      for th in heute["themen"]]}
    inner = f"""{CSS}<div class="ta" data-k="alle" data-f="alle"><h1>Kostenlose News-Arbeitsblätter – tagesaktuell</h1>
<p class="lead">Jeden Tag neu: <strong>kostenlose Arbeitsblätter zu aktuellen Nachrichten</strong> für Klasse 5–6 und 7–10, zu den Themen des täglichen Nachrichten-Reels „Dein Morgen-Update“. Mit Lesetext, Aufgaben, Kartenaufgabe und Lösungsblatt für Lehrkräfte.</p>
<nav class="sprung" aria-label="Auf dieser Seite"><a href="#heute">Heute</a><a href="#archiv">Archiv</a><a href="#hinweise">Hinweise</a><a href="newsletter.html">Newsletter</a></nav>
<h2 id="heute">Heute: {_datum(heute["datum"])}</h2>{wahl}
<div class="cards">{karten}</div>
{archiv}
<h2 id="hinweise">Hinweise</h2>
<ul><li><strong>Kostenlos und kopierfreundlich:</strong> alle Blätter als PDF, auf Wunsch in der Schwarz-Weiß-Fassung mit wenig Tinte.</li>
<li><strong>Sofort einsetzbar:</strong> Morgenkreis, Vertretungsstunde oder Hausaufgabe.</li>
<li><strong>Behutsam bei ernsten Themen:</strong> keine Gewaltdetails, Hinweise zum Umgang mit belastenden Nachrichten.</li></ul>
<p class="hinweis"><strong>Quelle und Lizenz:</strong> Die Fotos sind frei lizenzierte Bilder von Wikimedia Commons (Nachweis am Blatt) und zeigen den Ort oder das Thema, nicht das Ereignis. Die Texte beruhen auf mindestens zwei unabhängigen Meldungen; die Quellen stehen im Lösungsblatt.</p>
<p>Mehr kostenloses Material: <a href="kostenlos.html">Kostenloses Unterrichtsmaterial</a> · <a href="newsletter.html">Newsletter</a></p></div>"""
    title = "Kostenlose News-Arbeitsblätter tagesaktuell (Klasse 5–6 und 7–10)"
    cover = f'{SITE}/{heute["themen"][0]["thumb"]}'
    out = (g["head"](title, desc, url, cover, extra_ld=[ld]) + '<main class="article-wrap">' + inner + "</main>" + g["foot"]())
    open(os.path.join(g["OUT"], "tagesaktuell.html"), "w", encoding="utf-8").write(out)
    if url not in g["EXTRA_URLS"]: g["EXTRA_URLS"].append(url)
    print("Tagesaktuell:", len(tage), "Tage, Auswahl", "aktiv" if v3 else "aus", flush=True)
    return len(tage)
