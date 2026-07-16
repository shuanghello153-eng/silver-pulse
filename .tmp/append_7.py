# -*- coding: utf-8 -*-
import json, os

base = r"G:\workbuddy\2026-06-28-23-34-20\silver-pulse\.tmp"
batch_path = os.path.join(base, "batches", "batch_7.json")
result_path = os.path.join(base, "results", "result_7.json")

with open(batch_path, encoding="utf-8") as f:
    batch = json.load(f)
batch_names = [b["name"] for b in batch]

with open(result_path, encoding="utf-8") as f:
    results = json.load(f)

existing_names = set(r["name"] for r in results)

new_entries = [
 {
  "name": "GroundGame Health/SameSky Health",
  "desc_cn": "2024 年由 GroundGame.Health 与 SameSky Health 合并而成，专注通过文化适配的外展与在地人际关系，为健康险/MCO/社区组织(CBO)闭环解决健康相关的社会需求(SDOH)与照护缺口。其 HITRUST 认证平台连接难以触达的会员与社区服务，已满足 18 万+ 社会需求、触达 280 万+ 会员，覆盖全美 50 州；合并后获 7wireVentures 领投 1,700 万美元 A 轮。",
  "tag_l2": ["SDOH"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Grow Therapy",
  "desc_cn": "行为/心理健康平台，连接求助者、治疗师与健康险，让客户按保险、地区、专科筛选并预约心理咨询、精神科与用药管理（含青少年/儿童）。拥有 2.6 万+ 经过审核的治疗师，接入 125+ 健康险计划，覆盖全美 50 州并提供线上与线下服务；同时面向雇主与健康计划提供 EAP/保险无缝对接的福利方案。",
  "tag_l2": ["心理健康"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Hamilton Health Box",
  "desc_cn": "以可快速部署的微型诊所(microclinic™)为运营模式的初级医疗公司（2020 年成立于休斯顿），面向农村、城市弱势人群及雇主/职场提供基础医疗。提供全套现场诊所、移动诊所与混合式(线下+远程)照护，含初级/急诊/慢病管理、化验、精神健康、X 光；宣称 60 天内即可落地，已融资约 1,250 万美元。",
  "tag_l2": ["诊所"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "HarmonyCares",
  "desc_cn": "美国规模最大的按价值付费居家初级医疗（上门问诊/house call）提供商之一，服务 Medicare 及病情复杂的老年患者。在 15 个州服务 7 万+ 患者，由 175+ 初级医疗医生领衔、含护理经理/社工/药师的跨学科团队上门服务，并附姑息治疗、放射与化验；2024 年获 General Catalyst 等 2 亿美元融资。",
  "tag_l2": ["居家医疗"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "HealthArc",
  "desc_cn": "面向医疗机构/支付方/雇主的统一虚拟照护与远程患者监测(RPM)+慢病管理(CCM)平台，连接 40+ 款蜂窝/蓝牙医疗设备，以 AI 临床路径与自动化工作流覆盖 RPM/CCM/PCM/RTM/TCM 并自动生成 CPT 计费报告。已覆盖 40+ 州、750+ 机构、6.5 万+ 患者，符合 HIPAA/SOC2、采用 FDA 认证设备。",
  "tag_l2": ["慢病管理", "可穿戴监测"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "HealthSnap",
  "desc_cn": "一体化虚拟照护管理(VCM)平台，以集成 RPM 与 CCM/PCM 帮助机构远程管理高血压、糖尿病、肥胖等慢病。其专利资格报告与计费工具简化报销，可对接 80+ 套 EHR；已与 150+ 医疗系统合作、覆盖 33 州、远程管理 10 万+ 患者，获 HITRUST 认证并入选 2025 Inc.5000。",
  "tag_l2": ["慢病管理", "可穿戴监测"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Homeage",
  "desc_cn": "新加坡起家的按需居家照护平台（亦覆盖马来西亚、澳大利亚），用专有算法将 6,000+ 名在地持证照护人员/护士/治疗师匹配到长者家中，通过 App 预约、管理与支付。服务含居家个人照护、居家护理（鼻饲/尿管等）及家访康复（PT/OT/言语），成立于 2016 年，C 轮获淡马锡领投 3,000 万美元。",
  "tag_l2": ["护工平台", "居家护理"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Imperative Care",
  "desc_cn": "商业化阶段的医疗器械公司（加州 Campbell），聚焦中风与血管血栓清除。核心产品为 Zoom 中风系统（用于缺血性中风的抽吸导管）、Symphony（静脉血栓栓塞）与 Prodigy（急性肢体缺血）血栓清除系统，并研发 Telos 血管内机器人平台；多次获 FDA 许可。注意：并非投资机构。",
  "tag_l2": ["医疗器械"],
  "confidence": "high",
  "note": "原标签'产业基金'错误——Imperative Care 是医疗器械公司，非投资机构。"
 },
 {
  "name": "In-House Health",
  "desc_cn": "面向医院护理团队的 AI 人力调度 SaaS（2023 年成立于丹佛），用机器学习预测床位护理与排班需求，以灵活的院内护士抢班/排班工具替代外部中介派遣，提升护士掌控感与留任。获 NEA、TMV、Longevity Venture Partners 等 400 万美元种子轮；并非远程护理交付。",
  "tag_l2": ["养老软件"],
  "confidence": "med",
  "note": "实为医院护理排班/人力优化 SaaS，词表无精确对应，取'养老软件'近似（属医疗信息化软件）。"
 },
 {
  "name": "InHome Therapy",
  "desc_cn": "2021 年成立于宾州 King of Prussia，业内首个'居家治疗即服务'(HTaaS)供应商，为全美居家照护机构外包上门物理/作业/言语治疗。拥有 600+ 治疗师、350+ 机构合作伙伴、累计 250 万+ 次访视，以 R.I.S.E. 项目做治疗师招聘培训与留存；获 TT Capital Partners 领投 2,200 万美元+ 融资。",
  "tag_l2": ["居家康复", "康复医疗"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "K4Connect",
  "desc_cn": "面向养老社区（独立/协助/记忆照护）的 AgeTech SaaS 公司（2013 年成立于北卡 Raleigh）。旗舰产品 K4Community 与 FusionOS 整合智能家居/IoT、互联健康与社交参与，提供居民签到、语音(Alexa)控制、家属连接与运营数据洞察，已服务 15,000+ 居民、75+ 社区，累计融资 2,700 万美元+。",
  "tag_l2": ["适老化", "养老软件"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Kemtai",
  "desc_cn": "基于计算机视觉的数字化康复/运动治疗平台，无需穿戴设备，仅凭摄像头即可追踪 113 个身体关键点并提供实时动作纠错反馈，为 PT/肌骨/神经/慢病康复提供 2,000+ 训练动作、提升居家依从性；获 FDA 列名与 CE 认证，以 B2B API 及 Kemtai Care App 服务医疗机构与数字健康平台。",
  "tag_l2": ["康复医疗"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Kinto",
  "desc_cn": "美国家属照护支持平台（RSV Opco 5, Inc. d/b/a Kinto），为照护年迈父母等家人的照护者提供 App+专属照护教练+虚拟互助小组，协助记录照护笔记、安排预约、协调服务与存储文档。注意：与丰田出行品牌 KINTO（车辆订阅/共享）并非同一公司。",
  "tag_l2": ["照护支持"],
  "confidence": "med",
  "note": "可能与丰田 KINTO 出行品牌混淆；此处指 kinto.care，美国家属照护支持平台。"
 },
 {
  "name": "Kismet",
  "desc_cn": "澳大利亚数字照护生态平台（2023 年墨尔本成立，Kismet Participant），连接受护者、照护者、健康保险与服务机构，覆盖居家/残障/老龄人群；将 3.5 万+ 服务商按距离/评分/价格排序并自动匹配用户保险或 NDIS 计划，可即时预约，定位软件+医疗+电商+支付交汇。获 Prosus、Airtree 领投 1,080 万澳元。",
  "tag_l2": ["养老信息平台", "护工平台"],
  "confidence": "high",
  "note": ""
 },
 {
  "name": "Koda Health",
  "desc_cn": "AI 增强的预先/严重疾病照护规划(ACP)平台（Koda Healthcare，德州），通过数字平台+临床支持(KodaCares)帮助患者生成合法、符合本州要求的医疗意愿/目标照护指令，并与 Epic 等 EMR 集成。宣称可将临终住院降低 79%，服务 Cigna、Privia、Memorial Hermann 等，获 700 万美元 A 轮。",
  "tag_l2": ["安宁疗护"],
  "confidence": "med",
  "note": "实为预先护理计划(ACP)/严重疾病照护规划平台，词表无精确对应，取'安宁疗护'近似（均属临终/照护意愿范畴）。"
 },
]

# Validate no duplicate names among new entries and against existing
for e in new_entries:
    if e["name"] in existing_names:
        raise SystemExit(f"DUPLICATE name already in result: {e['name']}")
    if e["name"] not in batch_names:
        raise SystemExit(f"name not in batch_7.json: {e['name']}")

results.extend(new_entries)

# Final validation
assert len(results) == 39, f"Expected 39, got {len(results)}"
names = [r["name"] for r in results]
assert len(set(names)) == len(names), "Duplicate names found"
for n in names:
    assert n in batch_names, f"name not in batch: {n}"

with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("OK: wrote", len(results), "entries")
print("confidence distribution:", {c: sum(1 for r in results if r["confidence"]==c) for c in ("high","med","low")})
