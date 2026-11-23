# -*- coding: utf-8 -*-
"""23.11.2026: Seite "Tagesaktuell – Gratis-Unterrichtsbegleitmaterial" (tagesaktuell.html). Aufruf aus build.py: render(globals()).
Datenquelle: _tagesaktuell.json (schreibt C:\\Skripte\\haus_b\\nachrichten_reel\\vorlage\\tagesaktuell_veroeffentlichen.py), PDFs liegen unter tagesaktuell/<Datum>/.
Zu jedem Thema des taeglichen Nachrichten-Reels "Dein Morgen-Update": Schueler-Arbeitsblatt (PDF) + Loesungsblatt fuer Lehrkraefte (PDF)."""
import html, json, os, datetime

H = os.path.dirname(os.path.abspath(__file__))
WT = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
CSS = """<style>
.ta .lead{font-size:1.08rem}.ta h2{margin-top:2.2rem}.ta .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin:1rem 0}
.ta .tk{border:1px solid var(--line,#d0d0d8);border-radius:14px;overflow:hidden;background:var(--surface,transparent);display:flex;flex-direction:column}
.ta .tk img{width:100%;height:auto;aspect-ratio:1/1.41;object-fit:cover;background:#e8f0fa;display:block}
.ta .tk .b{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}.ta .tk h3{margin:0;font-size:1.05rem;line-height:1.3}
.ta .tk .fach{font-size:.82rem;color:var(--muted,#666)}.ta .tk p{margin:0;font-size:.92rem}
.ta .tk .dl{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto}.ta .tk .dl a{display:inline-block;padding:10px 14px;border-radius:10px;border:1px solid var(--line,#999);text-decoration:none;font-weight:600;font-size:.92rem}
.ta .tk .dl a.pri{background:#1f5fa8;color:#fff;border-color:#1f5fa8}
.ta .hinweis{border-left:4px solid #e0b100;background:rgba(224,177,0,.12);padding:.7rem 1rem;border-radius:8px;margin:1rem 0}
.ta details{margin:1rem 0}.ta summary{cursor:pointer;font-weight:600;padding:.4rem 0}
.ta .nach{font-size:.8rem;color:var(--muted,#666)}
@media(max-width:640px){.ta .cards{grid-template-columns:1fr}}</style>"""


def _datum(d):
    x = datetime.date.fromisoformat(d); return f"{WT[x.weekday()]}, {x.day}. {MON[x.month - 1]} {x.year}"


def render(g):
    p = os.path.join(H, "_tagesaktuell.json")
    if not os.path.exists(p): print("Tagesaktuell: keine Daten", flush=True); return 0
    tage = sorted(json.load(open(p, encoding="utf-8"))["tage"], key=lambda t: t["datum"], reverse=True)
    e = html.escape
    g["PAGE_DESC"]["tagesaktuell"] = ("Tagesaktuell: kostenlose Arbeitsblätter für Schülerinnen und Schüler (Klasse 5–10) zu den Themen des täglichen Nachrichten-Reels – "
                                      "mit Lesetext in einfacher Sprache, Kartenaufgabe und Lösungsblatt für Lehrkräfte.")
    def karte(t, th):
        return (f'<article class="tk"><a href="{e(th["pdf"])}" download aria-label="Arbeitsblatt herunterladen"><img src="{e(th["thumb"])}" alt="Deckblatt: {e(th["titel"])}" loading="lazy" width="424" height="600"></a>'
                f'<div class="b"><span class="fach">{e(th["fach"])} · Klasse 5–10</span><h3>{e(th["titel"])}</h3><p>{e(th["teaser"])}</p>'
                f'<div class="dl"><a class="pri" href="{e(th["pdf"])}" download>Arbeitsblatt (PDF)</a><a href="{e(th["loesung"])}" download>Lösung für Lehrkräfte</a></div>'
                f'<span class="nach">Foto: {e(th["foto"])}</span></div></article>')
    teile = []
    for i, t in enumerate(tage):
        kopf = f'<h2 id="t{t["datum"]}">{_datum(t["datum"])}</h2>'
        cards = '<div class="cards">' + "".join(karte(t, th) for th in t["themen"]) + "</div>"
        teile.append(kopf + cards if i < 7 else None)
    neu = "".join(x for x in teile if x)
    alt = "".join(f'<h3>{_datum(t["datum"])}</h3><ul>' + "".join(f'<li>{e(th["titel"])}: <a href="{e(th["pdf"])}" download>Arbeitsblatt</a> · <a href="{e(th["loesung"])}" download>Lösung</a></li>' for th in t["themen"]) + "</ul>" for t in tage[7:])
    archiv = f"<details><summary>Ältere Tage ({len(tage) - 7})</summary>{alt}</details>" if alt else ""
    inner = f"""{CSS}<div class="ta"><h1>Tagesaktuell – Gratis-Unterrichtsbegleitmaterial</h1>
<p class="lead">Zu jedem Thema aus dem täglichen Nachrichten-Reel „Dein Morgen-Update“ gibt es hier ein <strong>kostenloses Arbeitsblatt für Schülerinnen und Schüler</strong> (Klasse 5–10): Lesetext in einfacher Sprache, vier bis sechs Aufgaben mit einer Kartenaufgabe, Platz für die Antworten und ein Lösungsblatt mit genauer Punkteverteilung für Lehrkräfte.</p>
<ul><li>Jeden Tag neu: fünf Themen aus den Nachrichten der letzten 24 Stunden, sachlich und kindgerecht aufbereitet.</li>
<li>Sofort einsetzbar: ausdrucken und verteilen, als Morgenkreis, Vertretungsstunde oder Hausaufgabe.</li>
<li>Behutsam bei ernsten Themen: keine Gewaltdetails, Hinweise zum Umgang mit belastenden Nachrichten.</li></ul>
<p class="hinweis">Die Fotos sind frei lizenzierte Bilder von Wikimedia Commons (Nachweis am Blatt) und zeigen den Ort oder das Thema, nicht das Ereignis. Die Texte beruhen auf mindestens zwei unabhängigen Meldungen; Quellen stehen im Lösungsblatt.</p>
{neu}{archiv}
<p>Mehr kostenloses Material findest du unter <a href="kostenlos.html">Kostenloses Unterrichtsmaterial</a>. Im <a href="newsletter.html">Newsletter</a> gibt es regelmäßig neue Ideen und Geschenke.</p></div>"""
    g["render_page"]("tagesaktuell", "Tagesaktuell – Gratis-Unterrichtsbegleitmaterial für Schüler (Klasse 5–10)", inner)
    url = g["SITE"] + "/tagesaktuell.html"
    if url not in g["EXTRA_URLS"]: g["EXTRA_URLS"].append(url)
    print("Tagesaktuell:", len(tage), "Tage", flush=True)
    return len(tage)
