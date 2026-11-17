# -*- coding: utf-8 -*-
r"""passend.py – thematisch passendes Material für die Homepage (Vorschlag von Fenster C, 17.11.2026, Nutzerauftrag
„auf meiner Homepage wird nie passendes Material mit gezeigt und verlinkt“). Reine Rechenlogik, schreibt nichts.
Einbau in build.py siehe EINBAU.md. Test: python -X utf8 test_passend.py"""
import collections, math, re

_W = re.compile(r"[A-Za-zÄÖÜäöüß]{3,}")


def _stamm(w):
    """Grobe Grundform: Hörszenen/Hörszene, Wortfelder/Wortfeld treffen sich."""
    if len(w) >= 6:
        for e in ("en", "er", "es", "e", "n", "s"):
            if w.endswith(e): return w[:-len(e)]
    return w


class Passend:
    def __init__(self, mats, grade_nums, as_list, stop=(), zusatz=None):
        """zusatz: {id: weiterer Sachtext} (Auszug aus _excerpts.json, Blogartikel zum Material) – macht Vorlagenseiten thematisch findbar."""
        zusatz = zusatz or {}
        """mats: Liste der Katalog-Dicts mit Detailseite (id, title, desc, fach, line, grades, cover)."""
        self.mats = {m["id"]: m for m in mats}
        self.stop = set(stop)
        self.gr = {m["id"]: set(grade_nums(as_list(m.get("grades")))) for m in mats}
        self.tt = {m["id"]: self.tok(m["title"]) for m in mats}                       # Titelwörter
        self.td = {m["id"]: self.tok((m.get("desc") or "")[:600] + " " + (zusatz.get(m["id"]) or "")[:2500]) - self.tt[m["id"]] for m in mats}   # Beschreibung
        df = collections.Counter()
        for i in self.mats:
            for t in self.tt[i] | self.td[i]: df[t] += 1
        n = max(1, len(self.mats)); self.grenze = max(40, n // 50)                    # Vorlagenwörter (>2 % aller Seiten) zählen nicht
        self.idf = {t: math.log(n / c) for t, c in df.items() if c <= self.grenze}
        self.idx = collections.defaultdict(set)
        for i in self.mats:
            for t in self.tt[i] | self.td[i]:
                if t in self.idf: self.idx[t].add(i)
        self.by_fach = collections.defaultdict(list)
        for m in mats: self.by_fach[m.get("fach", "")].append(m["id"])

    def tok(self, s):
        r = set()
        for w in _W.findall(s or ""):
            k = w.lower()
            if k in self.stop: continue
            if len(w) == 3 and not any(c.isupper() for c in w[1:]): continue      # Dreibuchstaber nur als Kürzel (DaZ, GPS, DDR)
            r.add(_stamm(k))
        return r

    def _rang(self, tt, td, fach, line, nums, ohne, k):
        pkt = collections.Counter()
        for t in tt | td:
            w = self.idf.get(t)
            if not w: continue
            for j in self.idx[t]:
                if j in ohne or not (t in tt or t in self.tt[j]): continue        # Beschreibung×Beschreibung allein ist Rauschen
                pkt[j] += w * ((2.0 if t in tt else 1.0) * (1.0 if t in self.tt[j] else 0.5))   # Titel×Titel zählt am meisten
        for j in list(pkt):                                                          # Kandidaten-Titel nur teilweise getroffen (z. B. 1 von 3 Wörtern) -> abwerten
            kt = [t for t in self.tt[j] if t in self.idf]
            if kt: pkt[j] *= 0.6 + 0.4 * sum(1 for t in kt if t in tt or t in td) / len(kt)
        def rest(j):
            x = self.mats[j]
            return ((1.0 if fach and x.get("fach") == fach else 0) + (0.5 if line and x.get("line") == line else 0)
                    + (1.0 if nums and nums & self.gr[j] else 0) + (0.3 if x.get("cover") else 0))
        thema = sorted((j for j, p in pkt.items() if p >= 3.0), key=lambda j: (-(pkt[j] + rest(j)), -int(j)))[:k]
        if len(thema) < k:                                                            # auffüllen wie bisher: gleiches Fach/Reihe/Klasse
            schon = set(thema) | set(ohne)
            fuell = sorted((j for j in self.by_fach.get(fach, []) if j not in schon), key=lambda j: (-rest(j), -int(j)))
            thema += fuell[:k - len(thema)]
        return [self.mats[j] for j in thema]

    def fuer_material(self, m, k=8):
        i = m["id"]
        return self._rang(self.tt[i], self.td[i], m.get("fach", ""), m.get("line"), self.gr[i], {i}, k)

    def fuer_text(self, titel, fach="", ohne=(), k=6):
        """Für Blogartikel/Hubs ohne eigenes Material: Thema als Freitext."""
        return self._rang(self.tok(titel), set(), fach, None, set(), set(ohne), k)

    def fuer_post(self, p, k=6):
        """Blogartikel: zuerst das Material, das der Artikel vorstellt (meta url, sonst erster eduki-Link im Text), dann Themenverwandte."""
        ids = []
        for mid in re.findall(r"/material/(\d+)", (p.get("eduki") or "") + " " + (p.get("body_md") or "")):
            if mid in self.mats and mid not in ids: ids.append(mid)
        eig = [self.mats[i] for i in ids[:2]]
        if eig:
            m = eig[0]; i = m["id"]
            rest = self._rang(self.tt[i] | self.tok(p.get("thema") or ""), self.td[i], m.get("fach", ""), m.get("line"), self.gr[i], set(ids), k - len(eig))
        else:
            rest = self.fuer_text((p.get("thema") or "") + " " + (p.get("raw_title") or p.get("title") or ""), p.get("fach", ""), k=k)
        return eig + rest
