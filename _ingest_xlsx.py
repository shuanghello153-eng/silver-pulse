# -*- coding: utf-8 -*-
"""飞书 xlsx 企业入库：读取采集智能体产出的候选 JSON(_xlsx_candidates.json)，
逐家去重、补模板字段、打 ingest_time，写入 all_enterprises.json。
分类用现有词表；tag_l1/tag_l2 留空待标签AI填；不改动现有分类/标签体系。
"""
import json, copy

EP = "data/enterprise/all_enterprises.json"
CAND = "_xlsx_candidates.json"
ents = json.load(open(EP, encoding="utf-8"))
template = ents[0]
existing = {e.get("name", "").strip().lower() for e in ents}
maxserial = max(int(str(e.get("serial", "#0")).replace("#", "")) for e in ents if str(e.get("serial", "")).startswith("#"))

cands = json.load(open(CAND, encoding="utf-8"))
# 合法一级（防止采集方误填）
VALID_L1 = {"养老服务","康复辅具","消费品","文娱社交","食品营养","行业服务","金融保险","投资机构"}

added=0; skipped=0; bad_cat=0
for c in cands:
    nm=c.get("name","").strip().lower()
    if not nm:
        continue
    if nm in existing:
        skipped+=1; continue
    # 分类兜底：非法一级则降级为行业服务/行业媒体（不新增分类）
    l1=c.get("category_l1")
    if l1 not in VALID_L1:
        l1="行业服务"; bad_cat+=1
    l2=c.get("category_l2") or ""
    maxserial+=1
    ne=copy.deepcopy(template)
    ne["serial"]=f"#{maxserial:04d}"
    ne["name"]=c.get("name","")
    ne["region"]=c.get("region","国内")
    ne["category_l1"]=l1
    ne["category_l2"]=l2
    ne["description"]=c.get("description","")
    ne["desc_cn"]=c.get("description","")
    ne["website_url"]=c.get("website_url","")
    ne["crunchbase_url"]=""   # 模板深拷贝会带出 AgeClub 的 URL，新企业一律清空
    ne["business_tags"]=[]    # 同上，避免继承模板的业务标签
    ne["founded"]=c.get("founded","未披露")
    ne["stage"]=c.get("stage","未披露")
    ne["investors"]=c.get("investors","未披露")
    fl=c.get("funding_latest") or {}
    ne["funding_latest"]={"date":fl.get("date","未披露"),"amount":fl.get("amount","未披露"),
                          "round":fl.get("round","未披露"),"display":fl.get("display","未披露")}
    ft=c.get("funding_total") or {}
    ne["funding_total"]={"amount":ft.get("amount","未披露"),"display":ft.get("display","未披露")}
    ne["tags"]=c.get("tags",[]) or []
    ne["source"]=c.get("source","飞书供需对接表")
    ne["business_model"]=c.get("business_model","")
    ne["business_model_cn"]=c.get("business_model_cn","")
    ne["tag_l1"]=[]
    ne["tag_l2"]=[]
    ne["news_coverage"]={"news_count":0,"news_quality":"unscored","latest_news":None}
    ne["value_score"]=0
    ne["recommend"]=""
    ne["name_cn"]=""
    ne["highlights"]=(f"成立于{ne['founded']}年" if ne["founded"]!="未披露" else "")
    ne["payor_model"]="未披露"
    ne["ingest_time"]="2026-07-16"
    ents.append(ne); existing.add(nm); added+=1

json.dump(ents,open(EP,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(f"飞书企业入库：新增 {added} 家，跳过已存在 {skipped} 家，非法一级已兜底 {bad_cat} 家；现有总数 {len(ents)}")
