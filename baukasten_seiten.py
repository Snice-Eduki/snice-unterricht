# -*- coding: utf-8 -*-
"""09.11.: Gratis-Baukasten fuer Lehrkraefte: Hub + 6 Band-Seiten (Module zum Kopieren) + PDF/DOCX-Downloads. Aufruf aus build.py: render(globals())."""
import html, json, os, shutil, glob
H = os.path.dirname(os.path.abspath(__file__))
BEL = r"C:\Claude-Arbeitsblätter\Baukasten-Elternabend\_out\eduki\de"
PROFIL = "https://eduki.com/de/shop/400839"
BAENDE = {1: ("Elternabend Klasse 1–10", ["band1"], "Einladungen, Tagesordnungen, Ansprachen, Elternvertretung, Protokolle und Themenbausteine für jeden Elternabend."),
          2: ("Der erste Schultag in Klasse 1", ["band2"], "Einschulung, erste Unterrichtsstunde, Elternbetreuung, Briefe und Erste-Woche-Plan."),
          3: ("Lernentwicklungsgespräche Klasse 1–10", ["band3"], "Leitfäden, Selbsteinschätzungs- und Beobachtungsbögen, Zielvereinbarungen und Formulierungshilfen."),
          4: ("Übertritt nach Klasse 4", ["band4"], "Beratung und Elternabend zum Übertritt mit Steckbriefen aller 16 Bundesländer."),
          5: ("Fächerwahl und Infoabende an allen Schularten", ["band5"], "Wahlpflichtfächer, Sprachenfolge, Profilwahl und Berufsorientierung mit Länder- und Schulartensteckbriefen."),
          6: ("Fächer-Steckbriefe A–Z Klasse 1–10", ["band6a", "band6b"], "Über 40 Fächer: Elternabend-Bausteine, Fach-Infoabende und Formulierungen für Gespräche.")}
CSS = """<style>
.bk h2{margin-top:2rem}.bk .mod{border:1px solid #d0d0d8;border-radius:12px;padding:1rem 1.2rem;margin:1.2rem 0}
.bk .mod h3{margin:.1rem 0 .3rem}.bk .meta{font-size:.85rem;opacity:.7}.bk .zweck{font-weight:600}
.bk button.cp{font:inherit;font-size:.85rem;padding:.35rem .8rem;border-radius:8px;border:1px solid #2a6f85;background:#2a6f85;color:#fff;cursor:pointer;margin:.3rem .3rem .3rem 0}
.bk .bst{background:rgba(255,213,79,.18);border-left:4px solid #e0b100;padding:.6rem .9rem;border-radius:6px;margin:.6rem 0;white-space:pre-wrap}
.bk table{border-collapse:collapse;width:100%;font-size:.92rem;margin:.6rem 0}.bk td,.bk th{border:1px solid #bbb;padding:.35rem .5rem;text-align:left;vertical-align:top}
.bk .hint{background:rgba(42,111,133,.12);padding:.5rem .8rem;border-radius:6px;margin:.6rem 0}.bk .src{font-size:.82rem;opacity:.7}
.bk .toc{columns:2;column-gap:2rem}.bk .toc a{display:block;padding:.1rem 0}.bk .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem}
.bk .card{border:1px solid #d0d0d8;border-radius:12px;padding:1rem}.bk .dl a{display:inline-block;margin-right:.8rem}
@media(max-width:640px){.bk .toc{columns:1}}</style>"""
JS = """<script>
document.addEventListener('click',function(e){var b=e.target.closest('button.cp');if(!b)return;var t=document.getElementById(b.dataset.t);if(!t)return;
var txt=t.innerText;var done=function(){var o=b.textContent;b.textContent='Kopiert';setTimeout(function(){b.textContent=o},1500)};
function fb(s){var a=document.createElement('textarea');a.value=s;document.body.appendChild(a);a.select();try{document.execCommand('copy')}catch(x){}a.remove()}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done,function(){fb(txt);done()})}else{fb(txt);done()}});
</script>"""
E = html.escape


def eid(nr):
    f = os.path.join(BEL, f"band{nr}", "_upload_ergebnis.json")
    try:
        return json.load(open(f, encoding="utf-8"))["url"]
    except Exception:
        return PROFIL


def blk(b, mid, k):
    t = b["t"]; x = b.get("x")
    if t == "h": return f"<h4>{E(x)}</h4>"
    if t == "p": return f"<p>{E(x)}</p>"
    if t == "ul": return "<ul>" + "".join(f"<li>{E(i)}</li>" for i in x) + "</ul>"
    if t == "ol": return "<ol>" + "".join(f"<li>{E(i)}</li>" for i in x) + "</ol>"
    if t == "check": return "<ul style='list-style:none;padding-left:0'>" + "".join(f"<li>&#9744; {E(i)}</li>" for i in x) + "</ul>"
    if t == "baustein":
        i = f"b{mid}-{k}".replace(".", "_")
        return f'<div class="bst" id="{i}">{E(x)}</div><button class="cp" data-t="{i}" type="button">Baustein kopieren</button>'
    if t == "tabelle":
        return "<div style='overflow-x:auto'><table><tr>" + "".join(f"<th>{E(c)}</th>" for c in b["kopf"]) + "</tr>" + "".join("<tr>" + "".join(f"<td>{E(c)}</td>" for c in r) + "</tr>" for r in b["zeilen"]) + "</table></div>"
    if t == "felder": return "<ul style='list-style:none;padding-left:0'>" + "".join(f"<li>{E(i)}: ____________________</li>" for i in x) + "</ul>"
    if t == "skala":
        st = b["stufen"]
        return "<div style='overflow-x:auto'><table><tr><th>Aussage</th>" + "".join(f"<th>{E(s)}</th>" for s in st) + "</tr>" + "".join("<tr><td>" + E(a) + "</td>" + "<td>&#9744;</td>" * len(st) + "</tr>" for a in x) + "</table></div>"
    if t == "linien": return f"<p>{E(x)}: ______________________________________________</p>"
    if t == "hinweis": return f'<div class="hint"><strong>Tipp:</strong> {E(x)}</div>'
    if t == "quelle": return f'<p class="src">{E(x)}</p>'
    return ""


def render(g):
    head, foot, SITE, OUT, bc, EX = g["head"], g["foot"], g["SITE"], g["OUT"], g["breadcrumb_ld"], g["EXTRA_URLS"]
    os.makedirs(os.path.join(OUT, "downloads", "baukasten"), exist_ok=True); cards = []; urls = []
    for nr, (titel, files, kurz) in BAENDE.items():
        src = os.path.join(BEL, f"band{nr}"); pdfs = glob.glob(os.path.join(src, "Baukasten*.pdf")); docs = glob.glob(os.path.join(src, "*.docx"))
        if not pdfs or not docs: continue
        for p in pdfs + docs: shutil.copy(p, os.path.join(OUT, "downloads", "baukasten", os.path.basename(p)))
        pdfn, docn = os.path.basename(pdfs[0]), os.path.basename(docs[0])
        secs = []; nmod = 0
        for fn in files:
            d = json.load(open(os.path.join(H, "_baukasten", fn + ".json"), encoding="utf-8"))
            for a in d["abschnitte"]:
                secs.append(a); nmod += len(a["module"])
        toc = "".join(f'<div><strong>{E(a["titel"])}</strong>' + "".join(f'<a href="#m{m["id"].replace(".", "_")}">{E(m["id"])} {E(m["titel"])}</a>' for m in a["module"]) + "</div>" for a in secs)
        body = ""
        for a in secs:
            body += f'<h2>{E(a["titel"])}</h2>'
            for m in a["module"]:
                mid = m["id"].replace(".", "_"); inner = "".join(blk(b, m["id"], k) for k, b in enumerate(m["bloecke"]))
                body += (f'<section class="mod" id="m{mid}"><div class="meta">Modul {E(m["id"])} · {E(m.get("typ", ""))} · {E(m.get("stufe", ""))}</div><h3>{E(m["titel"])}</h3>'
                         f'<p class="zweck">{E(m.get("zweck", ""))}</p><div id="mod{mid}">{inner}</div><button class="cp" data-t="mod{mid}" type="button">Ganzes Modul kopieren</button></section>')
        slug = f"baukasten-band-{nr}"; url = f"{SITE}/{slug}.html"; ed = eid(nr)
        desc = f"Kostenloser Baukasten für Lehrkräfte, Band {nr}: {titel}. {kurz} {nmod} Module zum Kopieren, PDF und Word zum Download."
        out = head(f"{titel} – kostenloser Baukasten für Lehrkräfte", desc, url, "", extra_ld=[bc([("Start", SITE + "/"), ("Baukasten", SITE + "/baukasten.html"), (titel, url)])])
        out += (f'<main class="article-wrap bk">{CSS}<nav class="crumbs"><a href="index.html">Start</a> › <a href="baukasten.html">Baukasten</a> › <span>Band {nr}</span></nav>'
                f'<h1>Band {nr}: {E(titel)}</h1><p class="sub">{E(kurz)} Kostenlos, {nmod} Module. Jedes Modul lässt sich mit einem Klick kopieren und anpassen.</p>'
                f'<p class="dl"><a href="downloads/baukasten/{E(pdfn)}">PDF herunterladen</a> <a href="downloads/baukasten/{E(docn)}">Word-Datei (editierbar)</a> '
                f'<a href="{E(ed)}" rel="noopener">Auf eduki ansehen</a></p>'
                '<p class="src">Rechtliche Angaben zu den Bundesländern mit Quelle und Stand November 2026; bitte vor Gebrauch bei Ihrem Kultusministerium prüfen. Texte KI-gestützt erstellt und geprüft.</p>'
                f'<h2>Inhaltsverzeichnis</h2><div class="toc">{toc}</div>{body}'
                f'<p>Weitere kostenlose Bände: <a href="baukasten.html">alle Bände des Baukastens</a> · Mehr Unterrichtsmaterial im <a href="{PROFIL}" rel="noopener">Snice-Shop auf eduki</a></p></main>{JS}') + foot()
        open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8").write(out); urls.append(url)
        cards.append(f'<div class="card"><h3>Band {nr}: {E(titel)}</h3><p>{E(kurz)}</p><p class="meta">{nmod} Module</p><p class="dl"><a href="{slug}.html">Module ansehen</a> <a href="downloads/baukasten/{E(pdfn)}">PDF</a> <a href="downloads/baukasten/{E(docn)}">Word</a> <a href="{E(ed)}" rel="noopener">eduki</a></p></div>')
    if not cards: return 0
    url = f"{SITE}/baukasten.html"
    out = head("Kostenloser Baukasten für Lehrkräfte: Elternabend, Einschulung, Gespräche, Übertritt, Fächerwahl",
               "Sechs kostenlose Bände mit über 300 Modulen für Elternabende, den ersten Schultag, Lernentwicklungsgespräche, den Übertritt nach Klasse 4 und Fächerwahl-Abende, für alle Schularten in Deutschland.", url, "",
               extra_ld=[bc([("Start", SITE + "/"), ("Baukasten", url)])])
    out += (f'<main class="article-wrap bk">{CSS}<nav class="crumbs"><a href="index.html">Start</a> › <span>Baukasten</span></nav>'
            '<h1>Baukasten für Lehrkräfte: Elternabende, Gespräche und Infoabende</h1>'
            '<p class="sub">Sechs kostenlose Bände zum Auswählen und Kopieren: Elternabend, erster Schultag in Klasse 1, Lernentwicklungsgespräche, Übertritt nach Klasse 4, Fächerwahl und Informationsabende sowie Steckbriefe für über 40 Fächer. Für alle Schularten in Deutschland, Klasse 1 bis 10.</p>'
            '<p>So geht es: Band wählen, im Inhaltsverzeichnis das passende Modul suchen, mit einem Klick kopieren und anpassen. Oder gleich das ganze Heft als PDF zum Ausdrucken oder als Word-Datei zum Bearbeiten laden.</p>'
            f'<div class="cards">{"".join(cards)}</div>'
            f'<p>Alle Bände gibt es auch kostenlos auf <a href="{PROFIL}" rel="noopener">eduki</a>. Mehr Unterrichtsmaterial finden Sie in meinem <a href="{PROFIL}" rel="noopener">Snice-Shop</a>.</p>'
            '<p class="src">Rechtliche Angaben (Stand November 2026) sind mit Quellen versehen und ersetzen keine Rechtsberatung; bitte die aktuelle Regelung beim zuständigen Kultusministerium prüfen.</p></main>') + foot()
    open(os.path.join(OUT, "baukasten.html"), "w", encoding="utf-8").write(out); urls.append(url)
    EX.extend(urls); return len(urls)
