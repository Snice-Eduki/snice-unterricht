# Status snice-unterricht.eu — 01.09.2026 (Homepage-Kern KOMPLETT)

## ✅ FERTIG & LIVE
- **Finder mit allen 5929 Materialien**: echte eduki-Cover, deine Beschreibung, Fach-/Klasse-Filter, Sofortsuche (debounced), Direktlink zu eduki. Deployed, Pages-Build grün.
- **Performance** (mobil gemessen): Load 1,57 s (content-visibility), Tippen ruckelfrei (Debounce 180ms).
- **Logo** in Nav sichtbar + Favicon.
- **Sprach-Check:** 5764 deutsch, nur 165 EN-Titel (2,8%, legitim) → keine Filterung nötig.
- **Pinterest** 1 Runner stabil (prozess-bewusster Watchdog). **Mail-Watcher** `SniceMailWatch` alle 10 Min, klassifiziert → `_MAIL_TODO.md`.

## ⏳ WARTET (kein Eingriff nötig / möglich)
- **HTTPS-Cert** hängt bei Let's Encrypt seit ~26.08 (`authorization_created`). War 31.08 kurz issued, dann zurückgefallen. Auto-Task `SniceHomepageHttps` erzwingt es sobald stabil. **Falls dauerhaft stuck: einziger echter Fix = manueller „Enforce HTTPS"-Toggle in GitHub-Pages-Web-UI (nur via Nutzer-GitHub-Login).** Seite läuft über http. NICHT weiter per API remove/re-add (verschlimmert es).

## ⛔ BLOCKIERT
- **Lehrplan-Detailseiten:** `lehrplan.db` nur für Bayern sauber; andere BL lückenhaft/Rausch (getestet). „wortgetreu über alle 16 BL" nicht lieferbar ohne Neu-Scrapen der Landescurricula. Track ruht — NICHT erneut Keyword-Matching versuchen.

## 🔔 EREIGNISGESTEUERT
- `_MAIL_TODO.md` abarbeiten sobald eine handlungsrelevante Mail eintrifft (Kundenfrage / eduki-Materialcheck). Heikle Fälle (Recht/Erstattung) dem Nutzer vorlegen.

## Heartbeat-Modus
Kern fertig → Heartbeat = leichter Wächter: Live-Status (Pinterest/HTTPS/Mails) prüfen, `_MAIL_TODO.md` abarbeiten, nur bei echtem Bedarf handeln. Keine erfundene Zusatzarbeit.
