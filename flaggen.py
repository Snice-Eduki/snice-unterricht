# -*- coding: utf-8 -*-
"""20.11.2026: erzeugt einfache, selbst gezeichnete Flaggen-SVGs (lizenzfrei) nach assets/flags/<code>.svg. Wiederholbar: python flaggen.py"""
import math, os
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "assets", "flags")
W, Hh = 30, 20
def R(x, y, w, h, c): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'
def hs(*cs): n = len(cs); return "".join(R(0, i * Hh / n, W, Hh / n + .02, c) for i, c in enumerate(cs))
def vs(*cs): n = len(cs); return "".join(R(i * W / n, 0, W / n + .02, Hh, c) for i, c in enumerate(cs))
def star(cx, cy, r, c, rot=-90):
    p = []
    for i in range(10):
        a = math.radians(rot + i * 36); rr = r if i % 2 == 0 else r * .382
        p.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(p)}" fill="{c}"/>'
def cross(cx, t, c, w=W, h=Hh): return R(0, h / 2 - t / 2, w, t, c) + R(cx - t / 2, 0, t, h, c)
F = {}
F["de"] = hs("#000", "#dd0000", "#ffce00")
F["en"] = ('<rect width="30" height="20" fill="#012169"/><path d="M0,0 30,20M30,0 0,20" stroke="#fff" stroke-width="4"/>'
           '<path d="M0,0 30,20M30,0 0,20" stroke="#c8102e" stroke-width="1.5"/><path d="M15,0V20M0,10H30" stroke="#fff" stroke-width="6.5"/>'
           '<path d="M15,0V20M0,10H30" stroke="#c8102e" stroke-width="3.8"/>')
F["es"] = R(0, 0, W, Hh, "#aa151b") + R(0, 5, W, 10, "#f1bf00")
F["fr"] = vs("#0055a4", "#fff", "#ef4135")
F["it"] = vs("#009246", "#fff", "#ce2b37")
F["nl"] = hs("#ae1c28", "#fff", "#21468b")
F["pl"] = hs("#fff", "#dc143c")
F["cz"] = hs("#fff", "#d7141a") .replace('', '') + '<path d="M0,0 15,10 0,20Z" fill="#11457e"/>'
F["se"] = R(0, 0, W, Hh, "#006aa7") + cross(10, 4, "#fecc00")
F["dk"] = R(0, 0, W, Hh, "#c8102e") + cross(10, 3.2, "#fff")
F["no"] = R(0, 0, W, Hh, "#ba0c2f") + cross(10, 5, "#fff") + cross(10, 2.6, "#00205b")
F["fi"] = R(0, 0, W, Hh, "#fff") + cross(10, 4.2, "#003580")
F["ro"] = vs("#002b7f", "#fcd116", "#ce1126")
F["hu"] = hs("#cd2a3e", "#fff", "#436f4d")
F["gr"] = "".join(R(0, i * 20 / 9, W, 20 / 9 + .02, "#0d5eaf" if i % 2 == 0 else "#fff") for i in range(9)) + R(0, 0, 11.12, 11.12, "#0d5eaf") + R(4.45, 0, 2.22, 11.12, "#fff") + R(0, 4.45, 11.12, 2.22, "#fff")
sh = '<path d="M10,5.5h6v6.2c0,3-3,4-3,4s-3-1-3-4z" fill="#ee1c25" stroke="#fff" stroke-width=".5"/>'
F["hr"] = hs("#ff0000", "#fff", "#171796") + '<path d="M12,6.6h6v5.2c0,2.4-3,3.6-3,3.6s-3-1.2-3-3.6z" fill="#fff" stroke="#ff0000" stroke-width=".4"/>' + "".join(
    R(12.4 + (i % 4) * 1.3, 7 + (i // 4) * 1.3, 1.3, 1.3, "#ff0000") for i in range(16) if (i % 4 + i // 4) % 2 == 0)
F["sk"] = hs("#fff", "#0b4ea2", "#ee1c25") + '<path d="M7,4.5h7v6.2c0,3.2-3.5,4.5-3.5,4.5S7,13.9,7,10.7z" fill="#ee1c25" stroke="#fff" stroke-width=".6"/><path d="M10.5,6v7M8.6,8h3.8M8.9,10h3.2" stroke="#fff" stroke-width=".9"/>'
F["bg"] = hs("#fff", "#00966e", "#d62612")
F["rs"] = hs("#c6363c", "#0c4076", "#fff")
F["ua"] = hs("#005bbb", "#ffd500")
F["jp"] = R(0, 0, W, Hh, "#fff") + '<circle cx="15" cy="10" r="6" fill="#bc002d"/>'
tri = lambda a, n: f'<g transform="rotate({a} 15 10) translate(15 10)">' + "".join(R(-2.4, -8 + i * 1.1 if True else 0, 4.8, .6, "#000") for i in range(n)) + "</g>"
F["kr"] = (R(0, 0, W, Hh, "#fff") + '<circle cx="15" cy="10" r="3.4" fill="#cd2e3a"/><path d="M11.6,10a3.4,3.4 0 0 0 6.8,0a1.7,1.7 0 0 0 -3.4,0a1.7,1.7 0 0 1 -3.4,0z" fill="#0047a0"/>'
           + "".join(f'<g transform="rotate({a} 15 10)">' + "".join(R(12.9, 3.2 + i * .95 - 1.6, 4.2, .55, "#000") for i in range(3)) + "</g>" for a in (-34, 34, 146, 214)))
F["cn"] = R(0, 0, W, Hh, "#de2910") + star(5, 5, 3, "#ffde00") + star(10, 2.2, 1, "#ffde00", -70) + star(12, 4.4, 1, "#ffde00", -40) + star(12, 7.4, 1, "#ffde00", -10) + star(10, 9.6, 1, "#ffde00", -60)
F["th"] = R(0, 0, W, Hh, "#a51931") + R(0, 3.33, W, 13.34, "#f4f5f8") + R(0, 6.67, W, 6.66, "#2d2a4a")
F["hi"] = hs("#ff9933", "#fff", "#138808") + '<circle cx="15" cy="10" r="2.6" fill="none" stroke="#000080" stroke-width=".5"/><circle cx="15" cy="10" r=".5" fill="#000080"/>' + "".join(
    f'<line x1="15" y1="10" x2="{15 + 2.6 * math.cos(math.radians(a * 15)):.2f}" y2="{10 + 2.6 * math.sin(math.radians(a * 15)):.2f}" stroke="#000080" stroke-width=".25"/>' for a in range(24))
F["my"] = "".join(R(0, i * 20 / 14, W, 20 / 14 + .02, "#cc0001" if i % 2 == 0 else "#fff") for i in range(14)) + R(0, 0, 15, 10.0, "#010066") + '<circle cx="5.6" cy="5" r="3" fill="#fc0"/><circle cx="6.5" cy="5" r="2.5" fill="#010066"/>' + star(9, 5, 2, "#fc0")
F["id"] = hs("#ce1126", "#fff")
F["kz"] = (R(0, 0, W, Hh, "#00afca") + '<circle cx="14" cy="8" r="3" fill="#fec50c"/>' + "".join(
    f'<line x1="{14 + 3.6 * math.cos(math.radians(a * 22.5)):.2f}" y1="{8 + 3.6 * math.sin(math.radians(a * 22.5)):.2f}" x2="{14 + 5 * math.cos(math.radians(a * 22.5)):.2f}" y2="{8 + 5 * math.sin(math.radians(a * 22.5)):.2f}" stroke="#fec50c" stroke-width=".8"/>' for a in range(16))
    + '<path d="M9,14.2c2,.9 8,.9 10,0" stroke="#fec50c" stroke-width="1" fill="none"/>' + R(2, 2, .9, 16, "#fec50c"))
def main():
    os.makedirs(OUT, exist_ok=True)
    for k, v in F.items():
        open(os.path.join(OUT, k + ".svg"), "w", encoding="utf-8").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 20" width="30" height="20" role="img"><clipPath id="c"><rect width="30" height="20" rx="1.5"/></clipPath><g clip-path="url(#c)">{v}</g></svg>')
    print(len(F), "Flaggen")
if __name__ == "__main__": main()
