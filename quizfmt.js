/* Sulabham question layout.
   SUL_q.stem(q, L, esc) -> HTML for the question text plus its statements / lists.
   Match-the-following questions (List-I "A. … B. …" and List-II "1. … 2. …", either as two
   statement lines or written inside the question text) are shown as a clear two-column table.
   Other statements are shown one per line. */
(function(){
  if(window.SUL_q)return;
  var css=".qmt{width:100%!important;max-width:100%;align-self:stretch;display:table;border-collapse:collapse;margin:8px 0 4px;font-size:.92rem;table-layout:fixed}"+
    ".qmt th{background:var(--ink,#16324a);color:var(--paper,#fff);text-align:left;padding:6px 8px;font-size:.82rem}"+
    ".qmt td{border:1px solid var(--line,#d6dfe5);padding:6px 8px;vertical-align:top;overflow-wrap:anywhere}"+
    ".qmt td b{display:inline-block;min-width:1.6em;color:var(--accent,#c0392b)}"+
    ".qmt tr:nth-child(even) td{background:rgba(127,140,150,.08)}"+
    ".qfig{margin:8px 0}.qfig svg{max-width:100%;height:auto}.qst{margin:8px 0 4px;padding:0;list-style:none}.qst li{margin:4px 0;padding:6px 10px;border-left:3px solid var(--line,#d6dfe5);background:rgba(127,140,150,.07);border-radius:0 8px 8px 0}";
  var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
  var LET=["A","B","C","D","E","F"],NUM=["1","2","3","4","5","6"];
  /* split "A. x  B. y  C. z" in order; returns [[label,text],…] or null */
  function split(s,labs){s=String(s||"").trim();var out=[],pos=[],from=0;
    for(var i=0;i<labs.length;i++){var re=new RegExp((i?"(?:^|[\\s;,.])":"^")+"\\(?"+labs[i]+"[.)]\\s+","g");re.lastIndex=from;var m=re.exec(s);
      if(!m||(i===0&&m.index!==0))break;var st=m.index+(m[0].match(/^[\s;,.]/)?1:0);pos.push([labs[i],st,m.index+m[0].length]);from=m.index+m[0].length}
    if(pos.length<2)return null;
    for(var j=0;j<pos.length;j++){var end=j+1<pos.length?pos[j+1][1]:s.length;out.push([pos[j][0],s.slice(pos[j][2],end).replace(/[\s;,]+$/,"").trim()])}
    return out}
  var HEAD={en:["List-I","List-II"],te:["జాబితా-I","జాబితా-II"]};
  function lang(){return document.documentElement.lang==="te"?"te":"en"}
  function table(a,b,esc,h){var n=Math.max(a.length,b.length),r='<table class="qmt"><tr><th>'+esc(h[0])+'</th><th>'+esc(h[1])+'</th></tr>';
    for(var i=0;i<n;i++)r+='<tr><td>'+(a[i]?'<b>'+a[i][0]+'.</b> '+esc(a[i][1]):'')+'</td><td>'+(b[i]?'<b>'+b[i][0]+'.</b> '+esc(b[i][1]):'')+'</td></tr>';
    return r+'</table>'}
  /* finds a list header like "List-I (news)" inside the question to use as column titles */
  function heads(qt){var h=HEAD[lang()].slice(),m=qt.match(/(List[- ]?I|జాబితా[- ]?I)\s*(\([^)]*\))/),k=qt.match(/(List[- ]?II|జాబితా[- ]?II)\s*(\([^)]*\))/);
    if(m)h[0]+=" "+m[2];if(k)h[1]+=" "+k[2];return h}
  function stem0(q,L,esc,cls){var qt=L(q.q)||"",sts=(q.st||[]).map(function(x){return L(x)||""});
    /* case 1: lists written inside the question text */
    var m=qt.match(/^([\s\S]*?)(?:List[- ]?I|జాబితా[- ]?I)\s*:\s*([\s\S]*?)\s*(?:List[- ]?II|జాబితా[- ]?II)\s*:\s*([\s\S]*)$/);
    if(m&&!sts.length){var a=split(m[2],LET),b=split(m[3],NUM);
      if(a&&b)return'<p class="'+(cls||"qt")+'">'+esc(m[1].replace(/[.\s]+$/,"").trim()||qt)+'</p>'+table(a,b,esc,HEAD[lang()])}
    /* case 2: two statement lines, one lettered and one numbered */
    if(sts.length>=2){var li=-1,ni=-1;sts.forEach(function(s,i){if(li<0&&split(s,LET))li=i;else if(ni<0&&split(s,NUM))ni=i});
      if(li>=0&&ni>=0){var rest=sts.filter(function(_,i){return i!==li&&i!==ni});
        return'<p class="'+(cls||"qt")+'">'+esc(qt)+'</p>'+table(split(sts[li],LET),split(sts[ni],NUM),esc,heads(qt))+
          (rest.length?'<ul class="qst">'+rest.map(function(s){return"<li>"+esc(s)+"</li>"}).join("")+'</ul>':'')}}
    var lab=sts.some(function(s){return/^\s*(\(?([IVX]+|\d+|[A-F])[.)]\s|Assertion|Reason|నిశ్చితం|కారణం)/.test(s)});
    return'<p class="'+(cls||"qt")+'">'+esc(qt)+'</p>'+(sts.length?'<ul class="qst">'+sts.map(function(s,i){return"<li>"+(lab?"":"<b>"+(i+1)+".</b> ")+esc(s)+"</li>"}).join("")+'</ul>':'')}
  /* q.fig: trusted inline SVG from Sulabham's own files (figures, charts) */
  function stem(q,L,esc,cls){return stem0(q,L,esc,cls)+(q.fig?'<div class="qfig">'+q.fig+'</div>':'')}
  function isMatch(q,L){return stem(q,L,String).indexOf('class="qmt"')>=0}
  window.SUL_q={stem:stem,split:split,isMatch:isMatch};
})();
