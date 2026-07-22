# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, _ctx_from_db

BATCH = os.path.join(HERE, "batches_score", "batch_25.json")
OUT = os.path.join(HERE, "drafts_v5")
recs = json.load(open(BATCH, encoding="utf-8"))

# 重写（_is_v5_already=false）：编辑判断层，禁复述融资/上市/规模，覆盖 信息量+差异化+可复制
REWRITE = {
"#1027": ("围绕美国PACE整合照护计划，把诊疗、理赔与财务三类数据合成老人风险洞察，供上百家机构覆盖数万参保人，信息密度高、可拆解。独特在自研风险评级加专用病历深度绑定，专做双重资格低收入老人群体。国内长护险经办可借鉴其'数据即主动管理'思路，把分散数据源拧成干预清单，做本土化风险分层。", 8, 8, 7),
"#1076": ("背靠家电生态做家庭服务机器人，把清洁、康复外骨骼与陪伴分垂域落地，用兄弟IP形象降低老人对机器人的抵触。信息上，其渠道与供应链素材可拆解：洗衣扫地经验平移到助老场景。差异在'家电即入口'——以家庭场景牵引具身研发，而非从实验室造人。国内美的、海信等家电巨头可借鉴其把存量渠道与场景模型绑定、分拆垂域降成本的路径。", 8, 8, 8),
"#1106": ("从女性健康这一信息洼地切入，用月经血加外周血多组学做女性全周期解码，覆盖生育、激素、围绝经与早癌，资料详实可挖。差异在把常被忽视的月经血当诊断样本，围绝经管理直连心血管与骨健康。国内女性健康平台可借鉴其居家采样加临床教练加AI的订阅打法，做本土化慢病前移管理。", 8, 8, 7),
"#1107": ("信息上，极简腕带脱离手机、自动接急救中心的减法打法有故事性可挖。差异在不依赖手机与家庭群组分层响应，把救援网做轻。做不依赖手机、能续航约三周的极简跌倒腕带，用减法换佩戴依从，适合写'非手机依赖急救'切口。国内安康通、华为小米苹果的跌倒检测可借鉴其医保买单加轻资产接急救网的闭环，破解线下救援碎片化。", 7, 8, 8),
"#1111": ("信息上，其'脑穿梭'平台把基因沉默分子送进大脑、对准遗传性早发阿尔茨海默，技术路线反共识可拆解。差异在攻克把RNA药送过生理屏障这一全行业难题，对标罗氏诺华的脑穿梭路线。国内绿谷、先声等神经退行创新药可借鉴其上游递送加基因沉默平台思路，做本土化靶点选择。", 7, 9, 6),
"#1188": ("信息上，便携相机免散瞳拍视网膜、借AI识别糖网青光与黄斑变并外延心血管风险，把眼睛当全身健康窗口，资料详实可挖。差异在基层用AI替代专科读片、以卫生系统共建铺量。国内鹰瞳科技、腾讯觅影等眼底AI可借鉴其便携设备加体系共建加全身风险外延的组合，做基层眼科筛查商业化。", 8, 7, 7),
"#1202": ("信息上，通用人形机器人横跨工业与家庭陪护，消费级小布米借春晚出圈，有故事性可挖。差异在低价消费级打法，把人形机器人从工业演示拉进客厅。国内优必选、乐聚等可借鉴其价格下探与消费级节奏，但家庭陪护的安全交互与内容生态仍是落地门槛。", 7, 8, 7),
"#1255": ("信息上，自主配送机器人给园区社区与养老机构送餐送药，运营素材可挖。差异在跨国商超与工业客户基底，给养老配送提供稳定订单来源。国内南京新百、九如城等养老配送玩家可借鉴其机器人加场景运营的轻资产打法，但海外客户密度难平移。", 7, 7, 8),
"#1277": ("信息上，其护理与心理垂直EHR承载海量患者记录，资料厚可拆解。差异在把护理与心理照护合进同一套档案，而非通用HIS拼凑。国内乐湾、优享陪诊等护理信息化可借鉴其垂直深耕打法，但英国NHS生态依赖难直接平移。", 8, 7, 7),
}

def round_score(x):
    return int(round(float(x)))

results = []
for r in recs:
    s = r["serial"]
    nm = r.get("name_cn")
    if r.get("_is_v5_already"):
        rec = r["current_recommend"]
        info = round_score(r.get("current_info", 6))
        diff = round_score(r.get("current_diff", 6))
        copy = round_score(r.get("current_copy", 6))
    else:
        rec, info, diff, copy = REWRITE[s]
    draft = {
        "serial": s,
        "recommend": rec,
        "info_score": int(info),
        "diff_score": int(diff),
        "copy_score": int(copy),
    }
    fp = os.path.join(OUT, f"draft_{s}.json")
    json.dump(draft, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 门禁自测（用 DB 上下文，跳过 R10/R6/R7/R8 由单文件 CLI 天然不查）
    ctx = _ctx_from_db(s)
    tmp = dict(ctx)
    tmp["recommend"] = rec
    tmp["name"] = r.get("name")
    tmp["name_cn"] = r.get("name_cn")
    iss = validate(tmp)
    status = "PASS" if not iss else "FAIL:" + str(iss)
    results.append((s, nm, status))

for s, nm, st in results:
    print(f"{s} {nm}: {st}")
print("TOTAL", len(results), "PASS", sum(1 for x in results if x[2]=="PASS"))
