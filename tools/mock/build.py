import importlib,collections,sys,json,os
sys.path.insert(0,'.')
from mk import C,AR
mid=sys.argv[1];pre=sys.argv[2];date=sys.argv[3];n=int(sys.argv[4])
FIX=set(e for e,t in C.values())|set(e for e,t in AR)|{"Only I is implicit","Only argument I is strong","Only conclusion I follows","Only course of action I follows"}
SECS=[("his","Indian History","భారతదేశ చరిత్ర"),("geo","Geography","భూగోళశాస్త్రం"),("soc","Indian Society","భారతీయ సమాజం"),("ca","Current Affairs","కరెంట్ అఫైర్స్"),("men","Mental Ability","మెంటల్ ఎబిలిటీ")]
qs=[]
for s,_,_ in SECS:
    M=importlib.import_module(pre+'_'+s);assert len(M.Q)==30,(s,len(M.Q))
    for q in M.Q:q=dict(q);q["s"]=s;qs.append(q)
cnt=collections.Counter(q["a"] for q in qs);tgt=len(qs)/4
for q in qs:
    if q["o"][0]["en"] in FIX:continue
    a=q["a"];low=min(range(4),key=lambda k:cnt[k])
    if cnt[a]>tgt and cnt[low]<tgt:
        q["o"][a],q["o"][low]=q["o"][low],q["o"][a];cnt[a]-=1;cnt[low]+=1;q["a"]=low
print(dict(sorted(cnt.items())))
for q in qs:
    assert len(q["o"])==4 and len({o["en"] for o in q["o"]})==4,q["q"]["en"]
    for k in ("en","te"):assert q["q"][k] and q["why"][k]
out={"id":mid,"n":n,"date":date,"title":{"en":"Group 2 Prelims Mock Test %d"%n,"te":"గ్రూప్ 2 ప్రిలిమ్స్ మాక్ టెస్ట్ %d"%n},
 "mins":150,"neg":1/3,"secs":[{"id":s,"t":{"en":e,"te":t},"n":30} for s,e,t in SECS],"qs":qs}
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..');os.makedirs(os.path.join(ROOT,'mocks'),exist_ok=True)
json.dump(out,open(os.path.join(ROOT,'mocks','%s.json'%mid),'w'),ensure_ascii=False,separators=(',',':'))
ip=os.path.join(ROOT,'mocks','index.json');ix=json.load(open(ip)) if os.path.exists(ip) else []
ix=[x for x in ix if x["id"]!=mid]+[{"id":mid,"n":n,"date":date,"title":out["title"],"q":len(qs)}];ix.sort(key=lambda x:-x["n"])
json.dump(ix,open(ip,'w'),ensure_ascii=False,indent=1);print('written',len(qs))
