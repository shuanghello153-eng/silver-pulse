# -*- coding: utf-8 -*-
"""汇总 draft_out/ 全部分片(137家)，做入库前全量校验：
   ①字段完整 ②tag_l2⊆权威98词表 ③tag_l1有效且与tag_l2一致 ④描述门禁D1-D4
   ⑤recommend门禁R1-R10（含跨137雷同）⑥评分区分度 ⑦名称重复。"""
import json, os, sys, glob
from collections import Counter, defaultdict

ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scores_draft", "rework"))
from check_single import validate as validate_rec   # noqa
from check_description import validate_desc          # noqa

HERE = os.path.join(ROOT, "_qa_tmp", "ingest_187")
VOCAB = set(json.load(open(os.path.join(ROOT, "data/enterprise/_l2_l1.json"), encoding="utf-8")).keys())
L2L1 = json.load(open(os.path.join(ROOT, "data/enterprise/_l2_l1.json"), encoding="utf-8"))
VALID_L1 = {"养老服务", "康复辅具", "消费品", "文娱社交", "行业服务", "食品营养", "金融保险", "投资机构"}
# 4个live straggler也算合法tag_l2
STRAGGLERS = {"养老社区", "社区居家", "保险经纪", "健康管理"}
VOCAB |= STRAGGLERS

REQUIRED = ["name", "name_cn", "region", "description", "recommend", "tag_l2", "tag_l1",
            "info_score", "diff_score", "copy_score", "stage"]

# 库内已有名称（去重兜底）
db = json.load(open(os.path.join(ROOT, "data/enterprise/all_enterprises.json"), encoding="utf-8"))
db_names = set()
for e in db:
    for k in ("name", "name_cn"):
        v = e.get(k)
        if v: db_names.add(str(v).strip().lower())

# 载入全部分片
records = []
for fp in sorted(glob.glob(os.path.join(HERE, "draft_out", "*.json"))):
    d = json.load(open(fp, encoding="utf-8"))
    for r in d:
        r["_srcfile"] = os.path.basename(fp)
        records.append(r)
print(f"载入 {len(records)} 家\n")

all_recs = [r.get("recommend", "") for r in records if isinstance(r.get("recommend"), str)]

fails = defaultdict(list)
score_vals = defaultdict(list)
name_seen = {}
for i, r in enumerate(records):
    nm = r.get("name", f"?{i}")
    key = f"{r.get('_srcfile')} | {nm}"
    iss = []
    # ①字段完整
    for f in REQUIRED:
        v = r.get(f)
        if v in (None, "", []):
            iss.append(f"缺字段[{f}]")
    # ②③标签
    t2 = r.get("tag_l2") or []
    t1 = r.get("tag_l1") or []
    if isinstance(t2, str): t2 = [t2]
    if isinstance(t1, str): t1 = [t1]
    if not t2:
        iss.append("tag_l2为空(0标签禁止)")
    if len(t2) > 3:
        iss.append(f"tag_l2超3个({len(t2)})")
    for b in t2:
        if b not in VOCAB:
            iss.append(f"tag_l2非法[{b}]")
    for a in t1:
        if a not in VALID_L1:
            iss.append(f"tag_l1非法[{a}]")
    # tag_l1 应=tag_l2推导
    derived = set()
    for b in t2:
        l1 = L2L1.get(b)
        if isinstance(l1, list):
            l1 = l1[0] if l1 else None
        if l1: derived.add(l1)
    if derived and set(t1) != derived:
        iss.append(f"tag_l1与tag_l2不一致(应={sorted(derived)},实={sorted(t1)})")
    # ④描述门禁
    iss += validate_desc(r)
    # ⑤recommend门禁（others=其余136家）
    others = [x for x in all_recs if x != r.get("recommend")]
    iss += validate_rec(r, others=others)
    # ⑥评分
    for sk in ("info_score", "diff_score", "copy_score"):
        try:
            sv = float(r.get(sk))
            score_vals[sk].append(sv)
            if not (0 <= sv <= 10):
                iss.append(f"{sk}越界({sv})")
        except (TypeError, ValueError):
            iss.append(f"{sk}非数值")
    # ⑦名称重复
    lname = str(nm).strip().lower()
    if lname in db_names:
        iss.append("与库内名称重复(应已去重)")
    if lname in name_seen:
        iss.append(f"137内重名(另见{name_seen[lname]})")
    else:
        name_seen[lname] = key

    if iss:
        fails[key] = iss

# 输出
print(f"===== 校验结果：{len(records)-len(fails)}/{len(records)} 通过 =====\n")
if fails:
    for k, iss in fails.items():
        print(f"✗ {k}")
        for x in iss:
            print(f"    - {x}")
    print()
print("===== 评分区分度 =====")
for sk, vals in score_vals.items():
    c = Counter(vals)
    print(f"{sk}: min={min(vals)} max={max(vals)} 均值={sum(vals)/len(vals):.2f} 分布={dict(sorted(c.items()))}")

# 存一份失败清单json
json.dump({k: v for k, v in fails.items()}, open(os.path.join(HERE, "_validate_fails.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n失败清单已写 _validate_fails.json（{len(fails)}家）")
