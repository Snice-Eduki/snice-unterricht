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
