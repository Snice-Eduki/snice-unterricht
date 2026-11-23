# -*- coding: utf-8 -*-
"""21.11.2026: Marktseiten (Landessprachen) + Sprachmenue (Flagge + Eigenname) + hreflang-Cluster.
Pro Markt  <welt>/index.html. Texte: _laender/texte.json (Uebersetzung per Gemini/ChatGPT, Quelle deutsch in _laender/quelle_de.json).
Shop-Pruefung: _laender/<welt>.json {"ok":bool,"eduki":Shop-URL,"materials":[{"title","url"}]} (Skript C:\\Skripte\\_homepage_laender\\shop_pruefen.py).
Eine Seite entsteht nur, wenn der Markt in _laender/freigabe.json steht (Text uebersetzt+gegengelesen) UND Text UND geprueftes Shop-Ergebnis (ok) vorliegen; sonst zurueckgehalten (auch nicht im Menue/hreflang).
Flaggen: assets/flags/*.svg aus flag-icons (MIT), Lizenz dort.
Aufruf aus build.py: render(globals()) und nachbessern(globals()) (nach i18n-Render). Einzeln: python laender_seiten.py"""
import html, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); E = html.escape
# (Flagge/Menuecode, Ordner, html-lang, Eigenname) - bestehende Sprachen zuerst
MENU = [("de", "", "de", "Deutsch"), ("en", "en", "en", "English"), ("es", "es", "es", "Español"), ("fr", "fr", "fr", "Français"), ("it", "it", "it", "Italiano"),
 ("nl", "nl", "nl", "Nederlands"), ("pl", "pl", "pl", "Polski"), ("cz", "cz", "cs", "Čeština"), ("se", "se", "sv", "Svenska"), ("dk", "dk", "da", "Dansk"),
 ("no", "no", "nb", "Norsk"), ("fi", "fi", "fi", "Suomi"), ("ro", "ro", "ro", "Română"), ("hu", "hu", "hu", "Magyar"), ("gr", "gr", "el", "Ελληνικά"),
 ("hr", "hr", "hr", "Hrvatski"), ("sk", "sk", "sk", "Slovenčina"), ("bg", "bg", "bg", "Български"), ("rs", "rs", "sr", "Српски"), ("ua", "ua", "uk", "Українська"),
 ("jp", "jp", "ja", "日本語"), ("kr", "kr", "ko", "한국어"), ("cn", "cn", "zh", "中文"), ("th", "th", "th", "ไทย"), ("hi", "hi", "hi", "हिन्दी"),
 ("my", "my", "ms", "Bahasa Melayu"), ("id", "id", "id", "Bahasa Indonesia"), ("kz", "kz", "kk", "Қазақша")]
NEU = MENU[5:]
FONT = 'system-ui,-apple-system,"Segoe UI","Noto Sans","Noto Sans CJK JP","Noto Sans CJK KR","Noto Sans CJK SC","Noto Sans Thai","Noto Sans Devanagari","Nirmala UI","Leelawadee UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI",sans-serif'
CSS = """<style>
.lp{max-width:62rem;margin:0 auto;padding:1.2rem 16px 2rem;font-family:%s}.lp h1{margin:.4rem 0 .6rem;line-height:1.25;font-size:clamp(1.6rem,6.5vw,2.4rem);overflow-wrap:break-word;hyphens:auto}.lp .flag{width:60px;height:45px;border-radius:4px;box-shadow:0 0 0 1px #0002;vertical-align:middle;margin-right:.6rem;object-fit:cover}
.lp ul.nutzen{list-style:none;padding:0;margin:1.2rem 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));gap:.8rem}.lp .nutzen li{border:1px solid #c8c8d0;border-radius:14px;padding:.8rem 1rem;font-weight:600;background:#fff;color:#1a1a22}
.lp .kn{display:inline-block;font-weight:700;padding:.7rem 1.4rem;border-radius:999px;background:#1a1a22;color:#fff;text-decoration:none;margin:.6rem 0}
.lp .bsp{list-style:none;padding:0;margin:1rem 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.7rem}.lp .bsp a{display:block;height:100%%;box-sizing:border-box;color:#1a1a22;background:#fff;text-decoration:none;border:1px solid #c8c8d0;border-radius:12px;padding:.7rem .9rem;font-weight:600;font-size:.95rem}
.lp .andere{margin-top:2rem;font-size:.95rem;line-height:2.2}.lp .andere a{white-space:nowrap;margin-right:.9rem}
</style>""" % FONT


def _json(*p):
    f = os.path.join(H, *p)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}


def aktiv():
    """Codes der neuen Maerkte mit Text + geprueftem Shop."""
    t = _json("_laender", "texte.json"); fr = set(_json("_laender", "freigabe.json").get("freigegeben", []))
    # 23.11.: Seiten liegen fertig im Repo (texte.json nicht mehr vorhanden) -> Menue zeigt alle Maerkte mit vorhandener Seite + geprueftem Shop
    return [c for c, d, *_ in NEU if (c in fr or os.path.exists(os.path.join(H, d, "index.html"))) and _json("_laender", c + ".json").get("ok")]


def menue_liste():
    a = set(aktiv())
    return [m for m in MENU if m in MENU[:5] or m[0] in a]


def hreflang_block(g):
    s = g["SITE"]
    tags = "".join(f'<link rel="alternate" hreflang="{l}" href="{s}/{(d + "/") if d else ""}">' for c, d, l, n in menue_liste())
    return tags + f'<link rel="alternate" hreflang="x-default" href="{s}/">'


def menu_js(out=None):
    data = [{"c": c, "d": d, "l": l, "n": n} for c, d, l, n in menue_liste()]
    src = open(os.path.join(H, "_laender", "_langmenu.tpl.js"), encoding="utf-8").read()
    open(os.path.join(out or H, "assets", "langmenu.js"), "w", encoding="utf-8").write(src.replace("%%DATA%%", json.dumps(data, ensure_ascii=False)))


def seite(g, code, ordner, lang, name):
    T = _json("_laender", "texte.json")[code]; S = _json("_laender", code + ".json")
    url = f'{g["SITE"]}/{ordner}/'
    out = g["head"](T["title"], T["desc"], url, "", root="../", title_raw=True)
    out = out.replace('<html lang="de">', f'<html lang="{lang}">').replace('"inLanguage": "de"', f'"inLanguage": "{lang}"').replace('content="de_DE"', f'content="{lang}"')
    out = out.replace("</head>", hreflang_block(g) + "</head>", 1)
    top = g["topnav"]("../", url)
    out = out.split("</head><body>")[0] + "</head><body>\n" + top + "\n"
    bsp = "".join(f'<li><a href="{E(m["url"])}" target="_blank" rel="noopener">{E(m["title"])}</a></li>' for m in S.get("materials", []))
    andere = " ".join(f'<a href="{"../" + d + "/" if d else "../"}" hreflang="{l}" lang="{l}">{E(n)}</a>' for c, d, l, n in menue_liste() if c != code)
    out += (f'<main class="lp" id="main">{CSS}<h1><img class="flag" src="../assets/flags/{code}.svg" alt="" width="60" height="45">{E(T["h1"])}</h1><p>{E(T["intro"])}</p>'
            f'<ul class="nutzen">{"".join(f"<li>{E(x)}</li>" for x in T["nutzen"])}</ul><p>{E(T["shop"])}</p>'
            f'<p><a class="kn" href="{E(S["eduki"])}" target="_blank" rel="noopener">{E(T["btn"])} →</a></p>'
            f'<h2>{E(T["mat"])}</h2><ul class="bsp">{bsp}</ul>'
            f'<p class="andere"><strong>{E(T["andere"])}:</strong> {andere}</p></main>\n'
            f'<footer class="site"><p class="big">Snice</p><p><a href="../impressum.html">Impressum</a> · <a href="../datenschutz.html">Datenschutz</a></p></footer>\n{g["NAV_SCRIPT"]}\n</body></html>')
    os.makedirs(os.path.join(g["OUT"], ordner), exist_ok=True)
    open(os.path.join(g["OUT"], ordner, "index.html"), "w", encoding="utf-8").write(out)
    return url


def render(g):
    menu_js(g.get("OUT"))
    T = _json("_laender", "texte.json")   # 23.11.: ohne Text bleibt die vorhandene Seite unveraendert (nur Menue/hreflang/Sitemap)
    urls = [seite(g, c, d, l, n) if c in T else f'{g["SITE"]}/{d}/' for c, d, l, n in NEU if c in aktiv()]
    if isinstance(g.get("EXTRA_URLS"), list):
        g["EXTRA_URLS"].extend(u for u in urls if u not in g["EXTRA_URLS"])
    return len(urls)


MARK = "<!--hl-markt-->"


def nachbessern(g):
    """Nach dem i18n-Render: hreflang der neuen Maerkte in die 5 Bestands-Startseiten (de/en/es/fr/it) eintragen (Gegenseitigkeit), idempotent."""
    s = g["SITE"]; out = g["OUT"]; n = 0
    extra = MARK + "".join(f'<link rel="alternate" hreflang="{l}" href="{s}/{d}/">' for c, d, l, nm in menue_liste()[5:]) + MARK
    for f in ("index.html", "en/index.html", "es/index.html", "fr/index.html", "it/index.html"):
        p = os.path.join(out, f)
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        t = re.sub(re.escape(MARK) + ".*?" + re.escape(MARK), "", t, flags=re.S)
        if len(menue_liste()) > 5:
            t = t.replace("</head>", extra + "</head>", 1)
        open(p, "w", encoding="utf-8").write(t); n += 1
    return n


if __name__ == "__main__":
    sys.path.insert(0, H)
    import build as B
    B.FOOT_COLS = B.build_foot_cols()
    print("Marktseiten:", render(vars(B)), "Bestandsseiten:", nachbessern(vars(B)))
