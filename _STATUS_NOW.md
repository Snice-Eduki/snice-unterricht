# Status snice-unterricht.eu — 01.09.2026

## LIVE / fertig
- **Finder mit allen 5929 Materialien** (echte eduki-Cover, deine Beschreibung, Fach-/Klasse-Filter, Sofortsuche, Direktlink zu eduki). Deployed, Pages-Build grün.
- Logo in Nav sichtbar, Favicon gesetzt.
- Pinterest-Discovery: 1 Runner stabil. Mail-Watcher `SniceMailWatch` aktiv (alle 10 Min).

## Wartet (nicht anfassen)
- **HTTPS-Cert** hängt bei Let's Encrypt (`authorization_created`). Ratsbeschluss: 24 h in Ruhe lassen (kein Remove/Re-Add). Auto-Task `SniceHomepageHttps` erzwingt HTTPS sobald stabil. Seite läuft über http.

## BLOCKIERT: Lehrplan-Detailseiten-Track (getestet 01.09.)
- `lehrplan.db` liefert saubere, themengenaue Kompetenzen NUR für Bayern (LehrplanPLUS). Andere 14 BL: lückenhaft oder Rausch. KMK-Bildungsstandards-Zeilen ebenfalls verrauscht (Prüfungsfragmente).
- Präziser Matcher (Thema in `lb_titel`): hohe Präzision, ~0/15 BL Reichweite außer Bayern.
- **→ „wortgetreu über alle 16 BL" NICHT lieferbar ohne sauberes Neu-Scrapen der Landescurricula (eigenes Projekt).**
- Kein Ausspielen partieller/verrauschter Lehrplanblöcke (Qualitätswächter). Track = datenblockiert bis saubere Datenquelle.

## Nächste sinnvolle Schritte (deliverable)
- Finder-Performance/SEO: 5,1 MB index → evtl. Lazy-Render (nur N Karten initial, Rest on-scroll) falls mobil träge.
- Google-Sichtbarkeit: sitemap.xml steht; Indexierung läuft über robots.txt.
- `_MAIL_TODO.md` abarbeiten sobald handlungsrelevante Mail eintrifft.
