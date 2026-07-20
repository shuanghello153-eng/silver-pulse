# -*- coding: utf-8 -*-
import json, os, re

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework"
BATCHES = ["batch_src_012.json","batch_src_013.json","batch_src_014.json","batch_src_015.json"]
OUT = os.path.join(BASE,"drafts_v4")

# 载入原始企业卡
orig={}
for bf in BATCHES:
    for c in json.load(open(os.path.join(BASE,"batches_full",bf),encoding="utf-8")):
        orig[c["serial"]]=c

# 载入生成结果（仅校验本批次 012-015 对应的80家）
drafts={}
for fn in os.listdir(OUT):
    if fn.startswith("draft_") and fn.endswith(".json"):
        d=json.load(open(os.path.join(OUT,fn),encoding="utf-8"))
        if d["serial"] in orig:
            drafts[d["serial"]]=d

def cn(s): return (s or "").replace(" ","").replace("\n","")

# ---- 1) 全字段去重：recommend 与原始各字段的连续10字重叠 ----
print("=== 全字段去重检查（≥10字连续相同即报警）===")
dedup_err=0
for serial,d in drafts.items():
    rec=cn(d["recommend"])
    c=orig[serial]
    fields=[]
    fields.append(("desc_cn",cn(c.get("desc_cn",""))))
    fields.append(("silver_reason",cn(c.get("silver_reason",""))))
    fields.append(("description",cn(c.get("description",""))))
    hl=c.get("highlights")
    if isinstance(hl,list):
        for h in hl: fields.append(("highlights",cn(h)))
    elif isinstance(hl,str):
        fields.append(("highlights",cn(hl)))
    fd=c.get("funding_latest")
    if isinstance(fd,dict):
        fields.append(("funding_display",cn(fd.get("display",""))))
    fields.append(("funding_total",cn(str(c.get("funding_total","")))))
    for fname,fval in fields:
        if len(fval)<10: continue
        # 滑动窗口检测连续10字相同
        bad=None
        for i in range(len(fval)-9):
            sub=fval[i:i+10]
            if sub in rec:
                bad=sub; break
        if bad:
            print("  %s 与字段[%s]连续相同: %s"%(serial,fname,bad))
            dedup_err+=1
print("去重问题数:",dedup_err)

# ---- 2) 四维覆盖 ----
print("\n=== 四维覆盖检查 ===")
sig_tok=["融资","获","轮","万美元","万欧元","亿","种子","A轮","B轮","Pre-","战略","投资","领投","金额","信号","2024","2025","2026","2023","2022","2021","2020","2027","2019","2018","2017","2016","2013","2012","2015","2014","2009","2001","2000","信息","披露","公开","透明","数据"]
diff_tok=["亮点","差异","独特","不同","壁垒","不是","而非","而非","避开","区别","稀缺","强在","把","做成"]
copy_tok=["国内","中国","可借鉴","可学","对标","参考","借鉴","平移","复制","照搬","适合","落地","思路","模式","路径","暂存","观察"]
info_tok=["信息","公开","披露","透明","数据","资料","成熟","详情","有限","薄","细节","不足","少","样本","早期"]
miss=0
for serial,d in drafts.items():
    rec=d["recommend"]
    has_sig=any(t in rec for t in sig_tok)
    has_diff=any(t in rec for t in diff_tok)
    has_copy=any(t in rec for t in copy_tok)
    has_info=any(t in rec for t in info_tok)
    if not (has_sig and has_diff and has_copy and has_info):
        miss+=1
        print("  %s 缺维度 sig=%s diff=%s copy=%s info=%s"%(serial,has_sig,has_diff,has_copy,has_info))
print("四维缺失数:",miss)

# ---- 3) 跨企业相似度（3-gram Jaccard）----
print("\n=== 跨企业相似度（3-gram Jaccard >0.5 报警）===")
def shingles(s):
    s=cn(s); return set(s[i:i+3] for i in range(len(s)-2))
vecs={s:shingles(d["recommend"]) for s,d in drafts.items()}
serials=list(vecs.keys())
sim_err=0
maxpair=None;maxv=0
for i in range(len(serials)):
    for j in range(i+1,len(serials)):
        a,b=vecs[serials[i]],vecs[serials[j]]
        if not a or not b: continue
        jac=len(a&b)/len(a|b)
        if jac>maxv: maxv=jac;maxpair=(serials[i],serials[j])
        if jac>0.5:
            sim_err+=1
            print("  %s ~ %s 相似度=%.2f"%(serials[i],serials[j],jac))
print("相似超阈值对数:",sim_err,"  最高一对:",maxpair,round(maxv,3))
print("\nDONE")
