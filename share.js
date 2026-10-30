/* Sulabham share buttons.
   Any element with [data-share] becomes a share button.
   Attributes: data-url (relative or absolute; default: this page), data-title-en / data-title-te,
   data-text-en / data-text-te (message; the link is appended), data-img (optional poster to attach on phones).
   On phones uses the native share sheet; otherwise shows WhatsApp / Telegram / Copy link. */
(function(){
  if(window.SUL_share)return;
  var css=".shr-pop{position:absolute;z-index:60;background:#fff;color:#16324a;border:1px solid #d6dfe5;border-radius:14px;box-shadow:0 14px 34px rgba(12,34,56,.25);padding:8px;display:flex;flex-direction:column;gap:4px;min-width:190px;font:600 .92rem 'Noto Sans','Noto Sans Telugu',sans-serif}"+
    ".shr-pop a,.shr-pop button{display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;background:transparent;border:0;border-radius:10px;padding:9px 10px;min-height:42px;cursor:pointer;font:inherit;text-align:left}"+
    ".shr-pop a:hover,.shr-pop button:hover{background:#f1f5f8}.shr-pop i{font-style:normal;width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:.8rem}"+
    ".shr-pop .wa i{background:#25d366}.shr-pop .tg i{background:#229ed9}.shr-pop .cp i{background:#16324a}"+
    "@media (prefers-color-scheme:dark){.shr-pop{background:#16242f;color:#e6eef4;border-color:#29404f}.shr-pop a:hover,.shr-pop button:hover{background:#1f3140}}";
  var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
  var pop=null;
  function te(){return document.documentElement.lang==="te"}
  function abs(u){try{return new URL(u||location.href.split("#")[0],location.href).href}catch(e){return location.href}}
  function close(){if(pop){pop.remove();pop=null}}
  function info(b){var L=te()?"te":"en",url=abs(b.getAttribute("data-url"));
    return{url:url,title:b.getAttribute("data-title-"+L)||b.getAttribute("data-title-en")||document.title,
      text:b.getAttribute("data-text-"+L)||b.getAttribute("data-text-en")||"",img:b.getAttribute("data-img")}}
  function copy(s,btn){function ok(){var o=btn.innerHTML;btn.innerHTML="<i>✓</i>"+(te()?"లింక్ కాపీ అయింది":"Link copied");setTimeout(function(){close()},900)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(s).then(ok,function(){fallback()})}else fallback();
    function fallback(){var t=document.createElement("textarea");t.value=s;document.body.appendChild(t);t.select();try{document.execCommand("copy")}catch(e){}t.remove();ok()}}
  function menu(b,d){close();var msg=(d.text?d.text+"\n":"")+d.url;
    pop=document.createElement("div");pop.className="shr-pop";pop.setAttribute("role","menu");
    pop.innerHTML='<a class="wa" target="_blank" rel="noopener" href="https://wa.me/?text='+encodeURIComponent(msg)+'"><i>W</i>WhatsApp</a>'+
      '<a class="tg" target="_blank" rel="noopener" href="https://t.me/share/url?url='+encodeURIComponent(d.url)+'&text='+encodeURIComponent(d.text||d.title)+'"><i>T</i>Telegram</a>'+
      '<button type="button" class="cp"><i>⧉</i>'+(te()?"లింక్ కాపీ చేయండి":"Copy link")+'</button>';
    document.body.appendChild(pop);
    var r=b.getBoundingClientRect(),w=pop.offsetWidth,x=Math.min(Math.max(8,r.left+window.scrollX),window.scrollX+document.documentElement.clientWidth-w-8);
    pop.style.left=x+"px";pop.style.top=(r.bottom+window.scrollY+6)+"px";
    pop.querySelector(".cp").addEventListener("click",function(e){e.stopPropagation();copy(msg,this)});
    pop.querySelectorAll("a").forEach(function(a){a.addEventListener("click",function(){setTimeout(close,50)})})}
  function share(b){var d=info(b);
    if(navigator.share){
      var go=function(files){var o={title:d.title,text:d.text,url:d.url};if(files)o.files=files;
        navigator.share(o).catch(function(err){if(err&&err.name!=="AbortError")menu(b,d)})};
      if(d.img&&navigator.canShare){fetch(d.img).then(function(r){return r.blob()}).then(function(bl){var f=new File([bl],d.img.split("/").pop(),{type:bl.type||"image/png"});
        if(navigator.canShare({files:[f]}))go([f]);else go()}).catch(function(){go()})}
      else go();return}
    menu(b,d)}
  document.addEventListener("click",function(e){var b=e.target.closest("[data-share]");
    if(b){e.preventDefault();e.stopPropagation();share(b);return}
    if(pop&&!e.target.closest(".shr-pop"))close()});
  document.addEventListener("keydown",function(e){if(e.key==="Escape")close()});
  window.addEventListener("resize",close);
  window.SUL_share=share;
})();
