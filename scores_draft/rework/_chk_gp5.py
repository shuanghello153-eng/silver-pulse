# -*- coding: utf-8 -*-
import json, glob
from collections import Counter

OUTDIR = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework"
MINE = {"#0474","#0480","#0483","#0560","#0634","#0642","#0717","#0722","#0729","#0732",
"#0738","#0743","#0696","#0895","#0977","#1331","#1334","#0387","#0479","#0500","#0501",
"#0511","#0598","#0604","#0608","#0611","#0624","#0632","#0633","#0638","#0639","#0644",
"#0646","#0650","#0656","#0666"}
PAYOR_TABLE = ["个人自费","个人自费+政府补贴","个人自费+长护险","个人自费+医保",
    "B端机构采购","B端机构采购+政府付费","B端机构采购+政府/商保支付",
    "政府医保/商保支付","混合支付","不适用（投资机构）","未搜到"]
TEMPLATES = ["复制需结合本地资源","国内宜学其思路而非形态",
    "轻模式易复制，国内创业者可直接借鉴落地","切入XX赛道",
    "可照搬","易照搬","照搬","可抄其","可抄","可学其","可学","可借鉴",
    "值得借鉴","直接借鉴","落地","避开重资产陷阱",
    "可对照","可参照","可研其","可借其","可长期对标","对照落地"]
SIGNAL = ["融资","轮","募资","上市","获投","领投","完成","上线","入选","热点","披露","投资",
          "营收","背书","首发","推出","签","扩张","成长","势头","估值","千万","A轮","B轮","C轮","D轮","种子"]
INFO = ["数据","显示","公开","研究","万","亿","%","准确率","灵敏度","特异度","累计","报道",
        "运营","营收","用户","家庭","机构","会员","服务","模型","精度","降低","提升","覆盖","省","减"]
DIFF = ["而非","区别","独特","壁垒","闭环","精准","首款","首个","区别于","绕开","不卖","不堆","不做",
        "非","自研","专有","自有","独家","反共识","轻量","垂直","专注","只","仅","取代","替代","破","重构",
        "差异","不靠","未走","轻资产","轻"]
COPY = ["国内","平移","参照","参考","复刻","复用","借鉴","抄","对标","推行","镜像","拿来"]

files = glob.glob(OUTDIR + "/draft_*.json")
problems = []
checked = 0
for fn in files:
    with open(fn, encoding="utf-8") as f:
        try:
            d = json.load(f)
        except Exception:
            continue
    serial = d.get("serial")
    if serial not in MINE:
        continue
    checked += 1
    if set(d.keys()) != {"serial","recommend","desc_cn","silver_reason","payor_model","update_time","flag"}:
        problems.append(f"{serial} 键集合异常: {list(d.keys())}")
    rec = d.get("recommend", {})
    for k in ["rec_v1","rec_v2","rec_v3"]:
        v = rec.get(k,"")
        if not (40 <= len(v) <= 90):
            problems.append(f"{serial} {k} 字数={len(v)}")
        for t in TEMPLATES:
            if t in v:
                problems.append(f"{serial} {k} 套话[{t}]")
    def ov(a,b):
        ca,cb=Counter(a),Counter(b); inter=sum((ca&cb).values()); union=sum((ca|cb).values())
        return inter/union if union else 0
    if ov(rec.get("rec_v1",""),rec.get("rec_v2",""))>=0.5: problems.append(f"{serial} v1/v2 重合>=0.5")
    if ov(rec.get("rec_v1",""),rec.get("rec_v3",""))>=0.5: problems.append(f"{serial} v1/v3 重合>=0.5")
    if ov(rec.get("rec_v2",""),rec.get("rec_v3",""))>=0.5: problems.append(f"{serial} v2/v3 重合>=0.5")
    dc=d.get("desc_cn","")
    if len(dc)<80: problems.append(f"{serial} desc<80")
    if dc.startswith(("是一家","致力于","专注于")) or "成立于" in dc[:20]:
        problems.append(f"{serial} desc 开头违规")
    if len(d.get("silver_reason",""))<30: problems.append(f"{serial} silver<30")
    if d.get("payor_model") not in PAYOR_TABLE: problems.append(f"{serial} payor 不在表: {d.get('payor_model')}")
    if d.get("update_time")!="2026-07-18": problems.append(f"{serial} update_time 错")
    blob="".join([rec.get("rec_v1",""),rec.get("rec_v2",""),rec.get("rec_v3","")])
    miss=[]
    if not any(k in blob for k in SIGNAL): miss.append("信号强度")
    if not any(k in blob for k in INFO): miss.append("信息量")
    if not any(k in blob for k in DIFF): miss.append("差异化")
    if not any(k in blob for k in COPY): miss.append("可复制")
    if miss:
        problems.append(f"{serial} 维度缺失: {miss}")

print(f"检查我的文件数: {checked}")
if problems:
    print("=== 问题 ===")
    for p in problems: print(p)
    print(f"共 {len(problems)} 处")
else:
    print("=== 我的36个 draft 全部校验通过（8规则+四维度）===")
