# -*- coding: utf-8 -*-
"""Batch 28 (general-purpose-28) V5 drafts builder.

For _is_v5_already:true -> keep current_recommend, add info/diff/copy.
For _is_v5_already:false -> rewrite recommend (V5 editing-judgment layer,
no restating financing/IPO/scale), add info/diff/copy.
Output only to drafts_v5/draft_<serial>.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.join(HERE, "batches_score", "batch_28.json")
OUT = os.path.join(HERE, "drafts_v5")

batch = json.load(open(BATCH, encoding="utf-8"))

# recommends for the false ones: V5 editing-judgment layer.
# Principle: no restating financing/IPO/scale numbers from the fact sheet;
# cover 信息量 / 差异化 / 可复制; no company name; no banned templates.
REWRITE = {
    "#0512": "把老人手机与24小时紧急响应做成订阅制适老通信的打法值得拆。信息量上，其硬件加保险包绑定的订阅结构是可挖样本；差异化在大字体功能机叠加持续响应服务、而非卖一次性硬件；国内安康通、守护宝等做类似紧急呼叫，可学其“硬件加响应订阅”的适老通信思路，但美国医保免自费结构难平移。",
    "#0515": "把分散的家政护理做成全球连锁品牌的打法值得拆。信息量上，其加盟网络与护理员培训体系是可拆样本；差异化在加盟加关系型照护、把护工做成职业化网络而非零散中介；国内易得康、福寿康等做居家护理，可学其用品牌标准与培训提升护理员职业化、再用平台调度的思路，但重线下密度、难平移。",
    "#0604": "把用药依从做成硬件加家属提醒的打法值得拆。信息量上，其依从率试验与预封装药袋机制是可挖样本；差异化在多格药袋按钟点自动弹出、漏服即通知家属的医疗场景；国内小米、美的等做智能药盒，可学其“硬件加家属提醒加药师预封装”的依从性提升思路，但要过医疗注册与本地药师网络两道关。",
    "#0633": "把成人失禁用品做成DTC订阅加线下零售双渠道的打法值得拆。信息量上，其皮肤安全验证与渠道并行是可拆样本；差异化在适老失禁用品叠加订阅、降低老年采购门槛；国内可靠股份、豪悦护理等做失禁护理，可学其DTC订阅加药房零售并行、用皮肤安全做信任背书的思路，但国内失禁消费教育弱、复购难起。",
    "#0722": "把保险计划与诊所自营绑定的医疗整合打法值得拆。信息量上，其风险合约与自营保险结构是可挖样本；差异化在支付加服务一体、把医保结余与服务方利益对齐；国内平安健康、镁信健康等做医疗整合，可学其以风险合约对齐支付方与服务方的思路，但美国按人头预付结构难平移、合规差异大。",
    "#0788": "把食物当药物的慢病饮食干预打法值得拆。信息量上，其临床膳食配方与支付方覆盖是可拆样本；差异化在医学定制餐加远程营养师再加远程监测拼成一体；国内薄荷健康、糖友饱饱等做慢病营养，可学其以保险覆盖降低自付、用临床膳食做慢病干预的思路，但国内支付方覆盖弱、难照搬。",
    "#0801": "把诊所搬进员工家中的轻资产医疗打法值得拆。信息量上，其会员制结构与上门服务组合是可挖样本；差异化在按人月费打包、零自付降低就医门槛；国内企鹅医生、妙健康等做企业健康，可学其固定人月费加上门加虚拟的轻资产思路，但银发关联弱、不涉联邦医保、参考价值有限。",
    "#0862": "用短时神经刺激而非整夜追踪的失眠干预打法值得拆。信息量上，其非药物干预机制与上线营收是可挖样本；差异化在脑电母语式神经刺激、比智能床垫更轻；国内倍轻松、SKG等做睡眠硬件，可学其非药物、短时长干预的适老失眠思路，但属通用消费硬件、老年失眠仅为潜在延伸。",
    "#0890": "把听力初筛下沉到药房与养老院的打法值得拆。信息量上，其便携一体机与云转介是可挖样本；差异化在单设备集成耳镜微吸与听力检查、把初筛推进社区；国内可孚、鱼跃等做听力设备，可学其便携一体机加云转介把听力初筛搬进社区的思路，且听力衰退是痴呆最强可干预诱因、选题角度硬。",
    "#0905": "把真人直播小班抗阻训练做成银发健身订阅的打法值得拆。信息量上，其高留存与认知练习组合是可挖样本；差异化在直播加小班加认知练习延缓肌肉流失、降跌倒风险；国内乐刻、尚体等做银发健身，可学其以社群陪伴加可量化力量指标做订阅的思路，但国内适老健身付费意愿弱、需找锚点。",
    "#0121": "把医疗设备与听力验配服务绑定的国产替代打法值得拆。信息量上，其自研芯片与连锁验配网络是可挖样本；差异化在产品加验配中心加连锁联盟的获客结构；国内听力行业多为外资，可学其连锁验配加上门医疗的思路，但要过注册与芯片研发两道门槛、且已有门店规模信息有限。",
    "#0127": "把老字号信任背书做成社区中医康养IP的打法值得拆。信息量上，其多板块协同与社区操课覆盖是可拆样本；差异化在老字号品牌加药养结合、把中医康养触达家庭；国内中医馆与养老品牌多，可学其社区康养IP打法，但老字号牌照与品牌难复制、参考价值在思路而非形态。",
}

# scores for the false ones (my AI three-dim judgment)
SCORE_FALSE = {
    "#0512": (6, 6, 7),
    "#0515": (6, 6, 6),
    "#0604": (5, 5, 6),
    "#0633": (6, 5, 6),
    "#0722": (6, 5, 4),
    "#0788": (6, 5, 5),
    "#0801": (5, 5, 5),
    "#0862": (5, 5, 5),
    "#0890": (6, 6, 6),
    "#0905": (6, 6, 6),
    "#0121": (6, 7, 5),
    "#0127": (7, 5, 4),
}

results = {}
for e in batch:
    ser = e["serial"]
    if e.get("_is_v5_already"):
        rec = e["current_recommend"]
        info = int(round(e.get("current_info", 6)))
        diff = int(round(e.get("current_diff", 6)))
        copy = int(round(e.get("current_copy", 6)))
    else:
        rec = REWRITE[ser]
        info, diff, copy = SCORE_FALSE[ser]
    draft = {
        "serial": ser,
        "recommend": rec,
        "info": info,
        "diff": diff,
        "copy": copy,
    }
    fp = os.path.join(OUT, "draft_" + ser + ".json")
    json.dump(draft, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    results[ser] = (len(rec), e.get("_is_v5_already"))

print("written:", len(results))
for k, v in results.items():
    print(k, "chars=", v[0], "kept=" , v[1])
