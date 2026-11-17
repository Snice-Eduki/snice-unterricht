# -*- coding: utf-8 -*-
"""17.11.2026: Wissens-Seiten (nur DE) = eigene Sachtexte zu Lehrplanthemen, die als Textquelle der
Hoerverstehen-/Lueckentext-Blaetter dienen (Ersatz fuer die fruehere Klexikon-Verlinkung).
Daten: _wissen_themen.json neben build.py, Liste aus
  {"thema", "slug", "fach", "klassen", "text", "bild" (optional, Datei in assets/wissen/),
   "eduki" (optional, Material-URL), "audio" (optional, Hoerseiten-URL)}
Ausgabe: wissen/<slug>.html + wissen/index.html. Aufruf aus build.py: render(globals()).
Einzelseite ohne Vollbau: python wissen_seiten.py <slug> [<slug> ...]  (oder --alle)"""
import html, json, os, re, sys, collections

H = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(H, "_wissen_themen.json")
E = html.escape
CSS = """<style>
.ws .chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0 1rem}.ws .chips span{border:1px solid #d0d0d8;border-radius:999px;padding:.15rem .7rem;font-size:.9rem}
.ws .txt{max-width:44rem;font-size:1.15rem;line-height:1.7}.ws .txt p{margin:0 0 1rem}
.ws figure{margin:1rem 0 1.4rem;max-width:44rem}.ws figure img{width:100%;height:auto;border-radius:14px}
.ws .box{max-width:44rem;border:1px solid #d0d0d8;border-radius:14px;padding:1rem 1.2rem;margin:1.6rem 0}
.ws .src{font-size:.9rem;opacity:.75;max-width:44rem}.ws .tl{columns:3;column-gap:2rem;padding-left:1.1rem}
.ws audio{width:100%;margin:.4rem 0}
@media(max-width:700px){.ws .tl{columns:1}}</style>"""


def laden():
    if not os.path.exists(DATA):
        return []
    d = json.load(open(DATA, encoding="utf-8"))
    return [x for x in d if x.get("thema") and x.get("slug") and len(x.get("text", "")) >= 600]


def absaetze(text, n=4):
    s = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]
    return [" ".join(s[i:i + n]) for i in range(0, len(s), n)]


def seite(g, t):
    head, foot, SITE, bc = g["head"], g["foot"], g["SITE"], g["breadcrumb_ld"]
    url = f"{SITE}/wissen/{t['slug']}.html"
    kl = t.get("klassen", ""); fach = t.get("fach", "")
    desc = (f"{t['thema']} einfach erklärt: kurzer Sachtext für Klasse {kl}" if kl else f"{t['thema']} einfach erklärt: kurzer Sachtext für die Schule")
    desc += f" ({fach})." if fach else "."
    desc += " Passend zum Arbeitsblatt mit Lückentext, Hörverstehen und Suchsel."
    cover = f"{SITE}/assets/wissen/{t['bild']}" if t.get("bild") else ""
    ld = [bc([("Start", SITE + "/"), ("Wissen", SITE + "/wissen/"), (t["thema"], url)])]
    out = head(f"{t['thema']} einfach erklärt – Sachtext für Kinder", desc, url, cover, root="../", extra_ld=ld)
    chips = "".join(f"<span>{E(x)}</span>" for x in ([fach] if fach else []) + ([f"Klasse {kl}"] if kl else []))
    bild = (f'<figure><img src="../assets/wissen/{E(t["bild"])}" alt="{E(t["thema"])}" loading="lazy"></figure>' if t.get("bild") else "")
    txt = "".join(f"<p>{E(a)}</p>" for a in absaetze(t["text"]))
    audio = (f'<div class="box"><strong>Hörtext</strong><p>Den Text zum Anhören gibt es hier: <a href="{E(t["audio"])}" rel="noopener">Hörtext öffnen</a></p></div>' if t.get("audio") else "")
    if t.get("eduki"):
        mat = (f'<div class="box"><strong>Arbeitsblatt zum Text</strong><p>Zu diesem Sachtext gibt es ein Arbeitsblatt mit Lückentext, Wortspeicher, '
               f'Hörverstehen und Suchsel, jeweils mit Lösung.</p><p><a class="btn" href="{E(t["eduki"])}" rel="noopener">Arbeitsblatt auf eduki ansehen</a></p></div>')
    else:
        mat = ('<div class="box"><strong>Arbeitsblatt zum Text</strong><p>Zu diesem Sachtext gibt es ein Arbeitsblatt mit Lückentext, Wortspeicher, '
               f'Hörverstehen und Suchsel, jeweils mit Lösung, im <a href="{E(g["SHOP"])}" rel="noopener">Snice-Shop auf eduki</a>.</p></div>')
    out += (f'<main class="article-wrap ws">{CSS}<nav class="crumbs"><a href="../index.html">Start</a> › <a href="index.html">Wissen</a> › <span>{E(t["thema"])}</span></nav>'
            f'<h1>{E(t["thema"])}</h1><div class="chips">{chips}</div>{bild}<div class="txt">{txt}</div>{audio}{mat}'
            '<p class="src">Text: Snice Unterricht (eigener Text). Bild: KI-generiertes Symbolbild (eigene Erstellung).</p>'
            '<p><a href="index.html">Alle Wissens-Texte</a> · <a href="../materialien.html">Alle Materialien</a></p></main>') + foot("../")
    os.makedirs(os.path.join(g["OUT"], "wissen"), exist_ok=True)
    open(os.path.join(g["OUT"], "wissen", t["slug"] + ".html"), "w", encoding="utf-8").write(out)
    return url


def uebersicht(g, themen):
    head, foot, SITE, bc = g["head"], g["foot"], g["SITE"], g["breadcrumb_ld"]
    url = f"{SITE}/wissen/"
    by = collections.defaultdict(list)
    for t in themen:
        by[t.get("fach") or "Weitere Themen"].append(t)
    out = head("Wissen: Sachtexte für Kinder zu Lehrplanthemen", "Kurze, leicht verständliche Sachtexte zu Themen aus den Lehrplänen, "
               "jeweils passend zu einem Arbeitsblatt mit Lückentext, Hörverstehen und Suchsel.", url, "", root="../",
               extra_ld=[bc([("Start", SITE + "/"), ("Wissen", url)])])
    body = ""
    for fach in sorted(by):
        lis = "".join(f'<li><a href="{E(t["slug"])}.html">{E(t["thema"])}</a></li>' for t in sorted(by[fach], key=lambda x: x["thema"].lower()))
        body += f'<h2>{E(fach)}</h2><ul class="tl">{lis}</ul>'
    out += (f'<main class="article-wrap ws">{CSS}<nav class="crumbs"><a href="../index.html">Start</a> › <span>Wissen</span></nav>'
            '<h1>Wissen: Sachtexte zu Lehrplanthemen</h1><p class="sub">Kurze Sachtexte für Kinder und Jugendliche. Zu jedem Text gibt es ein '
            f'Arbeitsblatt mit Lückentext, Hörverstehen und Suchsel.</p>{body}</main>') + foot("../")
    open(os.path.join(g["OUT"], "wissen", "index.html"), "w", encoding="utf-8").write(out)
    return url


def render(g, nur=None):
    themen = laden()
    if not themen:
        return 0
    os.makedirs(os.path.join(g["OUT"], "wissen"), exist_ok=True)
    urls = [seite(g, t) for t in themen if not nur or t["slug"] in nur]
    urls.append(uebersicht(g, themen))
    if "EXTRA_URLS" in g and not nur:
        g["EXTRA_URLS"].extend(urls)
    return len(urls)


if __name__ == "__main__":
    sys.path.insert(0, H)
    import build as B
    B.FOOT_COLS = B.build_foot_cols()   # wie in build.main(), damit die Fusszeile vollstaendig ist
    arg = sys.argv[1:]
    n = render(vars(B), None if (not arg or arg == ["--alle"]) else set(arg))
    print("Wissens-Seiten geschrieben:", n)
