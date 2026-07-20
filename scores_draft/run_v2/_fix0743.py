import json
fp="scores_draft/run_v2/out/batch_011_out.json"
d=json.load(open(fp,encoding="utf-8"))
new="信号中、独角兽估值且服务1500家医院，信息量一般；差异化在把护士招聘做成医院反向抢人的匹配市场。其「反向抢人」匹配机制国内可借鉴，但护士招聘与银发直接关联弱，宜作医疗人力基础设施参照而非银发主库标的。"
for e in d["enterprises"]:
    if e["serial"]=="#0743":
        e["recommend"]=new
        print("updated #0743 -> len",len(new))
json.dump(d,open(fp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
