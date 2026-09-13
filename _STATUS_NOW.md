# Status snice-unterricht.eu — 13.09.2026 21:20 (SEO-Offensive, Rat 20:15)

## ✅ HEUTE
- **Search Console:** Property `http://snice-unterricht.eu/` VERIFIZIERT (HTML-Datei `google4340d9074c6c83c3.html` im Repo — NIE löschen). `sitemap.xml` (Index) eingereicht. Befund vorher: Domain war Google KOMPLETT unbekannt („URL ist Google nicht bekannt“, keine Sitemaps). Indexierung beantragt: Startseite, klasse-8.html (Rest per Tageskontingent nachholen: lesespurgeschichten, pruefungstraining, lueckentexte, materialien, fach-biologie, gratis). Zugang: Google-Session im ChatGPT-Profil `chatgpt-botrowser-profile` (Skripte im Session-Scratchpad `_gsc_*.py`; Suchfeld aria-label „Jede URL…“, Button-Text „Indexierung beantragen“ via `:text-matches`).
- **Material-Detailseiten:** `material/<id>-<slug>.html` für alle DE-Materialien mit Beschreibung ≥ 200 Zeichen (5.489, Commit bc0dbe70): Title/Meta/Canonical/OG, Product-JSON-LD (Preis EUR, eduki-URL), BreadcrumbList, Facts (Fach/Klasse/Schulform/Materialart), 8 ähnliche Materialien (Fach+Linie+Klasse), Links zu Fach-/Klassen-/Linien-Seite. Finder-/Landingpage-Karten verlinken jetzt auf die Detailseite (eduki-CTA dort). Sitemap-Index: `sitemap.xml` → `sitemap-seiten.xml` + `sitemap-material-1..3.xml` (Lesespuren zuerst, `lastmod`).
- **Site-URL vorübergehend http** (`SITE` in build.py), weil das GitHub-Pages-Zertifikat weiter in `authorization_created` hängt → Canonicals/Sitemap = http = Property. Nach Cert-Ausstellung: SITE zurück auf https, https-Property anlegen (gleiche HTML-Datei), Sitemap dort neu einreichen.
- **Volltext-Beschreibungen:** `Skripte\_katalog_desc_pull.py` (v1 materials API, 6 Threads, 429-Backoff, resumefähig) → `_katalog_desc.json` (gitignored); `load_katalog()` mischt sie ein. Danach `MAT_MIN_DESC` auf 300 zurück, Build, Push.
- `grade_nums`/`as_list`: Katalogfelder (String-Repr-Listen) werden jetzt korrekt geparst (Klasse 10 war vorher falsch).

## ⛔ OFFEN
- HTTPS-Zertifikat (Nutzer: Cloudflare-Konto + Nameserver bei netcup mit TAN — einzige belastbare Lösung nach 3 Re-Requests).
- Indexierungsanträge für die restlichen Hubs (Kontingent), wöchentlicher Search-Console-Check (Seiten/Abdeckung), Backlinks: IG-Bio/Pinterest → Detailseiten.

# Status snice-unterricht.eu — 12.09.2026 18:40 (Startseite NEU, kuratiert)

## ✅ LIVE (Commit 4d7ad1f)
- **Startseite = kuratierte Landingpage (Apple-Stil, 50 KB):** Hero mit Suche (→ materialien.html?q=), 3 Nutzenkacheln, Sektionen Lesespurgeschichten / Prüfungstraining / Lückentexte (je 8 Cover-Karten + Hub-Link), Fächer-Kacheln (21), Klassen-Chips (10), Herbst-Teaser, Gratis (44), FAQ (FAQPage-Schema), Über mich. Schema.org WebSite+SearchAction, Organization, FAQPage.
- **Voll-Finder** = `materialien.html` (5.725 DE-Materialien, Suche/Filter, `?q=` vorbelegbar).
- **SEO-Landingpages:** `fach-<fach>.html` (21, mit Klassen-Filter), `klasse-<n>.html` (10), `pruefungstraining.html`, `lueckentexte.html`, `gratis.html`, `english-worksheets.html` (EN getrennt), Lesespur-Hub + 19 Unterseiten, `herbst.html`. Jede mit BreadcrumbList + ItemList, eigenem Title/Description. Footer verlinkt alle Fächer/Klassen/Materialarten. Sitemap 1.073 URLs.
- **Katalog-Bereinigung im Build (`load_katalog`)**: Junk-Titel raus („Unterrichtsmaterial", „Deckblatt …"), Titel-Dubletten → nur neueste ID (waren 23 EN-Paare + 7 DE), EN-Materialien nur auf english-worksheets. → „doppelte Vorschauen" behoben.
- `datenschutz.html`, `404.html` vorhanden.

## ⛔ OFFEN
- **HTTPS-Zertifikat** (GitHub/Let's Encrypt) seit 26.08. „authorization_created"; 12.09. 17:00 sauber neu angefordert, Task `SniceHomepageHttps` erzwingt automatisch. Bitdefender warnt Kunden bei https:// (Cert = *.github.io). DNS ist sauber (kein AAAA/CAA/DS; Health-API: alles valid). **netcup-DNS-Änderungen nicht mehr autonom möglich** (TAN kommt per Gmail, Outlook-OAuth tot). Plan B: Cloudflare (Universal SSL sofort) → braucht Cloudflare-Konto + Nameserver-Wechsel bei netcup (TAN vom Nutzer).
- eduki-Shop-Cleanup: 23 EN-Dubletten (alt+neu beide live) + 18× „Unterrichtsmaterial" + 10× „Deckblatt St" → nach Login ältere pausieren/prüfen (Datenbankmanager-Auftrag).
- Impressum-Anschrift = Platzhalter (Nutzer-Entscheidung, keine Privatadresse).
