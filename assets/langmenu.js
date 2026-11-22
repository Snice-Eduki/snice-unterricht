/* Sprachmenue (20.11.2026): Flagge + Eigenname, ausklappbar. Erzeugt von laender_seiten.py - nicht von Hand aendern. Kein Tracking, keine Fremdanfragen. */
(function(){
var L=[{"c": "de", "d": "", "l": "de", "n": "Deutsch"}, {"c": "en", "d": "en", "l": "en", "n": "English"}, {"c": "es", "d": "es", "l": "es", "n": "Español"}, {"c": "fr", "d": "fr", "l": "fr", "n": "Français"}, {"c": "it", "d": "it", "l": "it", "n": "Italiano"}],d=document;if(!d.getElementById('topnav')||d.getElementById('langmenu'))return;
var seg=(location.pathname.split('/')[1]||'').toLowerCase(),cur=L[0];
L.forEach(function(x){if(x.d&&x.d===seg)cur=x});
var F='system-ui,-apple-system,"Segoe UI","Noto Sans","Noto Sans CJK JP","Noto Sans CJK KR","Noto Sans CJK SC","Noto Sans Thai","Noto Sans Devanagari","Nirmala UI","Leelawadee UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI",sans-serif';
var st=d.createElement('style');st.textContent='#topnav .links{min-width:0;overflow-x:auto;scrollbar-width:none}#langmenu{flex:none;position:relative;margin-left:.6rem;font:inherit}#langmenu .lmb{display:flex;align-items:center;gap:.45rem;font:inherit;font-family:'+F+';font-weight:600;padding:.3rem .65rem;border:1.5px solid currentColor;border-radius:999px;background:transparent;color:inherit;cursor:pointer;white-space:nowrap}'
+'#langmenu img{width:24px;height:16px;border-radius:2px;vertical-align:middle}#langmenu .lmb:after{content:"\\25BE"}#langmenu .lml{display:none;position:absolute;right:0;top:calc(100% + 6px);z-index:1000;background:#fff;color:#111;border:1px solid #c8c8d0;border-radius:14px;box-shadow:0 10px 30px #0003;padding:.5rem;width:min(34rem,92vw);max-height:70vh;overflow:auto;grid-template-columns:repeat(auto-fill,minmax(10.5rem,1fr));gap:.1rem}'
+'#langmenu.open .lml{display:grid}#langmenu .lml a{display:flex;align-items:center;gap:.5rem;padding:.4rem .55rem;border-radius:8px;color:#111;text-decoration:none;font-weight:500;font-family:'+F+'}'
+'#langmenu .lml a:hover,#langmenu .lml a:focus{background:#eef}#langmenu .lml a[aria-current]{font-weight:800;background:#f1f1f6}@media(max-width:640px){#langmenu{margin-left:auto}#langmenu .lml{position:fixed;left:8px;right:8px;top:64px;width:auto}}';
d.head.appendChild(st);
var al=d.querySelector('#topnav .links a[href$="material-in-anderen-sprachen.html"]');if(al)al.parentNode.removeChild(al);
var w=d.createElement('div');w.id='langmenu';
var b=d.createElement('button');b.type='button';b.className='lmb';b.setAttribute('aria-haspopup','true');b.setAttribute('aria-expanded','false');
b.innerHTML='<img src="/assets/flags/'+cur.c+'.svg" alt="" width="24" height="16"><span lang="'+cur.l+'">'+cur.n+'</span>';
var m=d.createElement('div');m.className='lml';m.setAttribute('role','menu');
L.forEach(function(x){var a=d.createElement('a');a.href='/'+(x.d?x.d+'/':'');a.setAttribute('hreflang',x.l);a.lang=x.l;a.setAttribute('role','menuitem');if(x===cur)a.setAttribute('aria-current','true');
a.innerHTML='<img src="/assets/flags/'+x.c+'.svg" alt="" width="24" height="16" loading="lazy"><span>'+x.n+'</span>';m.appendChild(a)});
w.appendChild(b);w.appendChild(m);
var old=d.querySelector('#topnav .langsw');if(old)old.parentNode.replaceChild(w,old);else d.getElementById('topnav').appendChild(w);
function zu(){w.classList.remove('open');b.setAttribute('aria-expanded','false')}
b.addEventListener('click',function(e){e.stopPropagation();var o=w.classList.toggle('open');b.setAttribute('aria-expanded',o)});
d.addEventListener('click',function(e){if(!w.contains(e.target))zu()});d.addEventListener('keydown',function(e){if(e.key==='Escape'){zu();b.focus()}});
})();
