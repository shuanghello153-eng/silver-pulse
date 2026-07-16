#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V21b 走查修复：一次性处理四路走查确认的「必修」项。
1) tag_synonyms.json 同类词冲突清理
2) _l2_l1.json 视觉辅助 消费品→康复辅具
3) all_enterprises.json 合并3对重复企业 + 补3条占位简介 + JOGO加医疗器械 + 全库重派生 tag_l1
均先备份。默认 dry-run，加 --apply 落库。
"""
import json, os, sys, shutil, time

APPLY = "--apply" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data/enterprise/")
ENT = BASE + "all_enterprises.json"
MAP = BASE + "_l2_l1.json"
SYN = BASE + "tag_synonyms.json"
ts = time.strftime("%Y%m%d_%H%M%S")


def backup(p, tag):
    d = os.path.join(BASE, "backups")
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, f"{os.path.basename(p).replace('.json','')}_{ts}_{tag}.json")
    shutil.copy2(p, dst)
    print("  备份:", os.path.basename(dst))


syn = json.load(open(SYN, encoding="utf-8"))
m = json.load(open(MAP, encoding="utf-8"))
es = json.load(open(ENT, encoding="utf-8"))

log = []

# ============ 1. 同类词冲突清理 ============
def rm(l2, words):
    before = list(syn[l2])
    syn[l2] = [w for w in syn[l2] if w not in words]
    removed = [w for w in before if w in words]
    if removed:
        log.append(f"[同类词] {l2} 移除: {removed}")

def add(l2, words):
    exist = set(syn[l2])
    added = [w for w in words if w not in exist]
    syn[l2].extend(added)
    if added:
        log.append(f"[同类词] {l2} 新增: {added}")

# 长寿词：保健品移出 → 长寿抗衰接手
LONG = ["抗衰", "抗衰老", "长寿", "抗老化", "延寿", "ageing", "anti-aging", "anti aging", "抗衰老药物"]
rm("保健品", LONG)
add("长寿抗衰", LONG)
# 机器人 去 陪伴机器人（与文娱社交下同名二级冲突）
rm("机器人", ["陪伴机器人"])
# 慢病管理 去 糖尿病（与食品营养下二级规范名冲突）
rm("慢病管理", ["糖尿病"])
# 文娱 去 短视频（与文娱社交下二级规范名冲突）
rm("文娱", ["短视频"])
# SDOH 去 SODH 错别字
rm("SDOH", ["SODH"])
# 养老信息平台 去 一级级伞词
rm("养老信息平台", ["养老", "养老服务", "养老产业", "elderly care", "senior care", "养老业务", "银发服务"])
# 医疗器械 去 错挂词（属消费品-药品配送）
rm("医疗器械", ["数字药房", "病炊配送"])

# 校验：每个二级仍有同类词
empty = [l2 for l2, ws in syn.items() if not ws]
assert not empty, f"清理后出现无同类词的二级: {empty}"

# ============ 2. 视觉辅助 → 康复辅具 ============
old = m.get("视觉辅助")
m["视觉辅助"] = ["康复辅具"]
log.append(f"[归属] 视觉辅助 {old} → ['康复辅具']")

# ============ 3. 企业库修复 ============
def find_idx(name):
    for i, e in enumerate(es):
        if e.get("name") == name:
            return i
    return -1

# 3a 合并重复：keep_name 保留, drop_name 删除, 并入其 tag_l2
merges = [
    ("Intus Care", "IntusCare"),   # 保留信息更全的 Intus Care(307字)
    ("JOY FOR ALL", "joyforall"),  # 保留品牌规范名
    ("Jubo", "Jubo Health"),       # 保留含融资信息的 Jubo(106字)
]
drop_idx = []
for keep, drop in merges:
    ki, di = find_idx(keep), find_idx(drop)
    if ki < 0 or di < 0:
        log.append(f"[合并] 跳过(未找到): keep={keep}({ki}) drop={drop}({di})")
        continue
    ke, de = es[ki], es[di]
    merged_l2 = list(dict.fromkeys((ke.get("tag_l2") or []) + (de.get("tag_l2") or [])))
    ke["tag_l2"] = merged_l2
    ke["tags"] = merged_l2
    drop_idx.append(di)
    log.append(f"[合并] 保留「{keep}」删除「{drop}」，合并二级→{merged_l2}")

# 3b 补占位简介
descs = {
    "茑屋书店": "日本知名连锁书店品牌（隶属 Culture Convenience Club），以「书店+咖啡+生活方式」复合空间著称。代官山茑屋书店主打面向中老年客群的高品质文化生活场景，是银发文娱消费的标杆业态。",
    "九为健康": "聚焦中医智能化服务，围绕中医体质辨识、慢病调理与健康管理，面向中老年人群提供中医养生方案。",
    "问岐健康": "以人工智能技术切入中医诊疗，探索中医智能化辅助诊断与健康管理服务，面向中老年健康需求。",
}
for name, dc in descs.items():
    i = find_idx(name)
    if i >= 0:
        es[i]["desc_cn"] = dc
        es[i]["description"] = dc
        log.append(f"[简介] 补写「{name}」({len(dc)}字)")

# 3c JOGO Health 加 医疗器械（FDA数字疗法，非纯消费品；保留尿失禁）
i = find_idx("JOGO Health")
if i >= 0:
    l2 = es[i].get("tag_l2") or []
    if "医疗器械" not in l2:
        l2 = list(dict.fromkeys(l2 + ["医疗器械"]))
        es[i]["tag_l2"] = l2; es[i]["tags"] = l2
        log.append(f"[标签] JOGO Health 加 医疗器械 → {l2}")

# 删除重复记录（倒序删，避免索引错位）
for di in sorted(drop_idx, reverse=True):
    es.pop(di)

# ============ 4. 全库重派生 tag_l1（依据最新 _l2_l1）============
def L1of(v):
    return v[0] if isinstance(v, list) else v

rederive = 0
for e in es:
    l2 = e.get("tag_l2") or []
    new_l1 = list(dict.fromkeys(L1of(m[x]) for x in l2 if x in m))
    if (e.get("tag_l1") or []) != new_l1:
        e["tag_l1"] = new_l1
        rederive += 1
log.append(f"[派生] tag_l1 重算，变更 {rederive} 家；企业总数 {len(es)}")

# ============ 输出 ============
print("=" * 60)
for l in log:
    print(l)
print("=" * 60)
print(f"{'[APPLY 落库]' if APPLY else '[DRY-RUN 预演，加 --apply 落库]'}")

if APPLY:
    backup(SYN, "pre_v21b"); backup(MAP, "pre_v21b"); backup(ENT, "pre_v21b")
    json.dump(syn, open(SYN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(m, open(MAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(es, open(ENT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("已写入 3 个真相源文件。")
