# 23.11.: uebersichtliche Startseite (Struktur: Hero -> Faecher -> Pakete -> Neu -> Maerkte -> Haken -> 3 Schritte -> Themen)
CSS = """<style>
.sn{max-width:1180px;margin:0 auto;padding:0 22px;box-sizing:border-box}
.sn section{margin:56px 0 0}
.sn h2{margin:0 0 6px;font-size:clamp(26px,3.4vw,38px);letter-spacing:-.03em;line-height:1.1;font-weight:700}
.sn .sub{margin:0 0 20px;color:var(--muted);font-size:17px}
.sn .kach{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.sn .kach a{display:flex;flex-direction:column;justify-content:center;min-height:92px;padding:16px 18px;border-radius:18px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s}
.sn .kach a:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
.sn .kach b{font-size:19px;font-weight:650;letter-spacing:-.01em}.sn .kach span{color:var(--muted);font-size:14px;margin-top:2px}
.sn .kach a.g{background:var(--accent);border-color:var(--accent);color:#fff}.sn .kach a.g span{color:rgba(255,255,255,.85)}
.sn .chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.sn .chips a{min-height:46px;display:inline-flex;align-items:center;padding:0 20px;border-radius:999px;background:var(--chip);border:1px solid var(--line);font-weight:600}
.sn .chips a:hover{background:var(--line)}
.sn .pak{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;padding:28px;border-radius:24px;background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--accent);box-shadow:var(--shadow)}
.sn .pak p{margin:0;color:var(--muted);font-size:17px}.sn .pak h2{margin:0 0 6px}
.sn .haken{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.sn .haken div{padding:22px;border-radius:18px;background:var(--surface);border:1px solid var(--line)}
.sn .haken b{display:block;font-size:19px;margin-bottom:4px}.sn .haken b:before{content:"✓";color:var(--accent);margin-right:8px}
.sn .haken span{color:var(--muted)}
.sn .schritte{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;counter-reset:s}
.sn .schritte div{counter-increment:s;padding:22px;border-radius:18px;background:var(--chip)}
.sn .schritte div:before{content:counter(s);display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;margin-bottom:10px}
.sn .schritte b{display:block;font-size:19px}.sn .schritte span{color:var(--muted)}
.sn .mehr{display:inline-flex;align-items:center;min-height:48px;padding:0 24px;border-radius:999px;background:var(--accent);color:#fff;font-weight:600}
@media(max-width:760px){.sn{padding:0 14px}.sn section{margin-top:40px}.sn .kach{grid-template-columns:repeat(2,1fr);gap:10px}.sn .haken,.sn .schritte{grid-template-columns:1fr}.sn .pak{padding:20px}}
</style>"""


def teile(fach_tiles, kl_chips, neu_html, lp_html):
    ft = fach_tiles.split("</a>")
    fach_tiles = "</a>".join(ft[:12]) + "</a>"
    lp = f'<section><h2>Beliebte Themen</h2>{lp_html}</section>' if len(lp_html) > 80 else ""
    schnell = [("g", "Gratis-News-Blätter", "Heute aktuell", "tagesaktuell.html"),
               ("", "Gratis-Material", "Nach Fach und Klasse", "kostenlos.html"),
               ("", "Lesespurgeschichten", "In drei Niveaustufen", "lesespurgeschichten.html"),
               ("", "Alle Materialien", "Suchen und filtern", "materialien.html")]
    a = ('<div class="kach">' + "".join(f'<a class="{c}" href="{h}"><b>{t}</b><span>{s}</span></a>' for c, t, s, h in schnell) + "</div>")
    return f"""{CSS}
<div class="sn">
<section><h2>Nach Fach stöbern</h2><p class="sub">Alles zu deinem Fach auf einer Seite.</p>
<div class="fachgrid">{fach_tiles}</div>
<p><a class="mehr" href="materialien.html">Alle Fächer ansehen</a></p>
<div class="chips">{kl_chips}</div></section>
<section><div class="pak"><div><h2>Materialpakete</h2><p>Komplette Themenpakete zum halben Einzelpreis.</p></div>
<a class="mehr" href="materialpakete.html">Pakete ansehen</a></div></section>
{neu_html}
<section><h2>Auch in anderen Sprachen</h2><p class="sub">Dieselben Materialien auf English, Español, Français, Italiano und mehr.</p>
<a class="mehr" href="material-in-anderen-sprachen.html">Sprachen und Märkte</a></section>
<section><div class="haken"><div><b>Mit Lösungen</b><span>Jedes Material mit Musterlösung.</span></div>
<div><b>Für jedes Niveau</b><span>Drei Stufen, gleiche Aufgabe.</span></div>
<div><b>Kopierfreundlich</b><span>Auch in Schwarz-Weiß.</span></div></div></section>
<section><h2>So funktioniert's</h2><p class="sub">In drei Schritten zum fertigen Unterricht.</p>
<div class="schritte"><div><b>Finden</b><span>Fach, Klasse oder Thema wählen.</span></div>
<div><b>Herunterladen</b><span>PDF mit Lösungen sofort nutzen.</span></div>
<div><b>Ausdrucken</b><span>Kopieren und loslegen.</span></div></div></section>
{lp}
</div>
"""
