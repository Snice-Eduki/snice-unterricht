# -*- coding: utf-8 -*-
"""18.11.2026 (Nutzerauftrag): Notenrechner fuer Lehrkraefte.
Seiten:  noten.html            freier Prozent-Notenschluessel, Noten 1-6            (kurze Adresse: snice-unterricht.eu/noten)
         noten-oberstufe.html  fester Schluessel der KMK-Oberstufenvereinbarung, 15-0 Notenpunkte
         noten-ihk.html        fester IHK-Schluessel (100-Punkte-Schluessel) fuer Berufsschule/Abschlusspruefungen
Datenschutz: reine Browser-Rechnung. Kein Speichern (kein Cookie, kein localStorage), kein Formularversand, keine Fremdeinbindung;
eine Content-Security-Policy (connect-src 'none', form-action 'none') verhindert das technisch. Vorbelegung aus dem QR-Code nur ueber
den #-Teil der Adresse (wird nie an den Server gesendet):  #p=16,30&kl=2
Aufruf aus build.py: noten_seiten.render(globals()).  Einzeln: python noten_seiten.py"""
import html, json, os, re, sys

H = os.path.dirname(os.path.abspath(__file__))
E = html.escape
SEITEN = [
    dict(datei="noten.html", titel="Notenrechner für Lehrkräfte: Notenschlüssel in Prozent, Notenliste und Durchschnitt",
         h1="Notenrechner mit eigenem Notenschlüssel",
         desc="Kostenloser Notenrechner für Lehrkräfte: Prozent-Notenschlüssel und Gesamtpunktzahl eintragen, Punkte je Schüler eingeben, Noten und Notendurchschnitt sehen und als Übersichtsblatt drucken. Ohne Anmeldung, alle Daten bleiben im Browser.",
         intro="Tragen Sie den Prozent-Notenschlüssel Ihrer Schule und die Gesamtpunktzahl ein. Der Rechner zeigt sofort die Punktegrenzen und zu jeder Punktzahl die Note. Am Ende drucken Sie ein Übersichtsblatt mit Notenverteilung und Durchschnitt.",
         cfg=dict(skala=6, fest=False, grenzen=[92, 81, 67, 50, 30, 0], quelle="")),
    dict(datei="noten-oberstufe.html", titel="Notenrechner Oberstufe: Notenpunkte 15 bis 0 nach dem KMK-Schlüssel",
         h1="Notenrechner Oberstufe (15 bis 0 Notenpunkte)",
         desc="Notenpunkte-Rechner für die gymnasiale Oberstufe: fester Prozent-Schlüssel der KMK-Oberstufenvereinbarung, Punkte je Schüler eingeben, Notenpunkte und Durchschnitt sehen und als Übersichtsblatt drucken. Alle Daten bleiben im Browser.",
         intro="Diese Seite rechnet mit dem festen Prozent-Schlüssel der Abiturprüfung (15 bis 0 Notenpunkte). Tragen Sie nur die Gesamtpunktzahl und die erreichten Punkte ein.",
         cfg=dict(skala=15, fest=True, grenzen=[95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 33, 27, 20, 0],
                  quelle="Schlüssel: Vereinbarung der Kultusministerkonferenz zur Gestaltung der gymnasialen Oberstufe und der Abiturprüfung, Anlage 1 (Bewertungsraster der schriftlichen Abiturprüfung). Für Klausuren während der Oberstufe kann Ihre Schule oder Fachschaft davon abweichen. Dann nutzen Sie die Schaltfläche „Schlüssel anpassen“.")),
    dict(datei="noten-ihk.html", titel="Notenrechner IHK-Schlüssel: Punkte in Noten umrechnen",
         h1="Notenrechner mit dem IHK-Schlüssel",
         desc="Notenrechner für Berufsschule und Ausbildung: fester IHK-Notenschlüssel (92, 81, 67, 50, 30 Prozent), Punkte je Schüler eingeben, Noten und Durchschnitt sehen und als Übersichtsblatt drucken. Alle Daten bleiben im Browser.",
         intro="Diese Seite rechnet mit dem festen Schlüssel der Industrie- und Handelskammern (100-Punkte-Schlüssel). Tragen Sie nur die Gesamtpunktzahl und die erreichten Punkte ein.",
         cfg=dict(skala=6, fest=True, grenzen=[92, 81, 67, 50, 30, 0],
                  quelle="Schlüssel: 100-Punkte-Schlüssel der Industrie- und Handelskammern für Zwischen- und Abschlussprüfungen (sehr gut ab 92 %, gut ab 81 %, befriedigend ab 67 %, ausreichend ab 50 %, mangelhaft ab 30 %). Viele berufliche Schulen verwenden ihn auch für Schulaufgaben. Legt Ihre Schule etwas anderes fest, nutzen Sie die Schaltfläche „Schlüssel anpassen“.")),
]
CSS = """<style>
.nr{max-width:62rem}.nr h2{margin:1.6rem 0 .5rem;font-size:1.3rem}
.nr .ds{border:2px solid #2e7d32;border-radius:14px;padding:.8rem 1.1rem;margin:1rem 0}
.nr .karte{border:1px solid #c8c8d0;border-radius:14px;padding:.9rem 1.1rem;margin:.8rem 0}
.nr .feld{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.7rem 1rem}
.nr label{display:block;font-weight:600;font-size:.95rem}
.nr input[type=text],.nr input[type=number],.nr input[type=date],.nr select{font:inherit;width:100%;box-sizing:border-box;padding:.4rem .55rem;border:1.5px solid #8a8a96;border-radius:8px;background:#fff;color:#111}
.nr table{border-collapse:collapse;width:100%}.nr th,.nr td{border:1px solid #c8c8d0;padding:.3rem .5rem;text-align:left;vertical-align:middle}
.nr th{font-size:.9rem}.nr #liste table{table-layout:fixed}.nr td input{min-width:0}.nr td.z{text-align:center;font-weight:700;white-space:nowrap}
.nr .sk td input{max-width:5.5rem}.nr .zwei{display:grid;grid-template-columns:repeat(auto-fit,minmax(19rem,1fr));gap:.8rem 1.2rem;align-items:start}
.nr .bal{display:inline-block;height:.9rem;background:#555;border-radius:3px;vertical-align:middle;min-width:1px}
.nr .knopf{font:inherit;font-weight:700;padding:.55rem 1.1rem;border-radius:999px;border:2px solid #111;background:#111;color:#fff;cursor:pointer;margin:.3rem .5rem .3rem 0}
.nr .knopf.h{background:transparent;color:inherit;border-color:currentColor}.nr .warn{color:#b00020;font-weight:700}.nr .falsch{border-color:#b00020!important;background:#fde7ea!important}
.nr .klein{font-size:.9rem;opacity:.85}.nr .kopfdruck,.nr .fussdruck{display:none}.nr .mw{font-size:1.5rem;font-weight:800}
@media print{@page{size:A4;margin:14mm}
 body>*:not(main){display:none!important}body{background:#fff!important;color:#000!important}
 .nr{max-width:none;font-size:10.5pt;color:#000}.nr .nd{display:none!important}.nr .kopfdruck,.nr .fussdruck{display:block}
 .nr h1{font-size:16pt;margin:0 0 2mm}.nr h2{font-size:12pt;margin:4mm 0 1.5mm}.nr .karte{border:0;padding:0;margin:0}
 .nr input,.nr select{border:0!important;padding:0!important;background:transparent!important;color:#000!important;-webkit-appearance:none;appearance:none}
 .nr th,.nr td{border-color:#000;padding:1mm 1.6mm;color:#000}.nr table{break-inside:auto}.nr tr{break-inside:avoid}.nr .zwei{grid-template-columns:1fr 1fr;gap:5mm}
 .nr .falsch{background:transparent!important;color:transparent!important}.nr .np15 #liste td{height:4.6mm;padding-top:.2mm;padding-bottom:.2mm;font-size:9.5pt;line-height:1.1}.nr.np15 #liste input{height:4mm;font-size:9.5pt}.nr.np15 h2{margin:2mm 0 1mm}.nr input{outline:0!important}.nr #liste td,.nr #liste th{height:auto;padding:.9mm 1.6mm!important;line-height:1.15!important}.nr #liste input{min-height:0!important;height:4.2mm!important;line-height:1.1!important;margin:0!important;display:block}.nr.np15 #liste td{padding:.3mm 1.6mm!important}.nr #sk td,.nr #vert td,.nr #sk th,.nr #vert th{padding:.3mm 1.6mm}.nr .sk15 td,.nr .sk15 th{font-size:9pt;padding:0 1.6mm!important}.nr .fussdruck p{margin:3mm 0 0}.nr.np15 #liste input{height:3.3mm!important;font-size:9pt!important}.nr.np15 #liste td,.nr.np15 #liste th{font-size:9pt;line-height:1.05!important;padding:.2mm 1.6mm!important}.nr.np15 .fussdruck p{margin:1.5mm 0 0}.nr p{margin:1mm 0}
 .nr .bal{background:#000;-webkit-print-color-adjust:exact;print-color-adjust:exact}.nr .stat{break-inside:avoid}}
</style>"""
JS = r"""<script>
(function(){
var C=%%CFG%%, $=function(i){return document.getElementById(i)}, S=[], offen=!C.fest;
var NAME6=["sehr gut","gut","befriedigend","ausreichend","mangelhaft","ungenügend"];
function stufen(){var a=[];if(C.skala==15){for(var i=15;i>=0;i--)a.push(i)}else{for(var j=1;j<=6;j++)a.push(j)}return a}
function zahl(v){if(v==null)return NaN;v=String(v).trim().replace(",",".");if(v===""||!/^\d+(\.\d+)?$/.test(v))return NaN;return parseFloat(v)}
function f(x){return (Math.round(x*100)/100).toString().replace(".",",")}
function schritt(){return $("halb").checked?0.5:1}
function grenzen(){ // Mindestpunkte je Stufe
 var max=zahl($("max").value), st=schritt(), g=[], ok=true, vor=101, ins=document.querySelectorAll("#sk input");
 for(var i=0;i<ins.length;i++){var p=zahl(ins[i].value);var bad=isNaN(p)||p>100||p>=vor&&i>0;if(i==ins.length-1){p=0;bad=false}
  ins[i].classList.toggle("falsch",bad);if(bad)ok=false;vor=p;
  g.push(isNaN(max)||isNaN(p)?NaN:Math.ceil(p/100*max/st-1e-9)*st)}
 return {g:g,ok:ok,max:max}}
function note(p,G){var s=stufen();for(var i=0;i<G.g.length;i++){if(p>=G.g[i]-1e-9)return s[i]}return s[s.length-1]}
function schluessel(){
 var s=stufen(),h="<tr><th>"+(C.skala==15?"Notenpunkte":"Note")+"</th><th>ab Prozent</th><th>Punkte</th></tr>";
 for(var i=0;i<s.length;i++){var letzte=i==s.length-1;
  h+="<tr><td><b>"+s[i]+"</b>"+(C.skala==6?" <span class='klein'>"+NAME6[i]+"</span>":"")+"</td><td><input type='text' inputmode='decimal' aria-label='ab Prozent für "+s[i]+"' value='"+String(C.grenzen[i]).replace(".",",")+"'"+((letzte||!offen)?" readonly":"")+"></td><td class='z' id='pb"+i+"'></td></tr>"}
 $("sk").innerHTML=h;var ins=document.querySelectorAll("#sk input");
 for(var k=0;k<ins.length;k++)ins[k].addEventListener("input",(function(k){return function(){C.grenzen[k]=this.value;rechne()}})(k))}
function liste(){
 var n=Math.max(1,Math.min(60,parseInt($("anz").value,10)||0));while(S.length<n)S.push({n:"",p:""});S.length=n;
 var je=n>14?Math.ceil(n/2):n,h="";
 for(var t=0;t<n;t+=je){h+="<table><tr><th style='width:2.4rem'>Nr.</th><th>Name <span class='klein nd'>(freiwillig)</span></th><th style='width:4.6rem'>Punkte</th><th style='width:3.4rem'>%</th><th style='width:3.6rem'>"+(C.skala==15?"NP":"Note")+"</th></tr>";
  for(var i=t;i<Math.min(n,t+je);i++)h+="<tr><td>"+(i+1)+"</td><td><input type='text' data-i='"+i+"' data-k='n' autocomplete='off' aria-label='Name "+(i+1)+"'></td><td><input type='text' inputmode='decimal' data-i='"+i+"' data-k='p' autocomplete='off' aria-label='Punkte "+(i+1)+"'></td><td class='z' id='pz"+i+"'></td><td class='z' id='nt"+i+"'></td></tr>";
  h+="</table>"}
 $("liste").innerHTML=h;var ins=document.querySelectorAll("#liste input");
 for(var k=0;k<ins.length;k++){var e=ins[k];e.value=S[+e.dataset.i][e.dataset.k];e.addEventListener("input",function(){S[+this.dataset.i][this.dataset.k]=this.value;rechne()})}}
function rechne(){
 var G=grenzen(),s=stufen(),max=G.max,gut=G.ok&&!isNaN(max)&&max>0;
 $("max").classList.toggle("falsch",isNaN(max)||max<=0);
 $("skwarn").textContent=G.ok?"":"Die Prozentwerte müssen von oben nach unten kleiner werden und dürfen höchstens 100 sein.";
 for(var i=0;i<s.length;i++){var o=i==0?max:G.g[i-1]-schritt();$("pb"+i).textContent=!gut?"":(G.g[i]>o+1e-9?"–":(f(G.g[i])+" bis "+f(o)))}
 var z={},sum=0,cnt=0;for(var a=0;a<s.length;a++)z[s[a]]=0;
 for(var j=0;j<S.length;j++){var p=zahl(S[j].p),el=document.querySelector("#liste input[data-i='"+j+"'][data-k='p']"),leer=String(S[j].p).trim()==="";
  var bad=!leer&&(isNaN(p)||!gut||p>max+1e-9||Math.abs(p/schritt()-Math.round(p/schritt()))>1e-9);if(el)el.classList.toggle("falsch",bad);
  if(leer||bad||!gut){$("pz"+j).textContent="";$("nt"+j).textContent="";continue}
  var nt=note(p,G);$("pz"+j).textContent=f(Math.round(p/max*1000)/10);$("nt"+j).textContent=nt;z[nt]++;sum+=nt;cnt++}
 var h="<tr><th>"+(C.skala==15?"Notenpunkte":"Note")+"</th><th style='width:4rem'>Anzahl</th><th>Verteilung</th></tr>",mx=1;for(var q in z)mx=Math.max(mx,z[q]);
 for(var b=0;b<s.length;b++)h+="<tr><td><b>"+s[b]+"</b></td><td class='z'>"+z[s[b]]+"</td><td>"+(z[s[b]]?"<span class='bal' style='width:"+Math.round(z[s[b]]/mx*100)*0.9+"%'></span>":"")+"</td></tr>";
 $("vert").innerHTML=h;
 $("schnitt").textContent=cnt?f(sum/cnt):"–";$("gew").textContent=cnt+" von "+S.length;
 var unter=0;for(var c=0;c<s.length;c++){if(C.skala==15?s[c]<=3:s[c]>=5)unter+=z[s[c]]}
 $("unter").textContent=cnt?(unter+" ("+f(Math.round(unter/cnt*1000)/10)+" %)"):"–";
 $("dtitel").textContent=$("titel").value||"Leistungsnachweis";$("dklasse").textContent=$("klasse").value||"____";
 $("dfach").textContent=$("fach").value||"____";$("ddatum").textContent=$("datum").value?$("datum").value.split("-").reverse().join("."):"__________";$("dmax").textContent=isNaN(max)?"____":f(max)}
function start(){
 var m=/[#&]p=([\d.,;]+)/.exec(location.hash),kl=/[#&]kl=([^&]+)/.exec(location.hash),fa=/[#&]f=([^&]+)/.exec(location.hash);
 if(kl)$("klasse").value=decodeURIComponent(kl[1]).slice(0,12);if(fa)$("fach").value=decodeURIComponent(fa[1]).slice(0,40);
 if(m){var w=m[1].split(/[,;]/).filter(function(x){return /^\d+$/.test(x)}).slice(0,4);if(w.length){$("max").value=w[0];
  if(w.length>1){var h="Punktzahl aus Ihrem Material: ";w.forEach(function(x){h+="<button type='button' class='knopf h' data-p='"+x+"'>"+x+" Punkte</button>"});$("schnell").innerHTML=h;
   $("schnell").addEventListener("click",function(e){var d=e.target.getAttribute("data-p");if(d){$("max").value=d;rechne()}})}}}
 schluessel();liste();rechne();
 ["max","halb","titel","klasse","fach","datum"].forEach(function(i){$(i).addEventListener("input",rechne)});
 $("anz").addEventListener("input",function(){liste();rechne()});
 $("druck").addEventListener("click",function(){window.print()});
 $("leer").addEventListener("click",function(){if(confirm("Alle Namen und Punkte löschen?")){S=[];liste();rechne()}});
 var an=$("anpassen");if(an)an.addEventListener("click",function(){offen=true;schluessel();rechne();an.style.display="none";$("festinfo").textContent="Sie rechnen jetzt mit einem eigenen Schlüssel."});
 window.addEventListener("beforeunload",function(e){for(var i=0;i<S.length;i++){if(S[i].p||S[i].n){e.preventDefault();e.returnValue="";return}}})}
start()})();
</script>"""


def seite(g, s):
    url = f'{g["SITE"]}/{s["datei"]}'
    c = s["cfg"]
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": s["h1"], "url": url, "applicationCategory": "EducationalApplication",
           "operatingSystem": "Browser", "inLanguage": "de", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    out = g["head"](s["titel"], s["desc"], url, "", extra_ld=ld)
    out = out.replace('<link rel="preconnect" href="https://eduki.com">\n', "")   # keine Verbindung zu Dritten auf dieser Seite
    csp = ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data:; connect-src 'none'; form-action 'none'; frame-src 'none'; object-src 'none'\"><meta name=\"referrer\" content=\"no-referrer\">")
    out, n = re.subn(r'(<meta charset="utf-8">)', r"\1" + csp.replace("\\", "\\\\"), out, count=1)
    if n != 1 or "preconnect" in out:
        raise RuntimeError("Notenrechner: Kopf nicht angepasst")
    andere = " · ".join(f'<a href="{x["datei"]}">{E(x["h1"])}</a>' for x in SEITEN if x is not s)
    fest = (f'<p id="festinfo" class="klein nd">{E(c["quelle"])}</p><p class="nd"><button type="button" class="knopf h" id="anpassen">Schlüssel anpassen</button></p>' if c["fest"] else
            '<p class="klein nd">Die Werte sind nur ein Beispiel. Den Notenschlüssel legt Ihre Schule oder Fachschaft fest. Tragen Sie ein, ab wie viel Prozent es welche Note gibt.</p>')
    wort = "Notenpunkte" if c["skala"] == 15 else "Note"
    unter = "0 bis 3 Notenpunkte" if c["skala"] == 15 else "Note 5 oder 6"
    out += (f'<main class="article-wrap nr{" np15" if c["skala"] == 15 else ""}">{CSS}'
            f'<h1 class="nd">{E(s["h1"])}</h1><p class="nd">{E(s["intro"])}</p>'
            '<div class="ds nd"><strong>Datenschutz: Ihre Eingaben verlassen Ihr Gerät nicht.</strong> Der Rechner arbeitet nur in Ihrem Browser. Es wird nichts an einen Server übertragen und nichts gespeichert, '
            'auch kein Cookie. Wenn Sie die Seite schließen oder neu laden, sind alle Eingaben gelöscht. Namen sind freiwillig. Die laufende Nummer aus Ihrer Klassenliste genügt. '
            f'<a href="datenschutz.html">Mehr zum Datenschutz</a></div>'
            '<div class="kopfdruck"><h1><span id="dtitel"></span></h1><p>Klasse: <b id="dklasse"></b> &nbsp;·&nbsp; Fach: <b id="dfach"></b> &nbsp;·&nbsp; Datum: <b id="ddatum"></b> &nbsp;·&nbsp; Gesamtpunktzahl: <b id="dmax"></b></p></div>'
            '<div class="karte nd"><h2 style="margin-top:0">1. Angaben zum Leistungsnachweis</h2><div class="feld">'
            '<div><label for="titel">Titel</label><input type="text" id="titel" maxlength="80" autocomplete="off" placeholder="z. B. Probearbeit Zahlen bis 100"></div>'
            '<div><label for="klasse">Klasse</label><input type="text" id="klasse" maxlength="12" autocomplete="off" placeholder="z. B. 2a"></div>'
            '<div><label for="fach">Fach</label><input type="text" id="fach" maxlength="40" autocomplete="off"></div>'
            '<div><label for="datum">Datum</label><input type="date" id="datum"></div>'
            '<div><label for="max">Gesamtpunktzahl</label><input type="text" inputmode="decimal" id="max" value="30" autocomplete="off"></div>'
            '<div><label for="anz">Anzahl der Schüler</label><input type="number" id="anz" min="1" max="60" value="35"></div>'
            '</div><p id="schnell" class="klein"></p><p><label style="font-weight:400"><input type="checkbox" id="halb" checked> halbe Punkte zulassen</label></p></div>'
            '<div class="zwei"><div class="karte"><h2 style="margin-top:0"><span class="nd">2. </span>Notenschlüssel</h2>' + fest +
            f'<table class="sk{" sk15" if c["skala"] == 15 else ""}" id="sk"></table><p id="skwarn" class="warn nd"></p></div>'
            f'<div class="karte stat"><h2 style="margin-top:0"><span class="nd">4. </span>Auswertung</h2><p>Durchschnitt ({wort}): <span class="mw" id="schnitt">–</span></p>'
            f'<p>Gewertet: <b id="gew"></b> &nbsp;·&nbsp; {unter}: <b id="unter"></b></p><table id="vert"{' class="sk15"' if c["skala"] == 15 else ""}></table></div></div>'
            f'<div class="karte"><h2 style="margin-top:0"><span class="nd">3. </span>Punkte und {wort}</h2><p class="klein nd">Tragen Sie die erreichten Punkte ein. Rot markierte Felder werden nicht gewertet (mehr Punkte als möglich oder keine Zahl).</p>'
            '<div class="zwei" id="liste"></div></div>'
            '<div class="fussdruck"><p style="margin-top:6mm">Datum, Unterschrift: ______________________________________</p><p class="klein">Erstellt mit dem Notenrechner von Snice Unterricht · snice-unterricht.eu/noten</p></div>'
            '<p class="nd"><button type="button" class="knopf" id="druck">Übersichtsblatt drucken</button><button type="button" class="knopf h" id="leer">Alles löschen</button></p>'
            '<p class="klein nd">Tipp: Im Druckdialog können Sie statt eines Druckers auch „Als PDF speichern“ wählen. Die Datei liegt dann nur auf Ihrem Gerät.</p>'
            f'<h2 class="nd">Weitere Notenrechner</h2><p class="nd">{andere}</p>'
            '<h2 class="nd">So rechnet die Seite</h2><p class="nd">Aus dem Prozentwert und der Gesamtpunktzahl ergibt sich die Mindestpunktzahl jeder Stufe. Sie wird auf den nächsten halben oder ganzen Punkt aufgerundet. '
            'Beispiel: 30 Punkte, Note 2 ab 81 %. 81 % von 30 sind 24,3 Punkte, also gibt es die Note 2 ab 24,5 Punkten. Der Durchschnitt ist der Mittelwert aller gewerteten Ergebnisse.</p>'
            '<p class="nd">Passende Leistungsnachweise mit Musterlösung und Punkteraster finden Sie bei den <a href="materialien.html">Materialien</a>.</p>'
            + JS.replace("%%CFG%%", json.dumps(c, ensure_ascii=False)) + "</main>") + g["foot"]()
    open(os.path.join(g["OUT"], s["datei"]), "w", encoding="utf-8").write(out)
    return url


def render(g):
    urls = [seite(g, s) for s in SEITEN]
    if isinstance(g.get("EXTRA_URLS"), list):
        g["EXTRA_URLS"].extend(u for u in urls if u not in g["EXTRA_URLS"])
    return len(urls)


if __name__ == "__main__":
    sys.path.insert(0, H)
    import build as B
    B.FOOT_COLS = B.build_foot_cols()
    print("Notenrechner-Seiten geschrieben:", render(vars(B)))
