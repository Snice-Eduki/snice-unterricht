# -*- coding: utf-8 -*-
"""17.11.2026: Wissens-Seiten (nur DE) = eigene Sachtexte zu Lehrplanthemen, die als Textquelle der
Hoerverstehen-/Lueckentext-Blaetter dienen (Ersatz fuer die fruehere Klexikon-Verlinkung).
Daten (nur lokal, per .gitignore NICHT im oeffentlichen Repo): _wissen_themen.json + _wissen_bilder/ neben build.py, Liste aus
  {"thema", "slug", "fach", "klassen", "text", "bild" (optional, Datei in assets/wissen/),
   "eduki" (optional, Material-URL), "audio" (optional, Hoerseiten-URL)}
18.11.2026 (Nutzer): Seiten duerfen NUR ueber den QR-Code erreichbar sein -> kryptische Adresse w/<hmac20>.html
(Geheimnis aus Skripte, _audio_secret.py), noindex/nofollow, keine Uebersicht, keine Sitemap, kein interner Link, Bild ebenfalls kryptisch.
Ausgabe: w/<id>.html. Adresse eines Themas: url_of(slug). Aufruf aus build.py: render(globals()).
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


sys.path.insert(0, r"C:\Claude-Arbeitsblätter\Skripte")
SITE_FEST = "https://snice-unterricht.eu"


def wid(slug):
    import _audio_secret as AS
    return AS.hid("wissen", slug)


def url_of(slug):
    return f"{SITE_FEST}/w/{wid(slug)}.html"


def _geheim(out):
    """Kopf entschaerfen: nichts, was Suchmaschinen/Vorschauen einlaedt."""
    out = re.sub(r'<link rel="canonical"[^>]*>', "", out)
    out = re.sub(r'<meta (?:property="og:|name="twitter:)[^>]*>', "", out)
    out = re.sub(r'<script type="application/ld\+json">.*?</script>', "", out, flags=re.S)
    out, n = re.subn(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">', out, count=1)
    if n != 1 or "noindex" not in out or "canonical" in out or "og:" in out:
        raise RuntimeError("Wissens-Seite: Kopf nicht entschaerft")
    return out


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
    w = wid(t["slug"]); url = f"{SITE}/w/{w}.html"
    kl = t.get("klassen", ""); fach = t.get("fach", "")
    desc = (f"{t['thema']} einfach erklärt: kurzer Sachtext für Klasse {kl}" if kl else f"{t['thema']} einfach erklärt: kurzer Sachtext für die Schule")
    desc += f" ({fach})." if fach else "."
    desc += " Passend zum Arbeitsblatt mit Lückentext, Hörverstehen und Suchsel."
    cover = ""
    bn = ""
    if t.get("bild"):   # Bild unter kryptischem Namen ausliefern (Quelle bleibt ausserhalb des Web-Ordners in _wissen_bilder/)
        import shutil
        q = os.path.join(H, "_wissen_bilder", t["bild"]); bn = w + os.path.splitext(t["bild"])[1].lower()
        os.makedirs(os.path.join(g["OUT"], "assets", "w"), exist_ok=True)
        if not os.path.exists(q): raise RuntimeError("Bild fehlt: " + q)
        shutil.copyfile(q, os.path.join(g["OUT"], "assets", "w", bn))
    ld = []
    out = head(f"{t['thema']} einfach erklärt – Sachtext für Kinder", desc, url, cover, root="../", extra_ld=ld)
    chips = "".join(f"<span>{E(x)}</span>" for x in ([fach] if fach else []) + ([f"Klasse {kl}"] if kl else []))
    bild = (f'<figure><img src="../assets/w/{E(bn)}" alt="{E(t["thema"])}" loading="lazy"></figure>' if bn else "")
    txt = "".join(f"<p>{E(a)}</p>" for a in absaetze(t["text"]))
    audio = (f'<div class="box"><strong>Hörtext</strong><p>Den Text zum Anhören gibt es hier: <a href="{E(t["audio"])}" rel="noopener">Hörtext öffnen</a></p></div>' if t.get("audio") else "")
    if t.get("eduki"):
        mat = (f'<div class="box"><strong>Arbeitsblatt zum Text</strong><p>Zu diesem Sachtext gibt es ein Arbeitsblatt mit Lückentext, Wortspeicher, '
               f'Hörverstehen und Suchsel, jeweils mit Lösung.</p><p><a class="btn" href="{E(t["eduki"])}" rel="noopener">Arbeitsblatt auf eduki ansehen</a></p></div>')
    else:
        mat = ('<div class="box"><strong>Arbeitsblatt zum Text</strong><p>Zu diesem Sachtext gibt es ein Arbeitsblatt mit Lückentext, Wortspeicher, '
               f'Hörverstehen und Suchsel, jeweils mit Lösung, im <a href="{E(g["SHOP"])}" rel="noopener">Snice-Shop auf eduki</a>.</p></div>')
    out += (f'<main class="article-wrap ws">{CSS}'
            f'<h1>{E(t["thema"])}</h1><div class="chips">{chips}</div>{bild}<div class="txt">{txt}</div>{audio}{mat}'
            '<p class="src">Text: Snice Unterricht (eigener Text). Bild: KI-generiertes Symbolbild (eigene Erstellung).</p>'
            '<p><a href="../materialien.html">Alle Materialien</a></p></main>') + foot("../")
    out = _geheim(out)
    os.makedirs(os.path.join(g["OUT"], "w"), exist_ok=True)
    open(os.path.join(g["OUT"], "w", w + ".html"), "w", encoding="utf-8").write(out)
    return url


def render(g, nur=None):
    themen = laden()
    if not themen:
        return 0
    urls = [seite(g, t) for t in themen if not nur or t["slug"] in nur]   # bewusst NICHT in EXTRA_URLS/Sitemap/IndexNow
    return len(urls)


if __name__ == "__main__":
    sys.path.insert(0, H)
    import build as B
    B.FOOT_COLS = B.build_foot_cols()   # wie in build.main(), damit die Fusszeile vollstaendig ist
    arg = sys.argv[1:]
    n = render(vars(B), None if (not arg or arg == ["--alle"]) else set(arg))
    print("Wissens-Seiten geschrieben:", n)
