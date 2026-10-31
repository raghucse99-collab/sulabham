/* Sulabham study tracker (saved only on this phone).
   sul_err : every question answered wrong  {id:{p:your pick,d:first date,l:last wrong date,n:times wrong,f:date fixed or 0}}
   sul_log : what was studied each day      {"YYYY-MM-DD":{r:{ref:{t:title,u:link,at:"HH:MM"}},q:{id:[pick,ok]}}}  (last 40 days)
   Pages call SUL_track.ans(id,pick,ok) when a question is answered.
   Any element with data-rd="<ref>" (and optional data-rt title, data-ru link) is logged as "read"
   after it has been on screen (and open, for <details>) for about 8 seconds. */
(function(){
  if(window.SUL_track)return;
  function pad(n){return(n<10?"0":"")+n}
  function day(x){x=x||new Date();return x.getFullYear()+"-"+pad(x.getMonth()+1)+"-"+pad(x.getDate())}
  function hm(){var x=new Date();return pad(x.getHours())+":"+pad(x.getMinutes())}
  function get(k){try{return JSON.parse(localStorage.getItem(k)||"{}")||{}}catch(e){return{}}}
  function put(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
  function logDay(G,d){if(!G[d])G[d]={r:{},q:{}};var ks=Object.keys(G).sort();while(ks.length>40)delete G[ks.shift()];return G[d]}
  function ans(id,pick,ok){if(!id)return;var d=day(),E=get("sul_err"),e=E[id];
    if(!ok){E[id]={p:pick,d:e?e.d:d,l:d,n:((e&&e.n)||0)+1,f:0}}else if(e&&!e.f){e.f=d}
    put("sul_err",E);var G=get("sul_log");logDay(G,d).q[id]=[pick,ok?1:0];put("sul_log",G)}
  function read(ref,title,url){if(!ref)return;var G=get("sul_log"),L=logDay(G,day());if(L.r[ref])return;
    L.r[ref]={t:title||"",u:url||"",at:hm()};put("sul_log",G)}
  var seen={};
  function vis(el){var r=el.getBoundingClientRect(),h=window.innerHeight||800;if(!r.height)return false;
    var v=Math.min(r.bottom,h)-Math.max(r.top,0);return v>=Math.min(220,r.height*0.5)}
  function tick(){if(document.hidden)return;var els=document.querySelectorAll("[data-rd]");
    for(var i=0;i<els.length;i++){var el=els[i],ref=el.getAttribute("data-rd");if(seen[ref]===-1)continue;
      if(el.tagName==="DETAILS"&&!el.open)continue;if(!vis(el))continue;
      seen[ref]=(seen[ref]||0)+1;if(seen[ref]>=8){seen[ref]=-1;read(ref,el.getAttribute("data-rt")||"",el.getAttribute("data-ru")||location.pathname.split("/").pop()+location.search+(el.id?"#"+el.id:""))}}}
  setInterval(tick,1000);
  window.SUL_track={ans:ans,read:read,day:day,get:get,put:put};
})();
