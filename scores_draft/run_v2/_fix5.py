import json
fixes = {
 "batch_004_out.json": {
   "#1153": "信号中（养老地产资本热度持续）、信息极丰富（官网IR+2025财报），REIT模式稳健但差异化不强；国内险资/地产基金可复制其对标其资产组合与出租率逻辑，与Welltower并读能看清'银发地产'的资本纪律与周期。",
   "#1155": "信号中（2025年报披露）、信息丰富，triple-net REIT稳健但高度依赖运营商偿付，差异化在租户风险管控；国内护理院重资产可参考triple-net，但REITs/医保差异大、难平移——其'租户风险管控'是国内最该复制的看点。",
   "#1156": "信号中（年报+出海收购报道）、信息丰富，从单租户分拆到多元+出海的成长型REIT，模式清晰非反共识；国内'运营+地产'分拆REIT可参考其架构，但A股无纯养老REIT、出海难复制——其'轻杠杆+高出租率+多元租户'资本纪律值得借鉴。",
   "#1158": "信号中（财报+行业媒体）、信息丰富，居家输液模式稳健顺常识、反共识性低；国内京东健康上门/民营护理站有同类，但支付以医保/个人为主、上门标准化弱。其'药师驱动+冷链+居家场景'体系可复制对标，尤适老龄化下居家医疗。",
 },
 "batch_005_out.json": {
   "#1173": "信号中（曾为衰老细胞清除先锋，2025被纳斯达克摘牌清算）、信息量足，差异化在'局部给药避系统毒性'的反共识路径；但公司层面现金枯竭、复制性低。国内抗衰创业最该学：好科学≠好公司，须控现金流、聚焦明确适应症与支付路径。",
 }
}
for fn, mp in fixes.items():
    fp=f"scores_draft/run_v2/out/{fn}"
    d=json.load(open(fp,encoding="utf-8"))
    for e in d["enterprises"]:
        if e["serial"] in mp:
            e["recommend"]=mp[e["serial"]]
            print("fixed", e["serial"], "len", len(mp[e["serial"]]))
    json.dump(d,open(fp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
