/* Newsletter-Einblendung: dezent, ohne Cookie/Tracking; Merker nur lokal (localStorage, 14 Tage) */
(function(){
var K="snice_nl_popup",TAGE=14,d=document;
if(d.documentElement.lang!=="de")return;
if(/(^|\/)(newsletter|newsletter-bestaetigt|impressum|datenschutz|geschenk|gutschein-blitz|ig|404)(\.html)?\/?$/.test(location.pathname))return;
if(/[?&](fbclid=|utm_medium=(paid|ad|ads|cpc|ppc))/i.test(location.search))return;
function lies(){try{var t=+localStorage.getItem(K);return t&&Date.now()-t<TAGE*864e5}catch(e){return false}}
function merke(){try{localStorage.setItem(K,String(Date.now()))}catch(e){}}
if(lies())return;
var el=null,zeigt=false,vorher=null;
function root(){var s=d.querySelector('link[rel=stylesheet][href$="assets/style.css"]');var h=s?s.getAttribute("href"):"assets/style.css";return h.replace(/assets\/style\.css$/,"")}
function zu(){if(!el)return;el.hidden=true;zeigt=false;merke();d.removeEventListener("keydown",esc);if(vorher&&vorher.focus){try{vorher.focus({preventScroll:true})}catch(e){}}}
function esc(e){if(e.key==="Escape")zu()}
function zeige(){
if(zeigt||lies())return;zeigt=true;vorher=d.activeElement;
el=d.createElement("div");el.className="nlpop";el.setAttribute("role","dialog");el.setAttribute("aria-labelledby","nlp-h");el.tabIndex=-1;
el.innerHTML='<button type="button" class="nlp-x" aria-label="Schließen">&times;</button><h2 id="nlp-h">Zwei Geschenke für dich</h2><p class="nlp-t">Im Newsletter für Lehrkräfte: dein persönlicher 50-%-Gutschein und ein Wunschmaterial gratis. Alle zwei Wochen eine Idee, die dir Vorbereitungszeit spart.</p><p><a class="nlp-btn" href="'+root()+'newsletter.html">Geschenke ansehen</a></p><span class="nlp-no">Freiwillig – alle Gratis-Materialien bleiben auch ohne Anmeldung frei.</span>';
d.body.appendChild(el);
el.querySelector(".nlp-x").addEventListener("click",zu);
el.querySelector(".nlp-btn").addEventListener("click",merke);
d.addEventListener("keydown",esc);
try{el.focus({preventScroll:true})}catch(e){}
}
setTimeout(zeige,20000);
addEventListener("scroll",function s(){var h=d.documentElement.scrollHeight-innerHeight;if(h>0&&scrollY/h>=.5){removeEventListener("scroll",s);zeige()}},{passive:true});
if(matchMedia("(hover:hover) and (pointer:fine)").matches){var t0=Date.now();d.addEventListener("mouseout",function(e){if(!e.relatedTarget&&e.clientY<=0&&Date.now()-t0>8000)zeige()})}
})();
