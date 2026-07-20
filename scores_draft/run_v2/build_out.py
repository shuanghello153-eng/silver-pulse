# -*- coding: utf-8 -*-
import json

OUT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out/batch_000_out.json"

# 主库已核验的四维分与 research_value（仅输出，不重算）
SCORES = {
 "#0565": dict(info=9.0, diff=8.5, copy=7.0, rv=88.0),
 "#0855": dict(info=8.5, diff=8.0, copy=5.0, rv=81.5),
 "#0602": dict(info=9.0, diff=5.0, copy=3.0, rv=71.6),
 "#0398": dict(info=7.5, diff=6.5, copy=6.0, rv=73.1),
 "#0593": dict(info=7.0, diff=7.0, copy=5.0, rv=67.7),
 "#0594": dict(info=7.0, diff=7.0, copy=5.0, rv=67.7),
 "#0595": dict(info=8.0, diff=4.0, copy=3.0, rv=60.6),
 "#0850": dict(info=7.5, diff=7.0, copy=6.0, rv=71.2),
 "#0012": dict(info=8.0, diff=7.0, copy=8.0, rv=75.2),
 "#0461": dict(info=8.0, diff=6.5, copy=4.0, rv=66.1),
 "#0949": dict(info=8.0, diff=6.5, copy=4.0, rv=66.1),
 "#0954": dict(info=7.5, diff=6.5, copy=4.0, rv=64.7),
}
SIGNAL = {
 "#0565":10.0,"#0855":10.0,"#0602":9.55,"#0398":8.55,"#0593":7.55,"#0594":7.55,
 "#0595":7.55,"#0850":7.55,"#0012":7.05,"#0461":7.05,"#0949":7.05,"#0954":7.05,
}

# 企业名称（用于自检：recommend 不得包含）
NAMES = {
 "#0565":["Oak Street","Oak Street Health","橡树街"],
 "#0855":["Signify","Signify Health"],
 "#0602":["AbbVie","Abbvie","艾伯维"],
 "#0398":["松龄护老","Pine Care","松齡護老"],
 "#0593":["Tivity","Tivity Health"],
 "#0594":["SilverSneakers","Silver Sneakers"],
 "#0595":["IAC"],
 "#0850":["Sharecare"],
 "#0012":["善诊","Shanzhen"],
 "#0461":["Amedisys"],
 "#0949":["LHC Group","LHC"],
 "#0954":["Enhabit"],
}

STAGE_WHITE = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}

def ent(serial, recommend, desc_cn, payor, role, founded, stage,
        highlights, events, sverdict, sreason):
    s = SCORES[serial]
    return {
        "serial": serial,
        "signal_strength": SIGNAL[serial],
        "info_score": s["info"],
        "diff_score": s["diff"],
        "copy_score": s["copy"],
        "research_value": s["rv"],
        "recommend": recommend,
        "desc_cn": desc_cn,
        "payor_model": payor,
        "business_tags_role": role,
        "founded": founded,
        "stage": stage,
        "highlights": highlights,
        "events": events,
        "update_time": "2026-07-17",
        "silver_verdict": sverdict,
        "silver_reason": sreason,
    }

enterprises = []

enterprises.append(ent(
 "#0565",
 "信号最强、信息量足，差异化在于以Medicare按人头预付承接全美老年初级保健，靠主动预防压低住院率盈利；可复制性受国内商保薄弱制约——最该学的是'医保结余分润+社区诊所'的基层路径，对国内紧密型医共体有直接借鉴。",
 "Medicare按人头预付的老年社区诊所网络",
 "政府医保(Medicare)按人头预付",
 "服务商", 2012, "被收购",
 ["CVS/Optum于2023年以106亿美元收购，现运营230+中心覆盖27州",
  "唯一获AARP背书的初级保健机构，按人头承担Medicare全额风险",
  "将住院率较Medicare基准降低约51%，靠预防实现医保结余分润",
  "2025年CVS对其商誉减记57亿美元并关闭16家诊所，盈利模式存疑"],
 [{"date":"2023-05","text":"CVS Health以106亿美元完成收购"},
  {"date":"2025","text":"CVS对Oak Street商誉减记57亿美元并关闭16家诊所"}],
 "核心银发","专注Medicare老年初级保健，平均患者68岁，老年健康核心场景"))

enterprises.append(ent(
 "#0855",
 "信号强、信息量足，差异化在把上门健康评估做成由健康计划全额买单的预防入口，并新增认知筛查；可复制性受国内居家评估付费方缺位制约——最该学的是'支付方采购+上门早筛'模式，国内可对接长护险与商保做居家失能/认知评估。",
 "由健康计划买单的居家健康评估与早筛",
 "政府医保(Medicare Advantage)按人头付费",
 "服务商", 2017, "被收购",
 ["2023年3月被CVS以约80亿美元收购，并入Healthspire到家体系",
  "年上门健康评估超300万人次，由健康计划全额买单、会员免费",
  "2024年新增居家轻度认知障碍数字筛查与糖尿病Focused Visits",
  "会员满意度97%，97%的MA计划含健身/健康福利"],
 [{"date":"2023-03","text":"CVS以约80亿美元完成收购"},
  {"date":"2024-10","text":"上线居家轻度认知障碍数字筛查"}],
 "核心银发","居家健康评估与认知早筛，直接服务老年健康预防"))

enterprises.append(ent(
 "#0602",
 "信号强、信息量足，差异化在押注跨血脑屏障的阿尔茨海默病候选药与递送平台；可复制性低（重研发投入、周期长）——国内创业者难复制原研，但可学其'瞄准被低估衰老疾病+平台型递送技术'的布局思路，关注神经退行性疾病早筛与用药。",
 "押注阿尔茨海默病跨血脑屏障候选药",
 "商业保险+个人自付(处方药)",
 "产品商", 2013, "已上市",
 ["2024年10月宣布、12月完成以14亿美元收购Aliada",
  "ALIA-1758为靶向焦谷氨酸淀粉样蛋白β的抗AD抗体，处1期临床",
  "采用跨血脑屏障MODEL递送平台，主攻CNS药物递送",
  "AbbVie为大型药企，神经科学为其关键增长板块"],
 [{"date":"2024-10-28","text":"宣布14亿美元收购Aliada"},
  {"date":"2024-12-11","text":"完成收购Aliada，ALIA-1758纳入管线"}],
 "核心银发","收购的Aliada核心资产为阿尔茨海默病候选药，瞄准衰老人群神经退行性疾病"))

enterprises.append(ent(
 "#0398",
 "信号较强、信息量中，差异化在香港高端护老院舍与认知障碍主题照护，并延伸至内地医养；可复制性中等——国内可学其'院舍标准化运营+高端认知症专区'打法，但香港政府买位模式难照搬，宜结合普惠定位。",
 "香港高端护老院舍与认知障碍主题照护",
 "个人自费+香港政府买位/资助",
 "运营商", 1989, "被收购",
 ["1989年创于香港观塘，首家在港主板上市的护老集团",
  "2024年2月被华懋集团私有化退市，旗下12间院舍、1632床位",
  "拓展浙江乌镇医养项目，设认知障碍主题照护专区",
  "定位高端护老，香港政府买位/资助+个人自费"],
 [{"date":"2022-08","text":"华懋集团收购56.15%股权"},
  {"date":"2024-02-29","text":"获法院批准私有化并从港交所退市"}],
 "核心银发","香港护老院舍与认知障碍照护，银发养护核心"))

enterprises.append(ent(
 "#0593",
 "信号中等、信息量中，差异化在把老年健身做成Medicare Advantage补贴的免费福利，按人头向健康计划收费；可复制性受国内银发健身付费意愿弱制约——最该学的是'保险买单+网点+社交'降低医疗支出的闭环，国内可对接惠民保。",
 "老年健身福利，靠MA补贴向健康计划收费",
 "政府医保(Medicare Advantage)补贴+健康计划采购",
 "服务商", 1981, "被收购",
 ["Stone Point Capital于2022年以20亿美元收购，由上市公司转为私有",
  "核心资产SilverSneakers为全美领先老年健身福利，覆盖1.6万网点",
  "按会员每月向健康计划收费，参保会员医疗支出低约16%",
  "2023年收购数字健康平台Burnalong，拓展虚拟健身"],
 [{"date":"2022-06","text":"Stone Point Capital以20亿美元收购并私有化"},
  {"date":"2023-07","text":"任命Hill Ferguson为CEO"}],
 "核心银发","SilverSneakers为老年健身福利，降低长者医疗支出"))

enterprises.append(ent(
 "#0594",
 "信号中等、信息量中，差异化正是老年健身福利品牌，靠MA补贴覆盖上万网点；可复制性受国内缺乏类似补贴制约——可学其'健身即预防、保险降支出'的定位，国内可探索社区健身与商保/长护险结合的轻模式。",
 "面向长者的免费健身福利与社交网络",
 "政府医保(Medicare Advantage)补贴",
 "服务商", 1992, "被收购",
 ["1992年由Mary Swanson创立，现属Tivity/Stone Point体系",
  "面向长者免费健身福利，通过MA与健康补充险覆盖",
  "网络含1.6万健身房与老年中心，会员满意度高",
  "被视为降低医疗支出的'生活方式福利'标杆"],
 [{"date":"1992","text":"由Mary Swanson创立"},
  {"date":"2022","text":"随Tivity被Stone Point收购转为私有资产"}],
 "核心银发","面向长者的免费健身与社交福利"))

enterprises.append(ent(
 "#0595",
 "信号中等、信息量足，差异化偏弱（互联网控股集团），银发切点仅在其家庭照护撮合平台；可复制性低——国内可参考'照护者平台+雇主福利'撮合模式，但需注意护工供给与信任体系的本土搭建。",
 "互联网控股集团，老年照护撮合为银发切点",
 "B端平台抽佣+个人订阅",
 "平台", 1995, "已上市",
 ["互联网与媒体控股集团（NASDAQ:IAC），2019年以5亿美元收购Care.com",
  "Care.com为全球最大家庭照护线上撮合平台，老年照护为增长最快板块",
  "模式为B端平台抽佣+个人订阅，并设雇主Care@Work福利",
  "2026年Care.com被以3.2亿美元转售给买方财团"],
 [{"date":"2019-12-20","text":"宣布5亿美元收购Care.com"},
  {"date":"2020-Q1","text":"完成收购Care.com"},
  {"date":"2026","text":"Care.com以3.2亿美元转售买方财团"}],
 "泛医疗擦边","银发切点仅来自Care.com的老年照护撮合，母公司为互联网控股集团，主业非银发"))

enterprises.append(ent(
 "#0850",
 "信号中等、信息量中，差异化在把数字健康平台与居家照护网络打通，面向支付方/雇主/个人；可复制性中等——国内可学其'健康数据中枢+居家护理'组合，对接医保与商保做慢病与到家照护管理。",
 "数字健康平台打通居家照护网络",
 "支付方/雇主采购+个人订阅",
 "平台", 2010, "被收购",
 ["2024年10月被医疗投资机构Altaris以5.18亿美元私有化收购",
  "旗下CareLinx为居家照护平台，注册照护人员超45万",
  "MA业务快速增长，2022年新增180万会员",
  "对接雇主、支付方与个人，含数字疗法与福利导航"],
 [{"date":"2021","text":"通过SPAC上市"},
  {"date":"2024-06-21","text":"Altaris宣布5.18亿美元收购"},
  {"date":"2024-10-22","text":"完成私有化收购，退市"}],
 "核心银发","数字健康+CareLinx居家照护，覆盖老年慢病与到家护理"))

enterprises.append(ent(
 "#0012",
 "信号中等、信息量足，差异化在国内最大体检网络+Alpha风控引擎推出80岁老年医疗险，并以AI总检提效；可复制性强——国内创业者最该学其'体检数据→保险风控→定制体检'闭环，及用DeepSeek做总检一体机的降本路径。",
 "国内最大体检网络，延伸至老年医疗险",
 "个人自费+B端企业采购",
 "平台", 2015, "成长期",
 ["2015年创立于上海，国内最大体检服务平台，覆盖300+城3000+机构",
  "自研Alpha风控引擎，推出国内首款80岁可购老年医疗险",
  "AI总检一体机2025年7月商用，报告生成缩至约2分钟",
  "累计融资近10亿元，2025未来医疗100强第6，已有IPO计划"],
 [{"date":"2025-02","text":"善太医AI接入DeepSeek"},
  {"date":"2025-07","text":"AI智能总检一体机商用"},
  {"date":"2025-05-12","text":"登未来医疗100强第6"}],
 "核心银发","老年体检网络+80岁老年医疗险，深耕银发健康预防与支付"))

enterprises.append(ent(
 "#0461",
 "信号中等、信息量足，差异化在居家医疗与临终关怀双线照护网络；可复制性受国内居家照护支付与护工供给制约——可学其'居家+安宁'一体化与按服务收费，国内宜从长护险定点机构切入。",
 "居家医疗与临终关怀双线照护网络",
 "政府医保(Medicare/Medicaid)+商业保险",
 "运营商", 1982, "被收购",
 ["2025年8月被UnitedHealth/Optum以33亿美元收购并退市",
  "全美最大居家医疗与临终关怀商之一，年服务46.5万患者、覆盖38州",
  "因反垄断被要求剥离164个网点（涉及年收入5.28亿美元）",
  "居家照护成本较住院低50%–70%，契合价值医疗"],
 [{"date":"2023-06","text":"同意被UnitedHealth以33亿美元收购"},
  {"date":"2025-08-14","text":"完成收购并退市，剥离164网点"}],
 "核心银发","居家医疗与临终关怀，老年到家照护核心场景"))

enterprises.append(ent(
 "#0949",
 "信号中等、信息量足，差异化在覆盖多州的家庭医疗与临终关怀网络，与医院系统共建到家能力；可复制性受支付与并购门槛制约——可学其'居家+社区+院后'整合与院企共建模式，国内可对接县域医共体。",
 "家庭医疗与临终关怀的到家照护网络",
 "政府医保(Medicare/Medicaid)+商业保险",
 "运营商", 1994, "被收购",
 ["2023年2月被UnitedHealth/Optum以54亿美元收购并退市",
  "覆盖37州与华盛顿特区，年患者接触超1200万次",
  "居家医疗+临终关怀+社区照护，与医院系统共建网点",
  "成为Optum到家医疗能力的核心基座"],
 [{"date":"2022-03","text":"UnitedHealth宣布54亿美元收购"},
  {"date":"2023-02-22","text":"完成收购并退市"}],
 "核心银发","家庭医疗与临终关怀，老年居家照护网络"))

enterprises.append(ent(
 "#0954",
 "信号中等、信息量中，差异化在居家健康与临终关怀双线上市规模，靠Medicare/Medicaid与服务收费；可复制性受国内支付结构制约——可学其'居家医疗+安宁疗护'轻重结合与精细化运营，国内可从安宁疗护试点切入。",
 "居家健康与临终关怀双线上市运营商",
 "政府医保(Medicare/Medicaid)+商业保险+服务收费",
 "运营商", 2014, "已上市",
 ["2022年从Encompass分拆在纽交所上市（EHAB）",
  "覆盖34州，约255个居家护理点与112个临终关怀点",
  "2025年Q1净收入1780万美元，临终关怀板块连续增长",
  "居家医疗靠Medicare/Medicaid与服务收费，非MA占比提升"],
 [{"date":"2022","text":"从Encompass分拆在纽交所上市"},
  {"date":"2025-03-04","text":"发布2024Q4财报，临终关怀连续增长"}],
 "核心银发","居家健康与临终关怀双线，老年到家与安宁疗护"))

# ---- 标签审查（仅输出建议，不写回库） ----
tag_review = [
 {"serial":"#0565","name":"Oak Street Health",
  "intro":"专注Medicare老年群体的按人头预付式初级保健连锁诊所，2023年被CVS/Optum收购，靠主动预防压低住院率并分享医保结余。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["诊所"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[]},
 {"serial":"#0855","name":"Signify Health",
  "intro":"由健康计划全额买单的居家健康评估平台，2023年被CVS收购，近年新增认知与慢病上门早筛。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["居家医疗"],"business_tags":{"customer":"B2B","role":"服务商(媒体/数据)","channel":[]}},
  "suggested":[]},
 {"serial":"#0602","name":"AbbVie",
  "intro":"大型生物制药企业，2024年收购Aliada获得跨血脑屏障的阿尔茨海默病候选药与CNS递送平台。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["药品"],"business_tags":{"customer":"B2B","role":"制造商(药)","channel":[]}},
  "suggested":[{"action":"change","tag":"医药(神经/退行性疾病)","reason":"该公司为生物制药企业，收购Aliada获阿尔茨海默病候选药，原'消费品'标签明显错位"}]},
 {"serial":"#0398","name":"松龄护老",
  "intro":"1989年创于香港的护老院运营商，曾为港主板首家上市护老集团，2024年被华懋集团私有化。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["远程医疗"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[{"action":"change","tag":"院舍照护(护老院)","reason":"实为香港护老院舍运营商，原'远程医疗'标签与其业务完全不符"}]},
 {"serial":"#0593","name":"Tivity Health",
  "intro":"以SilverSneakers老年健身福利为核心的健康生活方式公司，2022年被Stone Point私有化收购。",
  "old_tags":{"tag_l1":["文娱社交"],"tag_l2":["健身"],"business_tags":{"customer":"B2C","role":"服务商","channel":[]}},
  "suggested":[]},
 {"serial":"#0594","name":"SilverSneakers",
  "intro":"创立于1992年的老年免费健身与社交福利品牌，现属Tivity/Stone Point体系，覆盖全美上万网点。",
  "old_tags":{"tag_l1":["文娱社交"],"tag_l2":["健身"],"business_tags":{"customer":"B2C","role":"服务商","channel":[]}},
  "suggested":[]},
 {"serial":"#0595","name":"IAC",
  "intro":"互联网与媒体控股集团（NASDAQ:IAC），2019年收购家庭照护撮合平台Care.com切入银发照护。",
  "old_tags":{"tag_l1":["行业服务"],"tag_l2":["养老信息平台"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":["线上"]}},
  "suggested":[{"action":"change","tag":"家庭照护(照护者撮合)","reason":"IAC通过Care.com做家庭照护线上撮合，原'养老信息平台'不够准确，应为照护者撮合平台"}]},
 {"serial":"#0850","name":"Sharecare",
  "intro":"数据驱动的数字健康平台，拥有居家照护网络CareLinx，2024年被Altaris私有化收购。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["慢病管理"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[]},
 {"serial":"#0012","name":"善诊",
  "intro":"2015年创立于上海的国内最大体检服务平台，以体检数据衍生老年医疗险并以AI提效。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["体检筛查"],"business_tags":{"customer":"B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"健康服务","reason":"善诊为体检与健康服务平台，原'消费品'标签明显错位"}]},
 {"serial":"#0461","name":"Amedisys",
  "intro":"全美领先的居家医疗与临终关怀提供商，2025年被UnitedHealth/Optum收购并退市。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["居家护理"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
  "suggested":[]},
 {"serial":"#0949","name":"LHC Group",
  "intro":"覆盖多州的家庭医疗保健与临终关怀服务商，2023年被UnitedHealth/Optum以54亿美元收购。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["安宁疗护"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[]},
 {"serial":"#0954","name":"Enhabit",
  "intro":"2022年从Encompass分拆、在纽交所上市的居家健康与临终关怀双线运营商。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["临终关怀"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[]},
]

nonsilver = [
 {"serial":"#0595","name":"IAC","verdict":"泛医疗擦边",
  "reason":"银发相关性仅来自其旗下Care.com的老年照护撮合业务，母公司IAC为互联网/媒体控股集团，主业并非银发经济"}
]

# ---- 自检 ----
FORBID_ROUND = ["融资","轮","收购价","亿美","亿元","万美元","IPO","SPAC","估值"]
errors = []
for e in enterprises:
    ser = e["serial"]
    rec = e["recommend"]
    # 四维 0-10
    for k in ("info_score","diff_score","copy_score"):
        v = e[k]
        if not (0 <= v <= 10):
            errors.append(f"{ser}: {k}={v} 超出0-10")
    rv = e["research_value"]
    if not (0 <= rv <= 100):
        errors.append(f"{ser}: research_value={rv}")
    # recommend 长度 60-120 中文字
    n = len(rec)
    if not (60 <= n <= 120):
        errors.append(f"{ser}: recommend 长度={n} (需60-120)")
    # recommend 含禁用词（企业名/融资轮次/成立年份）
    for nm in NAMES[ser]:
        if nm.lower() in rec.lower():
            errors.append(f"{ser}: recommend 含企业名 '{nm}'")
    if "成立于" in rec:
        errors.append(f"{ser}: recommend 含 '成立于'")
    # 成立年份数字（4位）
    import re
    if re.search(r"19\d\d|20\d\d", rec):
        errors.append(f"{ser}: recommend 含年份数字")
    # stage 白名单
    if e["stage"] not in STAGE_WHITE:
        errors.append(f"{ser}: stage='{e['stage']}' 不在白名单")
    # payor 非空
    if not e["payor_model"] or e["payor_model"] in ("未披露",):
        errors.append(f"{ser}: payor_model 为空/未披露")
    # 全字段非空
    for k,v in e.items():
        if v is None or v == "" or v == [] :
            errors.append(f"{ser}: 字段 {k} 为空")
    # desc_cn <=30
    if len(e["desc_cn"]) > 30:
        errors.append(f"{ser}: desc_cn 长度={len(e['desc_cn'])} >30")

if errors:
    print("=== 自检未通过 ===")
    for x in errors:
        print(" -", x)
else:
    print("=== 自检全部通过 ===")
    out = {"batch":0, "enterprises":enterprises, "tag_review":tag_review, "nonsilver":nonsilver}
    with open(OUT,"w",encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("已写出:", OUT)
    print("企业数:", len(enterprises), "| tag_review:", len(tag_review), "| nonsilver:", len(nonsilver))
    for e in enterprises:
        print(f"  {e['serial']} recommend({len(e['recommend'])}字) stage={e['stage']} payor={e['payor_model'][:12]} verdict={e['silver_verdict']}")
