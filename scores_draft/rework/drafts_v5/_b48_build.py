# -*- coding: utf-8 -*-
"""general-purpose-61: batch_48 V5 编辑判断层推荐理由 + info/diff/copy 整数打分。
_is_v5_already=True -> 保留 current_recommend + 补分
_is_v5_already=False -> 重写(禁复述融资/上市/规模；覆盖 信息量+差异化+可复制；50-240字) + 打分
门禁: validate(..., skip=['R10','R6','R7','R8'])
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from check_single import validate, _ctx_from_db

SRC = os.path.join(ROOT, "batches_score", "batch_48.json")
OUT = HERE

batch = json.load(open(SRC, encoding="utf-8"))

# 6 家需重写（V5 编辑判断层）
REWRITE = {
    "#0837": "护理人员每天要登记大量长者健康变化、派发任务，这套记录与任务协同是机构运营的底层数据入口，可挖护工排班与异常预警的真实落地痛点。它用轻量协同替代笨重ERP，和全套养老系统错位，差异化在'先占记录入口'。国内颐讯、关爱养老也做养老SaaS，可学其从记录切入再扩数据的打法，对做机构数字化工具的创业者有参照价值。",
    "#0887": "缓和疗护在国内仍属早期，这家把临终关怀做成覆盖身心的全人护理，可挖其疼痛管理与家属支持的落地细节与服务质量数据。它用'居家+按价值付费'打包，与单点陪诊或纯医疗服务错位，差异化在支付与服务绑定。国内泰康安宁、慈爱嘉也做临终关怀，可学其居家缓和疗护的本土化打法，对做安宁服务的创业者有参照价值。",
    "#0900": "把视力自测搬上手机并拿到FDA批准，监管获批本身就是可挖的合规与临床验证素材，能拆解它如何把验光标准数字化。它用远程自测替代线下诊室验光，和实体眼镜店错位，差异化在合规门槛。国内云瞳、艾索诺也做在线眼科，可学其'在线验光+拿证'打法做消费医疗，对做远程检测的创业者有参照价值。",
    "#1079": "研究院背景团队把髋部助行外骨骼直接做个人预售，科研转民用的路径可挖，能拆解它如何把实验室结构变成消费级产品。它用轻量家用款直面C端，与傅利叶、程天的刚性康复外骨骼错位，差异化在'科研转民用'速度。国内程天科技也做助行外骨骼，可学其用预售验证真实需求的打法，对做出海银发硬件的团队有参照价值。",
    "#1214": "在线助听器订阅把原本一次性的高价听力服务拆成月费，模式可挖，能拆解它如何用远程验配降低门槛并维持续费。它用持续服务替代一锤子买卖，与卖硬件的验配中心错位，差异化在'服务化'。国内锦好医疗、可孚医疗也做助听器，可学其远程订阅打法做银发听力服务，对做医疗硬件服务化的创业者有参照价值。",
    "#1215": "DTC助听器靠APP自助验配省掉线下门店，背后供应链与品控规模可挖，能拆解它如何用软件替代验配师。它用自助流程替代人工验配中心，差异化在'去门店'。国内锦好医疗也做助听器，可学其APP自助验配打法做银发听力自助，对做消费级医疗器械的创业者有参照价值。",
}

# 14 家保留 + 补分 / 6 家重写 + 打分
SCORES = {
    "#0875": (7, 7, 7), "#0904": (6, 7, 7), "#0912": (7, 7, 7), "#0947": (7, 7, 7),
    "#0948": (6, 7, 7), "#0971": (6, 7, 7), "#0979": (6, 7, 7), "#0996": (6, 7, 7),
    "#1060": (7, 7, 7), "#1137": (7, 8, 7), "#1138": (7, 7, 7), "#1149": (7, 7, 8),
    "#1150": (7, 7, 7), "#1216": (6, 7, 7),
    "#0837": (6, 6, 7), "#0887": (6, 7, 7), "#0900": (7, 7, 7), "#1079": (7, 7, 7),
    "#1214": (7, 7, 8), "#1215": (6, 7, 7),
}

SKIP = ["R10", "R6", "R7", "R8"]
results = []
for e in batch:
    s = e["serial"]
    if e.get("_is_v5_already"):
        rec = e["current_recommend"]
        mode = "KEEP"
    else:
        rec = REWRITE[s]
        mode = "REWRITE"
    i, d, c = SCORES[s]
    doc = {"serial": s, "recommend": rec, "info": i, "diff": d, "copy": c}
    fp = os.path.join(OUT, "draft_%s.json" % s)
    json.dump(doc, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 门禁：合并 DB 上下文 + 跳过 R10/R6/R7/R8
    ctx = _ctx_from_db(s)
    tmp = dict(ctx)
    for k in ("recommend", "desc_cn", "highlights", "stage", "funding_latest", "funding_total"):
        if k in doc and doc[k] is not None:
            tmp[k] = doc[k]
    iss = validate(tmp, skip=SKIP)
    gate = "PASS" if not iss else "FAIL:" + str(iss)
    results.append((s, mode, i, d, c, len(rec), gate))

print(f"{'serial':7} {'mode':8} i/d/c  len  gate")
for s, mode, i, d, c, ln, gate in results:
    print(f"{s:7} {mode:8} {i}/{d}/{c}  {ln:3}  {gate}")
fails = [r for r in results if not r[6].startswith("PASS")]
print(f"\nTOTAL={len(results)} PASS={len(results)-len(fails)} FAIL={len(fails)}")
for r in fails:
    print("  FAIL", r)
