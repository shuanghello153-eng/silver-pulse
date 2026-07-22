# -*- coding: utf-8 -*-
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
REWORK = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, REWORK)
from check_single import validate, content_len

BATCH = os.path.join(REWORK, "batches_score", "batch_49.json")
OUTDIR = HERE
data = json.load(open(BATCH, encoding="utf-8"))

# --- REW 重写文本（V5 编辑判断层，不复述融资/规模/状态，三维度覆盖） ---
REWRITE = {
    "#1218": "助听器赛道里这家走光传导技术路线、用光代替传统放大，技术壁垒在光声转换音质稀缺。素材可挖其高端自费用户定位与临床适配故事；差异化在'不放大只传光'的反常识路线。国内可孚医疗等做基础助听器的团队，可借鉴其高端技术升级与自费市场打法，把听力干预往高客单走。",
    "#1271": "退休理财里把养老储蓄转成年金式现金流、做可视化收支视图，素材可挖其用户教育与转化漏斗。差异化在'现金流视角'而非单纯卖产品，反共识点是以收入管理代替资产增值叙事。国内天天基金的养老目标基金可借鉴这种现金流呈现与顾问式讲解，平移给初老客群做收入规划。",
    "#1282": "养老监测里用毫米波雷达做非接触式跌倒与呼吸感知，无穿戴无摄像头的方案素材可挖其机构部署与数据沉淀案例。差异化在无感监测替代可穿戴，错位在隐私友好。国内清雷科技等同赛道玩家可借鉴其雷达算法与场景化落地，平移到独居老人居家看护。",
    "#1325": "数字化医护养老把'产品+服务+数字化'叠起来，还接辅具租赁与适老化改造，模式素材可挖其多城运营与工单数据。差异化在长护险上门照护之外多加辅具与改造闭环，错位在运营数字化深度。国内居家养老商可复用其'长护险+辅具租赁'双轮，学其把服务流沉淀成数据资产。",
    "#1350": "美国私营养老护理运营商只做后台咨询与运营支持、不持有物业，轻资产托管输出的打法素材可挖其多州机构赋能案例。差异化在'管而不持'、把运营SOP与培训做成可售卖产品，壁垒在连锁管理经验。国内养老运营方可借鉴其'托管输出'模式，把重资产机构转成运营服务生意。",
    "#1360": "街镇小微养老点靠街坊熟人做上门照护与陪聊，这类本地样本素材可挖其获客与信任建立逻辑。差异化在熟人网络替代平台调度、轻资产周转，错位在扎根本地社区。国内县域小机构可搬其'熟人+上门'做法，学其用口碑而非投放获客，做街镇微养老节点。",
}

# --- 三维整数打分（info/diff/copy 各 0~10） ---
SCORE = {
    "#1218": (6, 8, 5), "#1223": (6, 7, 6), "#1224": (6, 7, 6), "#1270": (7, 6, 7),
    "#1271": (6, 6, 7), "#1282": (6, 7, 6), "#1283": (6, 7, 6), "#1284": (6, 6, 6),
    "#1301": (8, 7, 7), "#1325": (7, 6, 7), "#1350": (6, 7, 7), "#1357": (5, 5, 6),
    "#1360": (4, 5, 6), "#1362": (5, 6, 6), "#1363": (5, 5, 6), "#1364": (5, 6, 6),
    "#1365": (4, 5, 6), "#1366": (4, 5, 6), "#1367": (6, 6, 5), "#1373": (5, 6, 6),
}

written = 0
failed = []
for e in data:
    serial = e.get("serial")
    is_v5 = bool(e.get("_is_v5_already"))
    if is_v5:
        recommend = e.get("current_recommend")
    else:
        recommend = REWRITE.get(serial)
        if recommend is None:
            failed.append((serial, "缺少重写文本"))
            continue
    info, diff, copy = SCORE.get(serial, (5, 5, 5))

    draft = {
        "serial": serial,
        "recommend": recommend,
        "info": info,
        "diff": diff,
        "copy": copy,
        "name_cn": e.get("name_cn"),
        "name_en": e.get("name_en"),
        "desc_cn": e.get("desc_cn"),
        "highlights": e.get("highlights"),
        "stage": e.get("stage"),
        "_is_v5_already": is_v5,
    }
    ctx = {
        "serial": serial,
        "name": e.get("name_cn") or "",
        "name_cn": e.get("name_cn") or "",
        "desc_cn": e.get("desc_cn") or "",
        "highlights": e.get("highlights") or [],
        "stage": e.get("stage") or "",
        "recommend": recommend,
    }
    iss = validate(ctx)
    if iss:
        failed.append((serial, iss))
        print(f"[FAIL] {serial}: {iss}")
        continue
    fp = os.path.join(OUTDIR, f"draft_{serial}.json")
    json.dump(draft, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    written += 1
    print(f"[PASS] {serial} len={content_len(recommend)} info={info} diff={diff} copy={copy}")

print(f"\nWROTE {written} | FAILED {len(failed)}")
