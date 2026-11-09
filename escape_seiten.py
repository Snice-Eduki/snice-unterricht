# -*- coding: utf-8 -*-
"""09.11.: Gratis-Escape-Room Winter (Deutsch Kl. 5): eigene Seite mit Direkt-Download. Aufruf aus build.py: render(globals())."""
import html, os, shutil
E = html.escape
PROFIL = "https://eduki.com/de/shop/400839"
SRC = r"C:\Claude-Arbeitsblätter\Escape-Room-Serie\_pruefung\winter-d5-de\Escape-Room_Winter_D5.pdf"
SLUG = "escape-room-winter-deutsch-klasse-5"
def render(g):
    head, foot, SITE, OUT, bc, EX = g["head"], g["foot"], g["SITE"], g["OUT"], g["breadcrumb_ld"], g["EXTRA_URLS"]
    if not os.path.exists(SRC): return 0
    os.makedirs(os.path.join(OUT, "downloads"), exist_ok=True)
    fn = "Escape-Room_Winter_Deutsch_Klasse5.pdf"; shutil.copy(SRC, os.path.join(OUT, "downloads", fn))
    url = f"{SITE}/{SLUG}.html"; titel = "Escape-Room Winter für Deutsch Klasse 5 (kostenlos, 24 Seiten)"
    desc = "Kostenloser Escape-Room für den Deutschunterricht in Klasse 5 (Mittelschule Bayern): 6 Stationen zu Wortarten und Satzgliedern, 2 Schlösser, 1 Zauberwort. PDF direkt herunterladen."
    out = head(titel, desc, url, "", extra_ld=[bc([("Start", SITE + "/"), ("Kostenlos", SITE + "/kostenlos.html"), ("Escape-Room Winter", url)])])
    out += ('<main class="article-wrap"><nav class="crumbs"><a href="index.html">Start</a> › <a href="kostenlos.html">Kostenlos</a> › <span>Escape-Room Winter</span></nav>'
            '<h1>Escape-Room Winter: Deutsch Klasse 5</h1>'
            '<p class="sub">Die Klasse rettet das Winterfest: sechs Stationen, zwei Zahlenschlösser, ein Zauberwort. Kostenlos, fertig zum Ausdrucken.</p>'
            f'<p class="dl"><a class="btn" href="downloads/{fn}" download>PDF direkt herunterladen (24 Seiten)</a></p>'
            '<h2>Was steckt drin?</h2><ul><li>Sechs Stationen zu Wortarten, Satzgliedern, Rechtschreibstrategien, Zeitformen, Schreiben und Leseverstehen</li>'
            '<li>Zwei Zahlenschlösser und ein Zauberwort als Lösung, Hilfekarten ohne verratene Lösung</li>'
            '<li>Lösungen, Rückblick und Urkunde, passend zum Lehrplan Deutsch Mittelschule Bayern, Klasse 5</li></ul>'
            f'<p>Mehr kostenloses und weiteres Material: <a href="{PROFIL}" rel="noopener">Snice-Shop auf eduki</a> · <a href="kostenlos.html">alle kostenlosen Materialien</a></p></main>') + foot()
    open(os.path.join(OUT, SLUG + ".html"), "w", encoding="utf-8").write(out); EX.append(url); return 1
