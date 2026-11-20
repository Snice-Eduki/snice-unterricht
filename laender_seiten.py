# -*- coding: utf-8 -*-
"""20.11.2026: Landessprachen-Seiten + ausklappbares Sprachmenue (Flagge + Eigenname).
Pro neuem Markt  <welt>/index.html  (Gruss, Nutzen, Materialkacheln, eduki-Welt-Link).
Daten:   _laender/<welt>.json  {"materials":[{"title":..,"url":"https://eduki.com/..","image":"https://.."}]}  (Liste waechst; fehlt die Datei, wird sie leer angelegt)
Erzeugt: <welt>/index.html, assets/langmenu.js (Menue, aus _laender/_langmenu.tpl.js), assets/flags/*.svg (flaggen.py)
Aufruf aus build.py: laender_seiten.render(globals()).  Einzeln/wiederholbar: python laender_seiten.py"""
import html, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); E = html.escape
EDUKI = "https://eduki.com/{w}/autor/400839/snice-1"
# (Flagge/Menuecode, Ordner, html-lang, Eigenname) - bestehende Sprachen zuerst
MENU = [("de", "", "de", "Deutsch"), ("en", "en", "en", "English"), ("es", "es", "es", "Español"), ("fr", "fr", "fr", "Français"), ("it", "it", "it", "Italiano"),
 ("nl", "nl", "nl", "Nederlands"), ("pl", "pl", "pl", "Polski"), ("cz", "cz", "cs", "Čeština"), ("se", "se", "sv", "Svenska"), ("dk", "dk", "da", "Dansk"),
 ("no", "no", "nb", "Norsk"), ("fi", "fi", "fi", "Suomi"), ("ro", "ro", "ro", "Română"), ("hu", "hu", "hu", "Magyar"), ("gr", "gr", "el", "Ελληνικά"),
 ("hr", "hr", "hr", "Hrvatski"), ("sk", "sk", "sk", "Slovenčina"), ("bg", "bg", "bg", "Български"), ("rs", "rs", "sr", "Српски"), ("ua", "ua", "uk", "Українська"),
 ("jp", "jp", "ja", "日本語"), ("kr", "kr", "ko", "한국어"), ("cn", "cn", "zh", "中文"), ("th", "th", "th", "ไทย"), ("hi", "hi", "hi", "हिन्दी"),
 ("my", "my", "ms", "Bahasa Melayu"), ("id", "id", "id", "Bahasa Indonesia"), ("kz", "kz", "kk", "Қазақша")]
NEU = MENU[5:]
# h1, Begruessung/Nutzen, 3 Vorteile, Platzhalter, Knopf, Ueberschrift Materialien
T = {
"nl": ("Lesmateriaal voor leraren", "Hallo, ik ben Snice. Ik maak kant-en-klare werkbladen en lesmaterialen voor leraren, zodat jij minder tijd kwijt bent aan voorbereiding.", ["Direct inzetbaar, met antwoordblad", "Bespaart uren voorbereidingstijd", "Overzichtelijk en duidelijk gestructureerd"], "Materiaal volgt binnenkort", "Naar mijn eduki-wereld", "Materialen"),
"pl": ("Materiały dydaktyczne dla nauczycieli", "Cześć, jestem Snice. Przygotowuję gotowe karty pracy i materiały lekcyjne dla nauczycieli, żebyś miał więcej czasu dla uczniów.", ["Gotowe do użycia, z kluczem odpowiedzi", "Oszczędzają godziny przygotowań", "Przejrzyste i dobrze uporządkowane"], "Materiały wkrótce", "Do mojego świata eduki", "Materiały"),
"cz": ("Výukové materiály pro učitele", "Dobrý den, jsem Snice. Vytvářím hotové pracovní listy a podklady do výuky, abyste měli na přípravu méně času a na žáky více.", ["Ihned použitelné, s řešením", "Ušetří hodiny přípravy", "Přehledné a jasně uspořádané"], "Materiály brzy přibudou", "Do mého světa eduki", "Materiály"),
"se": ("Undervisningsmaterial för lärare", "Hej, jag heter Snice. Jag skapar färdiga arbetsblad och undervisningsmaterial så att du får mer tid över till dina elever.", ["Redo att användas, med facit", "Sparar timmar av förberedelsetid", "Tydligt och välstrukturerat"], "Material kommer snart", "Till min eduki-värld", "Material"),
"dk": ("Undervisningsmateriale til lærere", "Hej, jeg hedder Snice. Jeg laver færdige arbejdsark og undervisningsmateriale, så du får mere tid til dine elever.", ["Klar til brug, med facit", "Sparer timers forberedelse", "Overskueligt og tydeligt opbygget"], "Materiale følger snart", "Til min eduki-verden", "Materialer"),
"no": ("Undervisningsmateriell for lærere", "Hei, jeg heter Snice. Jeg lager ferdige arbeidsark og undervisningsmateriell, slik at du får mer tid til elevene dine.", ["Klart til bruk, med fasit", "Sparer timer med forberedelse", "Oversiktlig og tydelig oppbygd"], "Materiell kommer snart", "Til min eduki-verden", "Materiell"),
"fi": ("Opetusmateriaalia opettajille", "Hei, olen Snice. Teen valmiita tehtävämonisteita ja opetusmateriaaleja, jotta sinulle jää enemmän aikaa oppilaille.", ["Heti käyttövalmiita, ratkaisuineen", "Säästää tuntikausia valmistelua", "Selkeitä ja hyvin jäsenneltyjä"], "Materiaalit tulossa pian", "Eduki-maailmaani", "Materiaalit"),
"ro": ("Materiale didactice pentru profesori", "Bună, sunt Snice. Creez fișe de lucru și materiale pentru lecții, gata de folosit, ca să ai mai mult timp pentru elevii tăi.", ["Gata de utilizat, cu bareme de corectare", "Economisesc ore de pregătire", "Clare și bine structurate"], "Materialele urmează în curând", "Către lumea mea eduki", "Materiale"),
"hu": ("Oktatási anyagok tanároknak", "Üdvözlöm, Snice vagyok. Kész munkalapokat és tanórai anyagokat készítek, hogy több ideje maradjon a diákjaira.", ["Azonnal használható, megoldókulccsal", "Órákat spórol az előkészítésen", "Áttekinthető, jól szerkesztett"], "Az anyagok hamarosan érkeznek", "Az eduki-világomba", "Anyagok"),
"gr": ("Εκπαιδευτικό υλικό για εκπαιδευτικούς", "Γεια σας, είμαι η Snice. Δημιουργώ έτοιμα φύλλα εργασίας και διδακτικό υλικό, ώστε να έχετε περισσότερο χρόνο για τους μαθητές σας.", ["Έτοιμο προς χρήση, με λύσεις", "Εξοικονομεί ώρες προετοιμασίας", "Σαφές και καλά δομημένο"], "Το υλικό έρχεται σύντομα", "Στον κόσμο μου στο eduki", "Υλικό"),
"hr": ("Nastavni materijali za učitelje", "Bok, ja sam Snice. Izrađujem gotove radne listove i nastavne materijale kako biste imali više vremena za svoje učenike.", ["Spremno za upotrebu, s rješenjima", "Štedi sate pripreme", "Pregledno i jasno strukturirano"], "Materijali stižu uskoro", "U moj eduki svijet", "Materijali"),
"sk": ("Učebné materiály pre učiteľov", "Dobrý deň, som Snice. Vytváram hotové pracovné listy a podklady na vyučovanie, aby ste mali viac času na svojich žiakov.", ["Ihneď použiteľné, s riešeniami", "Ušetrí hodiny prípravy", "Prehľadné a jasne usporiadané"], "Materiály čoskoro pribudnú", "Do môjho sveta eduki", "Materiály"),
"bg": ("Учебни материали за учители", "Здравейте, аз съм Snice. Създавам готови работни листове и учебни материали, за да имате повече време за своите ученици.", ["Готови за употреба, с отговори", "Спестяват часове подготовка", "Прегледни и добре структурирани"], "Материалите скоро ще бъдат добавени", "Към моя свят в eduki", "Материали"),
"rs": ("Наставни материјали за наставнике", "Здраво, ја сам Snice. Правим готове радне листове и наставне материјале како бисте имали више времена за своје ученике.", ["Спремно за употребу, са решењима", "Штеди сате припреме", "Прегледно и јасно структурисано"], "Материјали стижу ускоро", "У мој eduki свет", "Материјали"),
"ua": ("Навчальні матеріали для вчителів", "Вітаю, я Snice. Створюю готові робочі аркуші та матеріали для уроків, щоб у вас залишалося більше часу на учнів.", ["Готові до використання, з відповідями", "Заощаджують години підготовки", "Зрозумілі та чітко структуровані"], "Матеріали з’являться незабаром", "До мого світу eduki", "Матеріали"),
"jp": ("先生のための授業教材", "こんにちは、Sniceです。すぐに使えるワークシートや授業用教材を作っています。準備の時間を減らし、子どもたちと向き合う時間を増やしましょう。", ["解答付きですぐに使える", "準備にかかる時間を大幅に節約", "見やすく分かりやすい構成"], "教材は近日公開予定です", "eduki のマイワールドへ", "教材"),
"kr": ("교사를 위한 수업 자료", "안녕하세요, Snice입니다. 바로 사용할 수 있는 학습지와 수업 자료를 만들어 선생님이 학생들에게 더 많은 시간을 쓰실 수 있도록 돕습니다.", ["정답지 포함, 바로 사용 가능", "수업 준비 시간을 크게 절약", "보기 쉽고 체계적인 구성"], "자료가 곧 올라옵니다", "eduki 월드로 가기", "자료"),
"cn": ("面向教师的教学资料", "您好，我是 Snice。我制作可直接使用的练习单和课堂教学资料，帮您节省备课时间，把更多时间留给学生。", ["可直接使用，附参考答案", "节省大量备课时间", "清晰易懂、结构合理"], "资料即将上线", "前往 eduki 专区", "教学资料"),
"th": ("สื่อการสอนสำหรับครู", "สวัสดี ฉันคือ Snice ฉันสร้างใบงานและสื่อการสอนที่พร้อมใช้ เพื่อให้คุณครูมีเวลาให้นักเรียนมากขึ้น", ["พร้อมใช้งานทันที มีเฉลย", "ประหยัดเวลาเตรียมการสอนได้หลายชั่วโมง", "จัดวางชัดเจน เข้าใจง่าย"], "สื่อการสอนจะมาเร็ว ๆ นี้", "ไปที่โลก eduki ของฉัน", "สื่อการสอน"),
"hi": ("शिक्षकों के लिए शिक्षण सामग्री", "नमस्ते, मैं Snice हूँ। मैं तैयार वर्कशीट और कक्षा की सामग्री बनाती हूँ, ताकि आपके पास अपने विद्यार्थियों के लिए ज़्यादा समय बचे।", ["तुरंत उपयोग के लिए तैयार, उत्तर सहित", "तैयारी के घंटे बचाएँ", "साफ़ और सुव्यवस्थित"], "सामग्री जल्द आ रही है", "मेरे eduki संसार में जाएँ", "सामग्री"),
"my": ("Bahan pengajaran untuk guru", "Hai, saya Snice. Saya menghasilkan lembaran kerja dan bahan pengajaran siap pakai supaya anda mempunyai lebih banyak masa untuk murid anda.", ["Sedia digunakan, dengan jawapan", "Menjimatkan berjam-jam masa persediaan", "Jelas dan tersusun rapi"], "Bahan akan menyusul tidak lama lagi", "Ke dunia eduki saya", "Bahan"),
"id": ("Materi ajar untuk guru", "Halo, saya Snice. Saya membuat lembar kerja dan materi pelajaran siap pakai agar Anda punya lebih banyak waktu untuk murid-murid Anda.", ["Siap pakai, lengkap dengan kunci jawaban", "Menghemat berjam-jam waktu persiapan", "Jelas dan tersusun rapi"], "Materi segera hadir", "Ke dunia eduki saya", "Materi"),
"kz": ("Мұғалімдерге арналған оқу материалдары", "Сәлеметсіз бе, мен Snice. Мен дайын жұмыс парақтары мен сабақ материалдарын жасаймын, сонда сізде оқушыларыңызға көбірек уақыт қалады.", ["Бірден қолдануға дайын, жауаптарымен", "Дайындық сағаттарын үнемдейді", "Түсінікті және жақсы құрылымдалған"], "Материалдар жақында қосылады", "eduki әлеміме өту", "Материалдар"),
}
FONT = 'system-ui,-apple-system,"Segoe UI","Noto Sans","Noto Sans CJK JP","Noto Sans CJK KR","Noto Sans CJK SC","Noto Sans Thai","Noto Sans Devanagari","Nirmala UI","Leelawadee UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI",sans-serif'
CSS = """<style>
.lp{max-width:62rem;margin:0 auto;padding:1.2rem 16px 2rem;font-family:%s}.lp h1{margin:.4rem 0 .6rem}.lp .flag{width:60px;height:40px;border-radius:4px;box-shadow:0 0 0 1px #0002;vertical-align:middle;margin-right:.6rem}
.lp ul.nutzen{list-style:none;padding:0;margin:1.2rem 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));gap:.8rem}.lp .nutzen li{border:1px solid #c8c8d0;border-radius:14px;padding:.8rem 1rem;font-weight:600}
.lp .soon{border:2px dashed #8a8a96;border-radius:14px;padding:1.4rem;text-align:center;font-size:1.15rem;font-weight:700;margin:1rem 0}
.lp .kn{display:inline-block;font-weight:700;padding:.7rem 1.4rem;border-radius:999px;background:#111;color:#fff;text-decoration:none;margin:.6rem 0}
.lp .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:1rem;margin:1rem 0}.lp .grid a{display:block;color:inherit;text-decoration:none;border:1px solid #c8c8d0;border-radius:12px;overflow:hidden}
.lp .grid img{width:100%%;aspect-ratio:3/4;object-fit:cover;display:block;background:#eee}.lp .grid span{display:block;padding:.5rem .6rem;font-size:.9rem;font-weight:600}
.lp .andere{margin-top:2rem;font-size:.95rem;line-height:2}.lp .andere a{white-space:nowrap;margin-right:.9rem}
</style>""" % FONT


def lade(code):
    p = os.path.join(H, "_laender", code + ".json")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump({"welt": code, "eduki": EDUKI.format(w=code), "materials": []}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    d = json.load(open(p, encoding="utf-8"))
    return [m for m in d.get("materials", []) if m.get("title") and str(m.get("url", "")).startswith("https://eduki.com/")]


def menu_js():
    data = [{"c": c, "d": d, "l": l, "n": n} for c, d, l, n in MENU]
    src = open(os.path.join(H, "_laender", "_langmenu.tpl.js"), encoding="utf-8").read()
    open(os.path.join(H, "assets", "langmenu.js"), "w", encoding="utf-8").write(src.replace("%%DATA%%", json.dumps(data, ensure_ascii=False)))


def seite(g, code, ordner, lang, name):
    h1, intro, nutzen, soon, knopf, mat = T[code]
    url = f'{g["SITE"]}/{ordner}/'
    mats = lade(code); eduki = EDUKI.format(w=code)
    out = g["head"](f"{h1} · Snice", intro, url, "", root="../", title_raw=True)
    out = out.replace('<html lang="de">', f'<html lang="{lang}">').replace('"inLanguage": "de"', f'"inLanguage": "{lang}"').replace('content="de_DE"', f'content="{lang}"')
    out = out.split("</head><body>")[0] + "</head><body>\n" + (
        '<header class="topnav" id="topnav"><a class="brand" href="../index.html" aria-label="Snice"><img src="../assets/logo-h.png" alt="Snice" width="303" height="97"></a>'
        f'<nav class="links" aria-label="Snice"><a href="{eduki}" target="_blank" rel="noopener">eduki</a></nav></header>\n')
    if mats:
        zentral = '<div class="grid">' + "".join(f'<a href="{E(m["url"])}" target="_blank" rel="noopener"><img src="{E(m.get("image", ""))}" alt="{E(m["title"])}" loading="lazy"><span>{E(m["title"])}</span></a>' for m in mats) + "</div>"
    else:
        zentral = f'<div class="soon">{E(soon)}</div>'
    andere = " ".join(f'<a href="{"../" + d + "/" if d else "../"}" hreflang="{l}" lang="{l}">{E(n)}</a>' for c, d, l, n in MENU)
    out += (f'<main class="lp" id="main">{CSS}<h1><img class="flag" src="../assets/flags/{code}.svg" alt="" width="60" height="40">{E(h1)}</h1><p>{E(intro)}</p>'
            f'<ul class="nutzen">{"".join(f"<li>{E(x)}</li>" for x in nutzen)}</ul><h2>{E(mat)}</h2>{zentral}'
            f'<p><a class="kn" href="{eduki}" target="_blank" rel="noopener">{E(knopf)} →</a></p><p class="andere">{andere}</p></main>\n'
            f'<footer class="site"><p class="big">Snice</p><p><a href="../impressum.html">Impressum</a> · <a href="../datenschutz.html">Datenschutz</a></p></footer>\n{g["NAV_SCRIPT"]}\n</body></html>')
    os.makedirs(os.path.join(g["OUT"], ordner), exist_ok=True)
    open(os.path.join(g["OUT"], ordner, "index.html"), "w", encoding="utf-8").write(out)
    return url


def render(g):
    menu_js()
    urls = [seite(g, c, d, l, n) for c, d, l, n in NEU]
    if isinstance(g.get("EXTRA_URLS"), list):
        g["EXTRA_URLS"].extend(u for u in urls if u not in g["EXTRA_URLS"])
    return len(urls)


if __name__ == "__main__":
    sys.path.insert(0, H)
    import build as B
    B.FOOT_COLS = B.build_foot_cols()
    print("Landesseiten:", render(vars(B)))
