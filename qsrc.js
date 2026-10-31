/* Sulabham question + reading resolver: turns saved ids back into full content.
   Question ids: d:DATE:i (Today quiz) · dm:DATE:item (Today practice MCQ) · c:DATE:i (daily CA quiz)
                 w:WEEK:i (weekly test) · v:LESSON:i (Visual Library) · p:TEST:i (Prelims free) · g:MOCK:i (Group 2 mock)
   Reading refs: t:DATE:item (Today page) · c:DATE:item (daily CA) · v:LESSON (Visual Library) · a:… (ASO chapter, title only)
   SUL_qsrc.questions(ids) -> Promise<{id:{q,st,o,a,why,link,lab}}>
   SUL_qsrc.reads(refs)    -> Promise<{ref:{kind,title,line,pts,facts,tip,trap,link}}> */
(function(){
  if(window.SUL_qsrc)return;
  var cache={};
  function getJ(u){if(!cache[u])cache[u]=fetch(u,{cache:"no-cache"}).then(function(r){if(!r.ok)throw 0;return r.json()}).catch(function(){return null});return cache[u]}
  function area(v){var a=(v.split("-")[1]||"pol").toLowerCase();return a}
  function file(p){var k=p[0];
    if(k==="d"||k==="dm"||k==="t")return"days/"+p[1]+".json";if(k==="c")return"cad/"+p[1]+".json";if(k==="w")return"caw/"+p[1]+".json";
    if(k==="v")return"vlib/"+area(p[1])+"/"+p[1]+".json";if(k==="p")return"pk/pack.json";if(k==="g")return"mocks/"+p[1]+".json";return null}
  function lab(en,te){return{en:en,te:te}}
  function q1(id,j){var p=id.split(":"),k=p[0],i=+p[2],q=null,link="",lb=null;if(!j)return null;
    if(k==="d"){q=(j.quiz||[])[i];link="today.html?d="+p[1]+"&tab=quiz";lb=lab("Today quiz · "+p[1],"నేటి క్విజ్ · "+p[1])}
    else if(k==="dm"){var it=(j.items||[]).filter(function(x){return x.id===p[2]})[0];q=it&&it.mcq;link="today.html?d="+p[1]+"#"+p[2];lb=lab("Today page MCQ · "+p[1],"నేటి పేజీ MCQ · "+p[1])}
    else if(k==="c"){q=(j.quiz||[])[i];link="current.html?d="+p[1]+"&q=1";lb=lab("Daily CA quiz · "+p[1],"రోజువారీ CA క్విజ్ · "+p[1])}
    else if(k==="w"){q=(j.test||[])[i];link="current.html?tab=week&w="+p[1];lb=lab("Weekly test · "+p[1],"వారపు టెస్ట్ · "+p[1])}
    else if(k==="v"){q=(j.mcq||[])[i];link="visuals.html?v="+p[1];lb=lab("Visual Library · "+p[1],"విజువల్ లైబ్రరీ · "+p[1])}
    else if(k==="g"){q=(j.qs||[])[i];link="mock.html?m="+p[1];lb=lab("Group 2 mock · "+(j.title&&j.title.en||p[1]),"గ్రూప్ 2 మాక్ · "+(j.title&&j.title.te||p[1]))}
    else if(k==="p"){var r=j.tests&&j.tests[p[1]]&&j.tests[p[1]][i];if(r){var en=[].concat(r.en),te=[].concat(r.te);
        q={q:{en:en[0],te:te[0]},st:en.slice(1).map(function(x,n){return{en:x,te:te[n+1]||x}}),o:r.o.map(function(o){return{en:o[0],te:o[1]}}),a:r.a,why:{en:r.xe,te:r.xt}}}
      link="prelims.html#test="+p[1];lb=lab("Prelims Pack · "+p[1].toUpperCase(),"ప్రిలిమ్స్ ప్యాక్ · "+p[1].toUpperCase())}
    if(!q||!q.o)return null;return{q:q.q,st:q.st,o:q.o,a:q.a,why:q.why,fig:q.fig,link:link,lab:lb}}
  function questions(ids){var out={};return Promise.all(ids.map(function(id){var f=file(id.split(":"));if(!f)return null;
    return getJ(f).then(function(j){var r=q1(id,j);if(r)out[id]=r})})).then(function(){return out})}
  function r1(ref,j,ix){var p=ref.split(":"),k=p[0];if(!j)return null;
    if(k==="t"){var it=(j.items||[]).filter(function(x){return x.id===p[2]})[0];if(!it)return null;
      return{kind:"t",title:it.title,line:it.line,pts:it.easy||[],facts:it.facts||[],tip:it.tip,trap:it.trap,link:"today.html?d="+p[1]+"#"+p[2]}}
    if(k==="c"){var c=(j.items||[]).filter(function(x){return x.id===p[2]})[0];if(!c)return null;
      return{kind:"c",title:c.title,pts:c.pts||[],facts:c.facts||[],tip:c.exam,link:"current.html?d="+p[1]+"#"+p[2]}}
    if(k==="v"){var t=null;(ix&&ix.areas||[]).forEach(function(A){A.subs.forEach(function(S){S.items.forEach(function(it){if(it.id===p[1])t=it.t})})});
      return{kind:"v",title:t||{en:p[1]},line:j.lead,pts:j.explain||[],facts:[],tip:(j.memory||[])[0],trap:(j.apply||[])[0],link:"visuals.html?v="+p[1]}}
    return null}
  function reads(refs){var out={};return getJ("vlib/index.json").then(function(ix){return Promise.all(refs.map(function(ref){var p=ref.split(":"),f=p[0]==="v"?file(["v",p[1]]):(p[0]==="t"||p[0]==="c")?file(p):null;
    if(!f)return null;return getJ(f).then(function(j){var r=r1(ref,j,ix);if(r)out[ref]=r})}))}).then(function(){return out})}
  window.SUL_qsrc={questions:questions,reads:reads,getJ:getJ};
})();
