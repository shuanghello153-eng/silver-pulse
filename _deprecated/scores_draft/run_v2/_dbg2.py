import json
db=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
SIG=["信号"];INFO=["信息","资料","披露","数据","透明度","公开"];DIFF=["差异","独特","打法","模式","定位","反常识","壁垒","亮点"];COPY=["复制","借鉴","可学","照搬","落地","国内","抄"]
for e in db:
    r=e.get("recommend")
    if not isinstance(r,str) or not r.strip(): print("EMPTY",e["serial"]); continue
    L=len(r)
    if L<30 or L>200: print("LEN",e["serial"],L,r); continue
    miss=[nm for nm,ok in [("信",any(w in r for w in SIG)),("息",any(w in r for w in INFO)),("差",any(w in r for w in DIFF)),("复",any(w in r for w in COPY))] if not ok]
    if miss: print("DIM",e["serial"],miss,r)
