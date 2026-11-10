# -*- coding: utf-8 -*-
"""10.11.: Lehrplan-Themenseiten (nur DE). Daten: _lehrplan_themen.json neben build.py.
Aufruf aus build.py: prepare(globals()) nach register_material_pages(), render(globals()) vor render_material_pages()."""
import html, json, os, re, collections, hashlib

H = os.path.dirname(os.path.abspath(__file__))
MIN_MATS = 4          # weniger passende Materialien -> keine Seite
MAX_CARDS = 24
GEX = re.compile(r"landkreis|kreis\b|\bbad \w+|\bam (rhein|main|neckar|harz|inn|lech)\b|\bim (allgäu|taunus|harz|odenwald)\b|^lf \d|^lernfeld|^ce \d|^bundesminister|^bundesministerin|^\d\d-\d\d |^steckbrief bundesland|^sprechstunde|^escape|^materialpaket rechenwelten|^klassenarbeitstrainer|^vera|^esa |^msa ", re.I)
E = html.escape
ST = {"themen": [], "by_mat": {}, "by_catfach": {}, "by_fk": {}, "urls": {}}
FACH_ORDER = ["Sachunterricht", "Deutsch", "Mathematik", "Erdkunde", "Geschichte", "Politik/Sozialkunde", "Biologie", "Physik", "Chemie",
              "Religion", "Ethik & Werte und Normen", "Englisch", "DaZ/DaF", "Musik", "Kunst", "Sport"]
CSS = """<style>
.lp .chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0 1rem}.lp .chips span{border:1px solid #d0d0d8;border-radius:999px;padding:.15rem .7rem;font-size:.9rem}
.lp .lead2{max-width:62rem}.lp section.hubs,.lp section.rel{margin:2rem 0}.lp .rel ul,.lp .hubs ul{columns:2;column-gap:2rem;padding-left:1.1rem}
.lp .fachblock{margin:1.8rem 0}.lp .fachblock h3{margin:.8rem 0 .3rem}.lp .tl{columns:3;column-gap:2rem;padding-left:1.1rem}
@media(max-width:700px){.lp .rel ul,.lp .hubs ul,.lp .tl{columns:1}}</style>"""


def core(t):
    t = re.split(r"\s+(?:Lückentext|Lesespur|Prüfungstraining)", t)[0]
    t = re.split(r"\s[–-]\s", t)[0]
    t = re.sub(r"\(.*?\)", "", t)
    t = re.sub(r"^(der|die|das|ein|eine)\s+", "", t.strip(), flags=re.I)
    return t.strip().lower()


def _h(s, n):
    return int(hashlib.md5((s + str(n)).encode("utf-8")).hexdigest(), 16)


def _pick(slug, n, opts):
    return opts[_h(slug, n) % len(opts)]


def _lst(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " und " + xs[-1]


def _kl(k0, k1):
    return f"Klasse {k0}" if k0 == k1 else f"Klasse {k0}–{k1}"


def title_for(thema, k0, k1, fach):
    kl = _kl(k0, k1)
    for t in (f"{thema} – Arbeitsblätter {kl} ({fach}) mit Lösungen | Snice", f"{thema} – Arbeitsblätter {kl} ({fach}) | Snice",
              f"{thema} – Arbeitsblätter {kl} | Snice", f"{thema} Arbeitsblätter | Snice"):
        if len(t) <= 65:
            return t
    return f"{thema} Arbeitsblätter | Snice"[:65]


def prepare(g):
    katalog_de, grade_nums, as_list, fach_slug, fk_kombis, sort_mats, MAT_PAGES = (g[x] for x in (
        "katalog_de", "grade_nums", "as_list", "fach_slug", "fk_kombis", "sort_mats", "MAT_PAGES"))
    data = json.load(open(os.path.join(H, "_lehrplan_themen.json"), encoding="utf-8"))
    mats = katalog_de()
    cores = [(m, core(m["title"]), m["title"].lower()) for m in mats]
    fcount = collections.Counter(m["fach"] for m in mats if m.get("fach"))
    kcount = collections.Counter(n for m in mats for n in grade_nums(m.get("grades")))
    ST["klassenseiten"] = {n for n, c in kcount.items() if c >= 10}
    themen = []
    for d in data:
        ri = re.compile(d["include"] + r"(?![a-zäöüß]{3})", re.I)
        re_ = re.compile(d["exclude"], re.I) if d["exclude"] else None
        k0, k1 = d["klassen"]
        hit = []
        for m, c, full in cores:
            if GEX.search(c) or GEX.search(full):
                continue
            if ri.search(c) and not (re_ and re_.search(c)):
                ns = grade_nums(m.get("grades"))
                if ns and (max(ns) < k0 - 1 or min(ns) > k1 + 1):
                    continue
                hit.append(m)
        if len(hit) < MIN_MATS:
            continue
        d = dict(d); d["mats"] = hit; themen.append(d)
    # Kataloge-Fach je Thema, Klassen, Linien
    for d in themen:
        fc = collections.Counter(m["fach"] for m in d["mats"] if m.get("fach"))
        cf = [f for f, _ in fc.most_common() if fcount.get(f, 0) >= 10]
        d["catfach"] = cf[0] if cf else None
        kc = collections.Counter(n for m in d["mats"] for n in grade_nums(m.get("grades")) if d["klassen"][0] - 1 <= n <= d["klassen"][1] + 1)
        d["kc"] = kc
        d["lines"] = collections.Counter(m.get("line") for m in d["mats"])
        d["url"] = f"lehrplan-{d['slug']}.html"
    ST["themen"] = themen
    for d in themen:
        for m in d["mats"]:
            ST["by_mat"].setdefault(m["id"], []).append(d)
        if d["catfach"]:
            ST["by_catfach"].setdefault(d["catfach"], []).append(d)
            for n in range(d["klassen"][0], d["klassen"][1] + 1):
                if (d["catfach"], n) in fk_kombis():
                    ST["by_fk"].setdefault((d["catfach"], n), []).append(d)
    return len(themen)


# ------------------------------------------------------------------ Links fuer andere Seiten
def _links(ds, label, k=None, limit=14):
    ds = sorted(ds, key=lambda d: -len(d["mats"]))[:limit]
    if not ds:
        return ""
    return (f'<p class="more"><strong>{label}</strong> ' + " · ".join(f'<a href="{d["url"]}">{E(d["thema"])}</a>' for d in sorted(ds, key=lambda d: d["thema"]))
            + ' · <a href="lehrplan-themen.html">Alle Lehrplanthemen</a></p>')


def links_fach(f):
    return _links(ST["by_catfach"].get(f, []), "Themen nach Lehrplan:", limit=18)


def links_fk(f, n):
    return _links(ST["by_fk"].get((f, n), []), f"Themen in Klasse {n}:")


def mat_links(m, root="../"):
    ds = sorted(ST["by_mat"].get(m["id"], []), key=lambda d: len(d["mats"]))[:2]
    if not ds:
        return ""
    return " · Lehrplanthema: " + " · ".join(f'<a href="{root}{d["url"]}">{E(d["thema"])}</a>' for d in ds)


def home_block(root=""):
    ds = sorted(ST["themen"], key=lambda d: -len(d["mats"]))[:14]
    if not ds:
        return ""
    chips = "".join(f'<a class="chip big" href="{root}{d["url"]}">{E(d["thema"])}</a>' for d in sorted(ds, key=lambda d: d["thema"]))
    return (f'<section class="section"><div class="sec-head"><div><h2>Nach Lehrplanthema</h2><p class="lead">Von Wasserkreislauf bis Weimarer Republik: '
            f'{len(ST["themen"])} Themenseiten mit passenden Arbeitsblättern, geordnet nach Fach und Klassenstufe.</p></div>'
            f'<a class="more" href="{root}lehrplan-themen.html">Alle Lehrplanthemen →</a></div><div class="klassen">{chips}</div></section>')


# ------------------------------------------------------------------ Texte
def _stufe(k0, k1):
    if k1 <= 4: return "der Grundschule"
    if k0 >= 5: return f"der Sekundarstufe I (Klasse {k0}–{k1})" if k0 != k1 else f"Klasse {k0}"
    return f"den Klassen {k0} bis {k1}"


def _linien(d):
    L = d["lines"]; p = []
    def pl(n, a, b): return f"{n} {a if n == 1 else b}"
    if L.get("lesespur"): p.append(pl(L["lesespur"], "Lesespurgeschichte", "Lesespurgeschichten"))
    if L.get("rechenwelt"): p.append(pl(L["rechenwelt"], "Rechenwelt", "Rechenwelten"))
    if L.get("lesespaziergang"): p.append(pl(L["lesespaziergang"], "Lesespaziergang", "Lesespaziergänge"))
    if L.get("basteln"): p.append(pl(L["basteln"], "Bastelvorlage", "Bastelvorlagen"))
    if L.get("pt"): p.append(pl(L["pt"], "Prüfungstraining", "Prüfungstrainings"))
    if L.get("lueckentext"): p.append(pl(L["lueckentext"], "Lückentext mit Hörverstehen", "Lückentexte mit Hörverstehen"))
    return p


def _tit(m):
    t = re.split(r"\s[–-]\s", m["title"])[0].strip()
    return t[:48].rsplit(" ", 1)[0].rstrip(" ,:–-") if len(t) > 48 else t   # 10.11.: am Wortende kürzen


def intro_texts(d):
    s = d["slug"]; b = d["begriffe"]; k0, k1 = d["klassen"]; n = len(d["mats"])
    p2 = _pick(s, 1, [
        f"Typische Bausteine der Einheit sind {b[0]}, {b[1]} und {b[2]}; darauf aufbauend kommen {b[3]}, {b[4]} und {b[5]} zur Sprache.",
        f"Im Unterricht begegnen den Lernenden zuerst {b[0]} und {b[1]}. Wer weitergeht, behandelt {b[2]}, {b[3]}, {b[4]} sowie {b[5]}.",
        f"Zum Themenkern zählen {b[0]}, {b[1]} und {b[2]}. Als Vertiefung bieten sich {b[3]} und {b[4]} an, am Ende steht oft {b[5]}.",
        f"Die Begriffsliste dieser Einheit: {_lst(b)}.",
        f"Gearbeitet wird in der Regel an {b[0]}, {b[1]} und {b[2]}, ergänzt um {b[3]}, {b[4]} und {b[5]}.",
        f"Als roter Faden eignen sich {b[0]}, {b[1]} und {b[2]}; {b[3]}, {b[4]} und {b[5]} lassen sich je nach Klassenstufe zuschalten."])
    st = _stufe(k0, k1)
    p3 = _pick(s, 2, [
        f"In den Lehrplänen der Länder ist das Thema im Fach {d['fach']} verankert, meist in {st}. {d['lernziel']}",
        f"Die Lehrpläne der Länder sehen das Thema im Fach {d['fach']} vor, in der Regel in {st}. Als Ziel gilt: {d['lernziel'][0].lower() + d['lernziel'][1:]}",
        f"Im Fach {d['fach']} gehört das Thema nach den Lehrplänen der Länder zum festen Programm, überwiegend in {st}. {d['lernziel']}",
        f"Je nach Bundesland variiert die genaue Einordnung; üblich ist das Fach {d['fach']} in {st}. {d['lernziel']}",
        f"Wo genau im Lehrplan das Thema steht, unterscheidet sich von Land zu Land, häufig im Fach {d['fach']} in {st}. Gemeinsames Ziel: {d['lernziel'][0].lower() + d['lernziel'][1:]}"])
    top = [_tit(m) for m in d["mats"][:0]]
    seen = set(); tl = []
    for m in sorted(d["mats"], key=lambda m: (0 if re.search(r"paket", m["title"], re.I) else 1, -int(m["id"]))):
        t = _tit(m)
        if t.lower() not in seen:
            seen.add(t.lower()); tl.append(t)
        if len(tl) == 3: break
    lin = _linien(d)
    ltxt = _lst(lin) if lin else "Arbeitsblätter und Übungen"
    kn = sorted(d["kc"])
    kr = f"Klasse {kn[0]}–{kn[-1]}" if len(kn) > 1 else (f"Klasse {kn[0]}" if kn else _kl(k0, k1))
    p4 = _pick(s, 3, [
        f"Aus unserem Katalog gehören {n} Materialien zu diesem Thema, darunter {_lst(tl)}. Der Bestand umfasst {ltxt} und reicht über {kr}. {d['tipp']}",
        f"{n} passende Materialien stehen bereit, etwa {_lst(tl)}. Vertreten sind {ltxt}; die Stufen reichen über {kr}. {d['tipp']}",
        f"Die Auswahl zum Thema umfasst derzeit {n} Titel, zum Beispiel {_lst(tl)}. Dazu zählen {ltxt} für {kr}. {d['tipp']}",
        f"Zum Thema finden Sie {n} Materialien, unter anderem {_lst(tl)}, verteilt auf {ltxt} in {kr}. {d['tipp']}"])
    th = d["thema"]
    p5 = _pick(s, 7, [
        f"Für den Einstieg in {th} bieten sich Aufgaben zu {b[0]} an, zum Üben solche zu {b[1]} und {b[2]}, zur Wiederholung vor einer Lernkontrolle ein Blick auf {b[5]}. Die Lösungen liegen bei, sodass im Unterricht niemand nachschlagen muss.",
        f"Eine Reihe zu {th} lässt sich so gliedern: erst {b[0]} erarbeiten, dann {b[1]} anwenden, später {b[3]} und {b[4]} vertiefen. Zu jedem Material gehört eine Musterlösung, die Korrektur und Selbstkontrolle erleichtert.",
        f"Wer {th} auf mehrere Stunden verteilt, startet mit {b[0]}, übt an {b[2]} und schließt mit {b[4]} ab. Alle Blätter sind kopierfertig und enthalten Lösungen für die schnelle Kontrolle.",
        f"Im Alltag einer Lehrkraft zählt, dass Material sofort einsatzbereit ist: Die Blätter zu {th} greifen {b[1]}, {b[2]} und {b[3]} auf, lassen sich ausdrucken und kommen mit Lösungen, damit die Vorbereitung kurz bleibt.",
        f"Ob Vertretungsstunde, Stationenarbeit oder Hausaufgabe: Die Arbeitsblätter zu {th} lassen sich flexibel einsetzen, etwa mit {b[0]} als Auftakt und {b[5]} als Abschluss. Musterlösungen sparen die Korrekturzeit."])
    dif = ""
    L = d["lines"]
    if L.get("lesespur"): dif = _pick(s, 8, ["Zur Differenzierung eignen sich die Lesespurgeschichten mit ihren drei Niveaustufen.", "Leistungsstarke und schwächere Lesende erhalten über die Lesespurgeschichten Texte in drei Stufen."])
    elif L.get("pt"): dif = _pick(s, 8, ["Für Klasse 8 bis 10 kommen die Prüfungstrainings als kompakte Vorbereitung auf Klassenarbeiten hinzu.", "Die Prüfungstrainings bereiten gezielt auf Klassenarbeiten und Abschlussprüfungen vor."])
    elif L.get("lueckentext"): dif = _pick(s, 8, ["Die Lückentexte mit Hörverstehen verbinden Lesen, Hören und Schreiben.", "Mit den Lückentexten und dem Hörverstehen per QR-Code wird auch das Zuhören trainiert."])
    elif L.get("rechenwelt"): dif = "Die Rechenwelten verpacken die Übung in ein Rollenspiel mit drei Anforderungsstufen."
    elif L.get("lesespaziergang"): dif = "Die Lesespaziergänge bringen Bewegung ins Lesen und lassen sich in Stationen aufbauen."
    elif L.get("basteln"): dif = "Die Bastelvorlagen verbinden Sachtext und Handarbeit in einer Einheit."
    return [d["einordnung"], p2, p3, (p5 + (" " + dif if dif else "")), p4]


def faq_of(d):
    s = d["slug"]; b = d["begriffe"]; k0, k1 = d["klassen"]; n = len(d["mats"]); kc = d["kc"]
    ks = sorted(kc)
    kr = f"Klasse {ks[0]}–{ks[-1]}" if len(ks) > 1 else (f"Klasse {ks[0]}" if ks else _kl(k0, k1))
    top = kc.most_common(1)[0][0] if kc else k0
    a1 = _pick(s, 4, [
        f"Die {n} Materialien zu diesem Thema sind für {kr} ausgelegt, die meisten davon für Klasse {top}. Einzelne Titel lassen sich mit Anpassung auch eine Stufe darunter oder darüber einsetzen.",
        f"Der Schwerpunkt liegt auf Klasse {top}; insgesamt deckt die Auswahl ({n} Titel) {kr} ab. In der Beschreibung jedes Materials steht die empfohlene Stufe.",
        f"Passend sind {kr}. Von den {n} Titeln wenden sich die meisten an Klasse {top}, einige lassen sich differenzierend auch in benachbarten Stufen nutzen."])
    a2 = _pick(s, 5, [
        f"Behandelt werden unter anderem {_lst(b[:4])}. Welche Aspekte in Ihrer Klasse Vorrang haben, richtet sich nach dem Lehrplan Ihres Bundeslandes.",
        f"Die Materialien arbeiten an {_lst(b[:3])} und gehen dann weiter zu {_lst(b[3:])}. Vorab lohnt ein Blick in den Lehrplan des eigenen Bundeslandes.",
        f"Inhaltlich reicht die Auswahl von {b[0]} über {b[1]} und {b[2]} bis zu {b[4]}; Details stehen bei den einzelnen Materialien."])
    a3 = _pick(s, 6, [
        f"{d['tipp']} Danach genügt meist ein Material als Einstieg und eines zum Üben.",
        f"{d['tipp']} So entsteht aus den Blättern eine kleine Einheit, die sich auf zwei bis drei Stunden verteilen lässt.",
        f"Beginnen Sie mit einem Einstieg zu {b[0]} und ergänzen Sie nach Bedarf. {d['tipp']}"])
    return [(f"Für welche Klassenstufe passen die Arbeitsblätter zu {d['thema']}?", a1),
            (f"Welche Inhalte decken die Materialien zu {d['thema']} ab?", a2),
            (f"Wie setze ich {d['thema']} im Unterricht ein?", a3)]


def related(d, k=5):
    ids = {m["id"] for m in d["mats"]}; sc = []
    for o in ST["themen"]:
        if o is d: continue
        ov = len(ids & {m["id"] for m in o["mats"]})
        s = ov * 2 + (6 if o["fach"] == d["fach"] else 0) + (2 if abs(o["klassen"][0] - d["klassen"][0]) <= 1 else 0)
        if s > 0 and (o["fach"] == d["fach"] or ov):
            sc.append((-s, o["slug"], o))
    sc.sort(key=lambda x: (x[0], x[1]))
    out = [o for _, _, o in sc[:max(k, 4)]]
    if len(out) < 4:
        for o in sorted(ST["themen"], key=lambda o: o["slug"]):
            if o is not d and o not in out and abs(o["klassen"][0] - d["klassen"][0]) <= 2: out.append(o)
            if len(out) >= 4: break
    return out[:6]


def render(g):
    head, foot, SITE, OUT, bc, EX, il, cat_card, sort_mats, fach_slug, fk_slug, fk_kombis, ld_faq = (g[x] for x in (
        "head", "foot", "SITE", "OUT", "breadcrumb_ld", "EXTRA_URLS", "itemlist_ld", "cat_card_html", "sort_mats", "fach_slug", "fk_slug", "fk_kombis", "faq_ld_of"))
    urls = []
    for d in ST["themen"]:
        k0, k1 = d["klassen"]; url = f"{SITE}/{d['url']}"
        title = title_for(d["thema"], k0, k1, d["fach"])
        paras = intro_texts(d); faq = faq_of(d)
        words = len(" ".join(paras).split())
        mats = sorted(sort_mats(d["mats"]), key=lambda m: 0 if re.search(r"paket", m["title"], re.I) else 1)
        cards = "\n".join(cat_card(m) for m in mats[:MAX_CARDS])
        rest = (f'<p class="more">Weitere {len(mats) - MAX_CARDS} Materialien zum Thema im <a href="materialien.html?q={E(d["thema"].split()[0])}">Material-Finder</a>.</p>'
                if len(mats) > MAX_CARDS else "")
        hubs = []
        cf = d["catfach"]
        if cf:
            hubs.append(f'<li><a href="{fach_slug(cf)}.html">Alle Materialien {E(cf)}</a></li>')
            for n in range(k0, k1 + 1):
                if (cf, n) in fk_kombis(): hubs.append(f'<li><a href="{fk_slug(cf, n)}.html">Arbeitsblätter {E(cf)} Klasse {n}</a></li>')
        for n in range(k0, k1 + 1):
            if n in ST["klassenseiten"]: hubs.append(f'<li><a href="klasse-{n}.html">Unterrichtsmaterial Klasse {n}</a></li>')
        hubs_html = f'<section class="hubs"><h2>Mehr Material nach Fach und Klasse</h2><ul>{"".join(hubs)}</ul></section>' if hubs else ""
        rel = related(d)
        rel_html = (f'<section class="rel"><h2>Verwandte Lehrplanthemen</h2><ul>' + "".join(
            f'<li><a href="{o["url"]}">{E(o["thema"])}</a> <small>({E(o["fach"])}, {E(_kl(*o["klassen"]))})</small></li>' for o in rel) +
            '</ul><p><a href="lehrplan-themen.html">Alle Lehrplanthemen im Überblick</a></p></section>')
        chips = "".join(f"<span>{E(x)}</span>" for x in d["begriffe"])
        desc = (f"{d['thema']} im Unterricht: Einordnung nach Lehrplan, Lerninhalte und {len(mats)} passende Arbeitsblätter mit Lösungen "
                f"für {_kl(k0, k1)} ({d['fach']}).")[:300]
        lds = [bc([("Start", SITE + "/"), ("Lehrplanthemen", SITE + "/lehrplan-themen.html"), (d["thema"], url)]),
               il(f"{d['thema']} – Arbeitsblätter", mats), ld_faq(faq)]
        h1 = f"{d['thema']}: Arbeitsblätter für {_kl(k0, k1)} ({d['fach']})"
        body = (f'{CSS}<main class="lp article-wrap"><nav class="crumbs" aria-label="Navigationspfad"><a href="index.html">Start</a> › <a href="lehrplan-themen.html">Lehrplanthemen</a> › <span>{E(d["thema"])}</span></nav>'
                f'<h1>{E(h1)}</h1><div class="lead2">' + "".join(f"<p>{E(p)}</p>" for p in paras) + f'</div><h2>Das gehört zum Thema</h2><div class="chips">{chips}</div>'
                f'<h2>Passende Arbeitsblätter und Materialpakete</h2><div class="grid">{cards}</div>{rest}'
                f'<h2>Häufige Fragen</h2>' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)
                + hubs_html + rel_html + '</main><script>[].forEach.call(document.querySelectorAll(".card"),function(c){c.classList.add("in");});</script>')
        out = head(title, desc, url, mats[0].get("cover", "") if mats else "", extra_ld=lds, title_raw=True) + body + foot()
        open(os.path.join(OUT, d["url"]), "w", encoding="utf-8").write(out)
        urls.append(url); d["words"] = words; d["title"] = title
    # Uebersicht
    url = f"{SITE}/lehrplan-themen.html"; blocks = []
    byf = collections.defaultdict(list)
    for d in ST["themen"]: byf[d["fach"]].append(d)
    for f in sorted(byf, key=lambda f: (FACH_ORDER.index(f) if f in FACH_ORDER else 99, f)):
        gs = [d for d in byf[f] if d["klassen"][0] <= 4]; sek = [d for d in byf[f] if d["klassen"][0] > 4]
        inner = ""
        for lab, grp in (("Grundschule (Klasse 1–4)", gs), ("Sekundarstufe I (ab Klasse 5)", sek)):
            if grp:
                inner += f"<h4>{lab}</h4><ul class='tl'>" + "".join(
                    f'<li><a href="{d["url"]}">{E(d["thema"])}</a> <small>{E(_kl(*d["klassen"]))}</small></li>' for d in sorted(grp, key=lambda d: (d["klassen"][0], d["thema"]))) + "</ul>"
        blocks.append(f'<div class="fachblock"><h3 id="{E(re.sub(r"[^a-z]+", "-", f.lower()))}">{E(f)}</h3>{inner}</div>')
    n = len(ST["themen"])
    intro = (f"Wer Unterricht nach Lehrplan plant, sucht selten nach einem einzelnen Arbeitsblatt, sondern nach einem Thema: Wasserkreislauf in Klasse 4, Römer in Klasse 6, "
             f"Bruchrechnung in Klasse 5. Diese Übersicht ordnet {n} Themen aus {len(byf)} Fächern nach Fach und Klassenstufe. Jede Themenseite erklärt kurz die fachliche Einordnung, "
             "nennt die typischen Lerninhalte und führt zu den passenden Materialien. Die Zuordnung zu einzelnen Lehrplänen unterscheidet sich je Bundesland; "
             "gemeint sind hier bewusst die Themen, die in den Lehrplänen der Länder immer wieder auftauchen.")
    lds = [bc([("Start", SITE + "/"), ("Lehrplanthemen", url)]),
           {"@context": "https://schema.org", "@type": "ItemList", "name": "Arbeitsblätter nach Lehrplanthemen", "numberOfItems": n,
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": d["thema"], "url": f"{SITE}/{d['url']}"} for i, d in enumerate(ST["themen"])]}]
    out = head("Arbeitsblätter nach Lehrplanthemen | Snice", f"{n} Lehrplanthemen von Sachunterricht bis Chemie mit Arbeitsblättern und Lösungen, geordnet nach Fach und Klassenstufe.",
               url, "", extra_ld=lds, title_raw=True)
    out += (f'{CSS}<main class="lp article-wrap"><nav class="crumbs" aria-label="Navigationspfad"><a href="index.html">Start</a> › <span>Lehrplanthemen</span></nav>'
            f'<h1>Arbeitsblätter nach Lehrplanthemen</h1><div class="lead2"><p>{E(intro)}</p></div>' + "".join(blocks) +
            '<p class="more"><a href="materialien.html">Alle Materialien im Finder</a> · <a href="kostenlos.html">Kostenloses Unterrichtsmaterial</a></p></main>') + foot()
    open(os.path.join(OUT, "lehrplan-themen.html"), "w", encoding="utf-8").write(out); urls.append(url)
    EX.extend(urls)
    return len(urls)
