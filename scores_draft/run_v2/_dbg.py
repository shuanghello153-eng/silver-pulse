import json
db=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
SIG=["信号"];INFO=["信息","资料","披露","数据","透明度","公开"];DIFF=["差异","独特","打法","模式","定位","反常识","壁垒","亮点"];COPY=["复制","借鉴","可学","照搬","落地","国内","抄"]
n_len=0;n_dim=0;n_empty=0;n_other=0
samples=[]
for e in db:
    r=e.get("recommend")
    if not isinstance(r,str) or not r.strip():
        n_empty+=1; 
        if len(samples)<3: samples.append(("EMPTY",e["serial"],repr(r)))
        continue
    L=len(r)
    if L<30 or L>200:
        n_len+=1
        if len([s for s in samples if s[0]=="LEN"])<5: samples.append(("LEN",e["serial"],L,r))
        continue
    has=[("信",any(w in r for w in SIG)),("息",any(w in r for w in INFO)),("差",any(w in r for w in DIFF)),("复",any(w in r for w in COPY))]
    miss=[nm for nm,ok in has if not ok]
    if miss:
        n_dim+=1
        if len([s for s in samples if s[0]=="DIM"])<8: samples.append(("DIM",e["serial"],miss,r))
print("L4失败分类: 空=",n_empty,"长度=",n_len,"缺维度=",n_dim)
for s in samples: print(s)
