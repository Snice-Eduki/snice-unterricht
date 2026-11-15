"""Eigene Texte für die Hub-Seiten (Fach-, Klassen-, Saisonseiten, kostenlos).

Die Texte stehen in hub_texte.json (Schlüssel = Slug). Felder je Slug:
  intro   Einleitung unter der Überschrift
  desc    Meta-Description
  sections  Liste aus [Überschrift, [Absatz, ...]]
  faq       Liste aus [Frage, Antwort]
Zahlen aus dem Katalog stehen nur als Platzhalter {n} (Anzahl Materialien der Seite) im Text,
damit nichts beim Tageslauf veraltet. Fehlt ein Slug, liefert fallback() einen datengetriebenen,
grammatisch sauberen Ersatztext, der Build scheitert also nie.
"""
import json
import os

_HIER = os.path.dirname(os.path.abspath(__file__))
_CACHE = None

# Grammatisch saubere Wendung "für ..." je Fachname. Fächer, die auf "-unterricht" enden oder nicht
# sinnvoll mit "-Unterricht" zusammengesetzt werden, stehen fest in der Tabelle.
_FUER = {
    "Biologie": "für den Biologieunterricht",
    "Chemie": "für den Chemieunterricht",
    "Deutsch": "für den Deutschunterricht",
    "Englisch": "für den Englischunterricht",
    "Erdkunde": "für den Erdkundeunterricht",
    "Geschichte": "für den Geschichtsunterricht",
    "Mathematik": "für den Mathematikunterricht",
    "Musik": "für den Musikunterricht",
    "Physik": "für den Physikunterricht",
    "Religion": "für den Religionsunterricht",
    "Sachunterricht": "für den Sachunterricht",
    "Spanisch": "für den Spanischunterricht",
    "Sport": "für den Sportunterricht",
    "Kunst": "für das Fach Kunst",
    "Wirtschaft": "für das Fach Wirtschaft",
    "Arbeitslehre": "für das Fach Arbeitslehre",
    "Hauswirtschaft": "für das Fach Hauswirtschaft",
    "Politik/Sozialkunde": "für das Fach Politik/Sozialkunde",
    "DaZ/DaF": "für den Unterricht in DaZ/DaF",
    "Digitale Bildung": "für das Thema Digitale Bildung",
    "Fachübergreifendes": "für den fächerübergreifenden Unterricht",
}


def fach_fuer(f):
    """'für den Deutschunterricht', 'für den Sachunterricht', 'für das Fach Kunst' ..."""
    if f in _FUER:
        return _FUER[f]
    if f.endswith("unterricht"):
        return "für den " + f
    if f.endswith("(BS)"):
        return "für den Berufsschulunterricht im Bereich " + f.replace("(BS)", "").strip(" ,")
    return "für das Fach " + f


def fach_in(f):
    """'in Kunst', 'im Sachunterricht' für Sätze mit Ortsangabe."""
    s = fach_fuer(f)
    if s.startswith("für den "):
        return "im " + s[len("für den "):]
    if s.startswith("für das Fach "):
        return "im Fach " + s[len("für das Fach "):]
    return s.replace("für ", "bei ", 1)


def pl(n, one, many, fmt=None):
    """Zähl-Baustein mit richtiger Einzahl/Mehrzahl: pl(1, 'Lückentext', 'Lückentexte') -> '1 Lückentext'."""
    z = fmt(n) if fmt else str(n)
    return f"{z} {one if n == 1 else many}"


# Einzahl/Mehrzahl je Produktlinie (Nominativ)
LINE_WORT = {
    "lesespur": ("Lesespurgeschichte", "Lesespurgeschichten"),
    "lueckentext": ("Lückentext mit Hörverstehen", "Lückentexte mit Hörverstehen"),
    "pt": ("Prüfungstraining", "Prüfungstrainings"),
    "basteln": ("Bastelvorlage", "Bastelvorlagen"),
    "rechenwelt": ("Rechenwelt", "Rechenwelten"),
    "lesespaziergang": ("Lesespaziergang", "Lesespaziergänge"),
}
LINE_KURZ = {
    "lueckentext": ("Lückentext", "Lückentexte"),
}


def lines_text(lines, order=("lesespur", "lesespaziergang", "rechenwelt", "basteln", "pt", "lueckentext"),
               kurz=False, fmt=None):
    """['3 Lesespurgeschichten', '1 Prüfungstraining', ...] aus Counter {line: n}."""
    teile = []
    for k in order:
        n = lines.get(k, 0)
        if n:
            one, many = (LINE_KURZ.get(k) if kurz and k in LINE_KURZ else LINE_WORT[k])
            teile.append(pl(n, one, many, fmt))
    return teile


def aufzaehlung(teile):
    """['a', 'b', 'c'] -> 'a, b und c'."""
    teile = list(teile)
    if len(teile) <= 1:
        return "".join(teile)
    return ", ".join(teile[:-1]) + " und " + teile[-1]


def laden():
    global _CACHE
    if _CACHE is None:
        p = os.path.join(_HIER, "hub_texte.json")
        try:
            with open(p, encoding="utf-8") as fh:
                _CACHE = json.load(fh)
        except (OSError, ValueError):
            _CACHE = {}
    return _CACHE


def _ersetze(s, n, nfmt):
    return s.replace("{n}", nfmt(n)) if isinstance(s, str) else s


def get(slug, n=0, nfmt=str):
    """Text-Dict für den Slug (Platzhalter {n} ersetzt) oder None."""
    t = laden().get(slug)
    if not t or not t.get("sections"):
        return None
    return {
        "intro": _ersetze(t.get("intro", ""), n, nfmt),
        "desc": _ersetze(t.get("desc", ""), n, nfmt),
        "sections": [[_ersetze(h, n, nfmt), [_ersetze(a, n, nfmt) for a in absaetze]]
                     for h, absaetze in t["sections"]],
        "faq": [[_ersetze(q, n, nfmt), _ersetze(a, n, nfmt)] for q, a in t.get("faq", [])],
    }


def fallback(name, wofuer, beispiele, n, lines_txt, nfmt=str):
    """Ersatztext aus Katalogdaten, falls für einen Slug noch kein eigener Text vorliegt.
    name: Seitenname, wofuer: z. B. 'für den Deutschunterricht' oder 'für die 3. Klasse',
    beispiele: Liste echter Titel, lines_txt: Liste wie ['3 Lesespurgeschichten']."""
    bsp = aufzaehlung([f"„{b}“" for b in beispiele[:4]])
    absatz = (f"Auf dieser Seite sammle ich {nfmt(n)} Materialien {wofuer}"
              + (f", darunter {aufzaehlung(lines_txt)}" if lines_txt else "")
              + ". Alle sind kopierfertig und enthalten Lösungen.")
    if bsp:
        absatz += f" Zum Einstieg eignen sich zum Beispiel {bsp}."
    return {
        "sections": [[f"Unterrichtsmaterial: {name}", [absatz]]],
        "faq": [],
    }
