/* Sulabham personal (one-device) unlock codes.
   Every phone gets a device number (saved once in this browser). The owner turns
   (course master code + device number) into a personal code with the private code maker.
   This page turns (personal code + this device number) back into the master code.
   A personal code typed on another phone gives a wrong master code, so unlocking fails.
   Plain master codes are accepted only until CUTOFF (for buyers who already have them). */
(function(){
  if(window.SUL_dev)return;
  var CUTOFF="2026-11-30",A="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",DA="23456789ABCDEFGHJKMNPQRSTUVWXYZ";
  function norm(c){return String(c||"").toUpperCase().replace(/[^A-Z0-9]/g,"")}
  function id(){var d=null;try{d=localStorage.getItem("sul_dev")}catch(e){}
    if(!d||!/^[2-9A-HJKMNP-Z]{6}$/.test(d)){var r=new Uint8Array(6);crypto.getRandomValues(r);d="";for(var i=0;i<6;i++)d+=DA[r[i]%DA.length];try{localStorage.setItem("sul_dev",d)}catch(e){}}
    return d}
  function pad(n){return(n<10?"0":"")+n}
  function today(){var t=new Date();return t.getFullYear()+"-"+pad(t.getMonth()+1)+"-"+pad(t.getDate())}
  function mask(prod,dev){return crypto.subtle.digest("SHA-256",new TextEncoder().encode(prod+"|"+norm(dev).replace(/^D(?=[2-9A-Z]{6}$)/,"")+"|sulabham-v1")).then(function(h){return new Uint8Array(h)})}
  function check(s){var t=0;for(var i=0;i<s.length;i++)t+=A.indexOf(s[i])*(i+1);return A[t%36]}
  /* personal code -> master code (Promise). Returns "" when it cannot be a valid code here. */
  function resolve(typed,prod){var p=norm(typed);
    if(p.length===10&&check(p.slice(0,-1))===p.slice(-1)){var body=p.slice(0,-1);
      return mask(prod,id()).then(function(k){var m="";for(var i=0;i<body.length;i++)m+=A[(A.indexOf(body[i])-k[i]%36+36)%36];return m})}
    return Promise.resolve(today()<=CUTOFF?p:"")}
  /* master + device -> personal code (used by the owner's code maker) */
  function make(master,prod,dev){var m=norm(master);
    return mask(prod,dev).then(function(k){var b="";for(var i=0;i<m.length;i++)b+=A[(A.indexOf(m[i])+k[i]%36)%36];var c=b+check(b);return c.replace(/(.{5})(?=.)/g,"$1-")})}
  window.SUL_dev={id:id,resolve:resolve,make:make,cutoff:CUTOFF};
  /* show the device number next to every unlock box */
  function show(){var f=document.getElementById("codeForm");if(!f||document.getElementById("devNo"))return;
    var te=document.documentElement.lang==="te",p=document.createElement("p");p.id="devNo";
    p.style.cssText="margin:8px 0 0;font-size:.85rem;background:var(--pasupu-soft,#fff3cf);border:1px dashed var(--pasupu,#e3a400);border-radius:10px;padding:7px 10px";
    p.innerHTML=(te?"మీ పరికరం నంబర్: ":"Your device number: ")+'<b style="font-family:monospace;font-size:1.05rem;letter-spacing:.08em">D-'+id()+'</b><br><small>'+(te?"చెల్లింపు స్క్రీన్‌షాట్‌తో పాటు ఈ నంబర్ పంపండి. మీ కోడ్ ఈ ఫోన్‌లో మాత్రమే పనిచేస్తుంది.":"Send this number with your payment screenshot. Your code will work on this phone only.")+'</small>';
    f.parentNode.insertBefore(p,f)}
  function tick(){show();var p=document.getElementById("devNo"),te=document.documentElement.lang==="te";if(p&&p.getAttribute("data-l")!==String(te)){p.remove();show();var q=document.getElementById("devNo");if(q)q.setAttribute("data-l",String(te))}}
  if(document.readyState!=="loading")tick();else document.addEventListener("DOMContentLoaded",tick);
  new MutationObserver(function(){tick()}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["lang"]});
})();
