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


# ---------------------------------------------------------------- Landesseiten EN/FR/ES/IT (09.11.)
LP = {
 "en": dict(slug="winter-escape-room-english-year-6", pdf=r"C:\Claude-Arbeitsblätter\Escape-Room-Winter-D5-en\Winter-Escape-Room_English_Y6.pdf", dl="Winter-Escape-Room_English_Year6.pdf",
  eduki="https://eduki.com/de/material/2412114", tpt="https://www.teacherspayteachers.com/Product/18258767", home="Home", free="Free", freeslug="free",
  title="Winter Escape Room for English Year 6 (free, 24 pages)", desc="Free winter escape room for English in Year 6 (KS2): 6 stations on word classes, verb tenses, sentence parts, spelling and reading, 2 locks, 1 magic word. Download the PDF directly.",
  h1="Winter Escape Room: English Year 6", sub="The class rescues the winter lantern: six stations, two locks, one magic word. Free and ready to print.", btn="Download the PDF directly (24 pages)", inh="What is inside?",
  li=["Six stations on word classes, verb tenses, sentence parts, spelling strategies, a non-fiction text and a story", "Two locks (a number lock and a magic word) as the solution, hint cards that never give away the answer", "Answer key, reflection sheet and certificate, about 90 minutes without a computer"],
  more="More free and paid resources:", shop="Teachers Pay Teachers", shopurl="https://www.teacherspayteachers.com/product/18258767", alle="all free resources", lang_en="English"),
 "fr": dict(slug="escape-room-hiver-francais-6e", pdf=r"C:\Claude-Arbeitsblätter\Escape-Room-Winter-D5-fr\Escape-Room_Hiver_6e.pdf", dl="Escape-Room_Hiver_Francais_6e.pdf",
  eduki="https://eduki.com/fr/material/2412103", tpt="", home="Accueil", free="Gratuit", freeslug="gratuit",
  title="Escape room d'hiver pour le français en 6e (gratuit, 24 pages)", desc="Escape room d'hiver gratuit pour le français en 6e (cycle 3) : 6 stations, 2 cadenas, 1 mot magique, cartes d'aide et corrigés. Télécharger le PDF directement.",
  h1="Escape room d'hiver : français 6e", sub="La classe sauve la lanterne d'hiver : six stations, deux cadenas, un mot magique. Gratuit, prêt à imprimer.", btn="Télécharger le PDF directement (24 pages)", inh="Que contient-il ?",
  li=["Six stations : nature des mots, temps du verbe, fonctions, orthographe, texte documentaire, texte littéraire", "Deux cadenas (un code et un mot magique) comme solution, cartes d'aide qui ne donnent jamais la réponse", "Corrigés, fiche de bilan et diplôme, environ 90 minutes sans ordinateur"],
  more="Plus de ressources gratuites et payantes :", shop="Snice sur eduki", shopurl="https://eduki.com/fr/shop/400839", alle="toutes les ressources gratuites"),
 "es": dict(slug="escape-room-invierno-lengua-1-eso", pdf=r"C:\Claude-Arbeitsblätter\Escape-Room-Winter-D5-es\Escape-Room_Invierno_ES.pdf", dl="Escape-Room_Invierno_Lengua_1ESO.pdf",
  eduki="https://eduki.com/es/material/2412110", tpt="", home="Inicio", free="Gratis", freeslug="gratis",
  title="Escape room de invierno para Lengua en 1.º ESO (gratis, 24 páginas)", desc="Escape room de invierno gratis para Lengua en 1.º ESO: 6 estaciones, 2 cerraduras, 1 palabra mágica, pistas y soluciones. Descarga el PDF directamente.",
  h1="Escape room de invierno: Lengua 1.º ESO", sub="La clase salva la linterna de invierno: seis estaciones, dos cerraduras, una palabra mágica. Gratis y listo para imprimir.", btn="Descargar el PDF directamente (24 páginas)", inh="¿Qué incluye?",
  li=["Seis estaciones: clases de palabras, tiempos verbales, sintagmas y funciones, ortografía, texto informativo y texto narrativo", "Dos cerraduras (un candado numérico y una palabra mágica) como solución, pistas que nunca revelan la respuesta", "Soluciones, hoja de reflexión y diploma, unos 90 minutos sin ordenador"],
  more="Más recursos gratuitos y de pago:", shop="Snice en eduki", shopurl="https://eduki.com/es/shop/400839", alle="todos los recursos gratuitos"),
 "it": dict(slug="escape-room-inverno-italiano-classe-prima", pdf=r"C:\Claude-Arbeitsblätter\Escape-Room-Winter-D5-it\Escape-Room_Inverno_I1.pdf", dl="Escape-Room_Inverno_Italiano_Classe1.pdf",
  eduki="https://eduki.com/it/material/2412122", tpt="", home="Home", free="Gratis", freeslug="gratis",
  title="Escape room d'inverno per l'italiano in classe prima (gratis, 24 pagine)", desc="Escape room d'inverno gratuito per l'italiano in classe prima (secondaria di I grado): 6 stazioni, 2 lucchetti, 1 parola magica, carte di aiuto e soluzioni. Scarica il PDF direttamente.",
  h1="Escape room d'inverno: italiano classe prima", sub="La classe salva la lanterna d'inverno: sei stazioni, due lucchetti, una parola magica. Gratis e pronto da stampare.", btn="Scarica subito il PDF (24 pagine)", inh="Cosa contiene?",
  li=["Sei stazioni: parti del discorso, tempi verbali, elementi della frase, ortografia, testo informativo e testo narrativo", "Due lucchetti (un codice numerico e una parola magica) come soluzione, carte di aiuto che non svelano mai la risposta", "Soluzioni, scheda di riflessione e attestato, circa 90 minuti senza computer"],
  more="Altre risorse gratuite e a pagamento:", shop="Snice su eduki", shopurl="https://eduki.com/it/shop/400839", alle="tutte le risorse gratuite"),
}


def render_i18n(g):
    """Vor i18n_build.render() aufrufen: schreibt je Sprache eine Escape-Room-Seite (Depth 1, im Sprachordner)."""
    import i18n_build as I
    B = I.B; n = 0
    for lang, c in LP.items():
        if lang not in I.SITEMAP_URLS or not os.path.exists(c["pdf"]): continue
        os.makedirs(os.path.join(B.OUT, "downloads"), exist_ok=True); shutil.copy(c["pdf"], os.path.join(B.OUT, "downloads", c["dl"]))
        url = f"{I.SITE}/{lang}/{c['slug']}.html"
        ld = [I.breadcrumb_ld([(c["home"], f"{I.SITE}/{lang}/"), (c["h1"], url)])]
        out = I.head_i18n(lang, c["title"], c["desc"], url, None, 0, extra_ld=ld)
        lis = "".join(f"<li>{E(x)}</li>" for x in c["li"])
        tpt = f' · <a href="{c["shopurl"]}" rel="noopener">{E(c["shop"])}</a>' if lang == "en" else f' · <a href="{c["shopurl"]}" rel="noopener">{E(c["shop"])}</a>'
        out += (f'<main class="article-wrap"><nav class="crumbs"><a href="./">{E(c["home"])}</a> › <span>{E(c["h1"])}</span></nav>'
                f'<h1>{E(c["h1"])}</h1><p class="sub">{E(c["sub"])}</p>'
                f'<p class="dl"><a class="btn" href="../downloads/{c["dl"]}" download>{E(c["btn"])}</a></p>'
                f'<h2>{E(c["inh"])}</h2><ul>{lis}</ul>'
                f'<p>{E(c["more"])} <a href="{c["eduki"]}" rel="noopener">eduki</a>{tpt}</p></main>') + I.foot_i18n(lang, 0)
        I.write(lang, c["slug"], out); I.SITEMAP_URLS[lang].append((url, None)); n += 1
    return n
