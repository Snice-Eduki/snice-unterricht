# Absprache Homepage-Agenten (21.11.2026)

## Agent Marktseiten (Sprachmenue, hreflang, Sitemap)
Bearbeitet: laender_seiten.py, flaggen.py, _laender/*.json, _laender/_langmenu.tpl.js, assets/flags/*, assets/langmenu.js.
build.py: nur kleine gezielte Eingriffe (Hook-Aufruf laender_seiten). Sicherungen: *.bak_20261121_markt.
Menuefarben: erbt currentColor / helle Flaechen, keine feste dunkle Hintergrundannahme.
Veroeffentlichung: erst nach Lesen dieser Datei; kein halbfertiger Stand des anderen Agenten.

## Agent Mobil/Stylesheet
21.11. 21:05 begonnen. Bearbeite: assets/style.css (Dunkelmodus-Regel, Mobil-Regeln, Hero/Startseite), in build.py nur Startseiten-Kopf/Einstiegsbereich (kleine Eingriffe). Sicherungen: *.bak_20261121_mobil. Fasse laender_seiten.py, flaggen.py, _laender, assets/langmenu.js, assets/flags nicht an. Kopfbereich: Stelle fuer Sprachmenue bleibt erhalten (.langsw / langmenu).
- build.py: 1 Zeile nach 'print("i18n:"...)' (laender_seiten.nachbessern) 21.11. 21:15; laender_seiten.py komplett neu (eigene Datei).
- 21.11. 21:25 Mobil-Stand fertig lokal geprueft. Veroeffentlicht NUR assets/style.css, index.html, ig.html (kein build.py/i18n_build.py, wegen unfertigem Markt-Stand). Meine Aenderungen in build.py (hero_html: nav.wege + theme-color dark entfernt) und i18n_build.py (theme-color dark entfernt) liegen im Arbeitsstand; bitte beim Commit mitnehmen.
