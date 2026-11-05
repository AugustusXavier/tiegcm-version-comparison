import re,sys,json,difflib
zh=open(sys.argv[1],encoding='utf-8').read(); en=open(sys.argv[2],encoding='utf-8').read()
pat=re.compile(r"""'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*"|>[^<>]+<""")
def split(s):
    toks=[]; pieces=[]; last=0
    for m in pat.finditer(s): pieces.append(s[last:m.start()]); toks.append(m.group(0)); last=m.end()
    return toks,pieces
tz,pz=split(zh); te,pe=split(en)
sm=difflib.SequenceMatcher(None,pe,pz,autojunk=False); m={}; conf={}
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal':
        for k in range(i2-i1):
            a,b=te[i1+k],tz[j1+k]
            if a in m and m[a]!=b: conf.setdefault(a,set()).update([m[a],b])
            elif a not in m: m[a]=b
    else: print('unaligned',tag,te[i1:i2][:3],tz[j1:j2][:3])
# drop ambiguous ones (same English used for two different Chinese strings)
for a in conf: m.pop(a,None)
m={a:b for a,b in m.items() if a!=b}
print('mapped',len(m),'ambiguous dropped',len(conf),[a[:30] for a in conf][:10])
json.dump(m,open('en2zh.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
