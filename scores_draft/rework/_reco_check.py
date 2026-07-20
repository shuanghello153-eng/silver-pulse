# -*- coding: utf-8 -*-
import json, os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single import validate, _ctx_from_db

TARGET = set("#0592 #0596 #0597 #0601 #0603 #0605 #0606 #0607 #0616 #0617 #0621 #0622 "
                 "#0623 #0625 #0626 #0627 #0630 #0636 #0637 #0641 #0643 #0653 #0655 #0657 "
                 "#0658 #0659 #0660 #0661 #0663 #0665 #0668 #0670 #0671 #0673 #0674 #0680".split())

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts_v5")
files = sorted(glob.glob(os.path.join(D, "draft_#*.json")))
recs = []
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    if d.get("serial") not in TARGET:
        continue
    ctx = _ctx_from_db(d.get("serial", ""))
    tmp = dict(ctx)
    for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
        if k in d and d[k] is not None:
            tmp[k] = d[k]
    recs.append((d.get("serial"), tmp))

others = [r[1].get("recommend", "") for r in recs]
print(f"== 校验目标草稿 {len(recs)} 份 | recommend 相关项 + 跨企业雷同(R10)，R6/R7/R8(主库记录)已跳过 ==\n")
any_fail = False
for serial, tmp in recs:
    iss = validate(tmp, others=others, skip=["R6", "R7", "R8"])
    status = "PASS" if not iss else "FAIL:" + str(iss)
    if iss:
        any_fail = True
    print(f"  {serial}: {status}")
print("\n== 结论:", "全部 recommend 相关项 PASS" if not any_fail else "存在 FAIL，需修复")
