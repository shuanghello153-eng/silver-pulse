# -*- coding: utf-8 -*-
"""
selection/recommend.py — 推荐理由重算（T24 + T30）。

每天跑批时，对 scored_latest.json 中每一条资讯重算推荐理由：
  - 去掉"X事件"冗余前缀（标题/摘要已含事件词就不重复）
  - 金额只在标题/摘要没出现过时才带（避免"标题说10亿、理由又说10亿"）
  - 带入 entity_name / 领域 / 反常识度，做差异化模板（融资/收购/IPO/政策/产品/其他）
  - 零 AI 成本（纯关键词模板），放在 reapply_centrality 之后，
    此时 entity_name / 领域 / 反常识度 字段已就位，理由更准。

这是 Loop 哲学的一部分：推荐理由每次跑批都会变得更好，而不是写死一次。
"""
import json
import os
import re
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORED_LATEST_PATH = os.path.join(DATA_DIR, "scored_latest.json")

# 国内参照模板（按事件/领域差异化）— 每类 3–5 变体，随机选择降重复率
# 格式: {事件类型: [变体1, 变体2, ...]}
# 零模型成本，纯关键词拼接 + 随机化。
CHINA_REF_VARIANTS = {
    "融资": [
        "中国银发企业可参照其融资节奏与估值逻辑，关注同赛道国内玩家。",
        "从融资节奏看，国内同类赛道的估值与资本偏好值得对标。",
        "此轮融资释放的信号：该细分方向正吸引资本关注，国内可对照看。",
        "海外银发赛道融资活跃度是国内市场温度的先行指标。",
        "资本用真金白银投票的方向，国内创业者可重点跟踪。",
    ],
    "收购并购": [
        "美国银发赛道并购活跃，中国创业者可关注被并购方的产品能力是否可引入国内。",
        "并购整合往往意味着赛道进入成熟期，国内可提前布局互补能力。",
        "被并购方的技术/渠道/品牌价值，对中国银发市场有直接借鉴意义。",
        "跨国并购案例揭示的定价逻辑，可作为国内投融资参考坐标。",
        "收购方的战略意图，往往预示着下一阶段行业竞争焦点。",
    ],
    "IPO上市": [
        "海外银发企业上市路径值得研究，国内同类企业可参考其商业模式与合规框架。",
        "IPO 企业的招股书是免费的行业深度研究报告，建议精读其风险因素章节。",
        "公开市场的定价锚点，对未上市银发企业的估值有参照意义。",
        "从 IPO 路演材料中可提取出资本市场最关心的银发赛道命题。",
        "上市公司的财报透明度高，可持续跟踪验证其商业模式是否跑通。",
    ],
    "战略合作": [
        "战略合作往往预示生态卡位，中国创业者可思考同类联盟机会。",
        "跨界合作揭示的能力互补模式，国内可寻找类似组合机会。",
        "大厂入局的战略合作信号值得关注，往往意味着赛道即将爆发。",
        "战略联盟的分工方式，可供国内银发生态建设参考。",
        "合作双方的资源禀赋差异，暗示了行业的关键瓶颈在哪里。",
    ],
    "产品发布": [
        "新产品发布揭示用户需求演进，国内团队可对照自身产品路线图。",
        "海外新品的功能定义和定价策略，是国内产品经理的免费教材。",
        "产品迭代方向反映用户痛点迁移，国内团队应保持同步敏感度。",
        "从新品发布的市场反馈，可预判国内同类需求的成熟时间窗口。",
        "新产品的技术路径选择，对国产化方案有直接参考价值。",
    ],
    "政策法规": [
        "海外政策变动是中国政策的先行指标，长护险/支付端改革可提前研判。",
        "政策红利期的国际经验表明，支付方变革将重塑整个产业链格局。",
        "监管沙盒或试点政策的海外实践，可为国内政策设计提供参照。",
        "CMS/Medicare 政策调整往往是全球银发支付体系的风向标。",
        "法规变化暴露出的行业痛点，正是创新企业的机会窗口。",
    ],
    "居家养老": [
        "居家养老是中美共同主战场，服务模式差异值得深度对标。",
        "居家照护的人力模型和盈利难点，国内同行可直接借鉴。",
        "海外居家养老的技术赋能手段（远程监测/AI辅助），国内可加速引入。",
        "居家场景的产品服务一体化趋势，国内有供应链优势可放大。",
        "从上门服务到社区嵌入的模式演进，国内正处于类似阶段。",
    ],
    "养老地产": [
        "养老地产存量改造经验对中国大量老旧设施有参考价值。",
        "海外 CCRC 模式的运营数据，是国内养老地产投资的重要参照。",
        "存量资产转型养老的国际经验，对国内城市更新有实操意义。",
        "医养结合在物业空间层面的落地方式，国外已有成熟样板。",
    ],
    "认知症": [
        "认知症照护是刚需赛道，海外照护模式可为中国家庭提供范本。",
        "认知症专业照护的人才培养体系，国内尚处早期可快速引进。",
        "非药物干预技术的临床证据积累，国内外几乎站在同一起跑线。",
        "认知症家庭的付费意愿和能力，决定了商业模式的可行性边界。",
    ],
    "数字疗法": [
        "数字疗法/远程医疗的支付与落地模式，中国可少走弯路。",
        "数字疗法的循证要求和 FDA 路径，国内出海企业需提前布局。",
        "远程患者管理（RPM）的医保支付试点经验，值得持续跟踪。",
        "数字健康产品的用户依从性设计，海内外面临相似挑战。",
    ],
    "保险科技": [
        "保险科技降低银发风险成本，国内长护险商业化可借鉴。",
        "长寿风险管理（longevity risk）的创新工具，保险科技公司正在重新定义。",
        "UBI（基于使用行为）保险模式在银发群体的适用性，海外已有探索。",
        "保险+服务的闭环模式，可能是国内长护险商业化破局点。",
    ],
    "健康服务": [
        "护理人力是共性瓶颈，海外用工模式对中国有参照意义。",
        "医护人员的职业路径设计和薪酬激励，直接影响服务质量稳定性。",
        "连锁化vs本土化的健康服务模式之争，海外数据可提供决策依据。",
        "健康服务的人力成本结构，决定了中国市场的定价天花板。",
    ],
    "康复设备": [
        "康复辅具国产化空间大，海外产品定义值得研究。",
        "康复机器人的临床落地进度，国内外差距正在缩小。",
        "辅具租赁模式的国际经验，对降低国内用户门槛有启发。",
        "康复设备的医保/商保覆盖路径，海外先行者已探明部分路线。",
    ],
    "养老用品": [
        "智能硬件+服务是趋势，国内供应链优势可放大。",
        "老年消费电子的产品力定义，海外品牌仍在摸索中。",
        "适老化设计的细节体验，国内外用户反馈高度一致。",
        "银发用品的渠道策略（电商/DTC/线下），各有成败案例可研究。",
    ],
    "长寿科技": [
        "长寿科技是长期赛道，早期布局者值得跟踪。",
        "衰老生物学的基础研究突破，正在向应用转化加速推进。",
        "长寿赛道的投资回报周期极长，需要区分科学进展和商业炒作。",
        "从抗衰成分到检测设备，产业链各环节都有早期机会。",
    ],
    "智慧养老": [
        "AI+养老的落地场景，国内可结合本地数据优势。",
        "智慧养老的核心不在技术而在场景定义，海外试错成本已被付出。",
        "传感器+AI 的跌倒检测/健康监测方案，国内外产品力接近。",
        "养老机构的数字化管理系统（EHR/运营SaaS），国内替代空间巨大。",
    ],
    "行业趋势": [
        "行业报告揭示结构性机会，可作为选题地图。",
        "宏观趋势数据中的微观机会点，值得拆解为具体选题方向。",
        "跨行业的银发渗透案例，往往隐藏着尚未被发现的蓝海。",
        "行业集中度的变化趋势，揭示了哪些细分正在走向整合。",
        "头部企业的战略动向，是判断行业下一个风口的最佳线索。",
    ],
}

# 兼容旧接口：CHINA_REF[key] 返回第一个变体（不随机）
CHINA_REF = {k: v[0] for k, v in CHINA_REF_VARIANTS.items()}


def detect_amount(text):
    """Extract funding amount if present."""
    if not text:
        return ""
    patterns = [
        r"\$\s?([\d.]+(?:\s?[mb])?\s?(?:million|billion|m|b)?)",
        r"([\d.]+\s?(?:亿|万)\s?(?:元|美元|人民币)?)",
        r"(\d+\.?\d*\s?(?:亿|万)\s?(?:美元|人民币|元)?)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


def gen_recommendation(article, tags, entity_name="", domains=None, novelty=0, _seen=None):
    """生成差异化、去冗余的推荐理由。

    Args:
        _seen: dict[str, int] 可选的已见计数器 {模板前缀: 使用次数}，
              调用方传入可在批次内做去重（同模板最多用 2 次强制换）。
    """
    if _seen is None:
        _seen = {}
    if domains is None:
        domains = []
    title = (article.get("title_cn") or article.get("title") or "")
    summary = (article.get("summary") or article.get("summary_cn")
               or article.get("raw_content") or "")
    blob = (title + " " + summary)
    blob_low = blob.lower()
    primary = tags[0] if tags else "行业趋势"
    amount = detect_amount(blob)
    has_amount = bool(amount) and (amount.lower() in blob_low)

    # 事件词是否已出现在标题/摘要（避免"X事件"冗余前缀）
    kw_map = {
        "融资": ["融资", "a轮", "b轮", "c轮", "天使轮", "series", "raises",
                  "funding", "获投", "获融", "本轮", "轮融资", "战略融资"],
        "收购并购": ["收购", "并购", "acqui", "merge", "被收购", "买下"],
        "IPO上市": ["ipo", "上市", "goes public", "敲钟", "挂牌", "公开募股"],
        "政策法规": ["政策", "法规", "medicare", "medicaid", "cms", "fda",
                     "长护险", "指引", "管理办法", "条例"],
        "产品发布": ["发布", "上线", "推出", "launch", "unveil", "debut", "首发", "新品"],
    }
    event_visible = any(k in blob for k in kw_map.get(primary, []))

    subj = (entity_name or "").strip()
    # 无 entity 时用领域/具体标签作主语，避免大量条目理由雷同（仍以真实话题为锚）
    if not subj and domains:
        subj = domains[0]
    if not subj and len(tags) > 1:
        subj = tags[1]

    # 事件洞察（差异化模板）
    if primary == "融资":
        if has_amount:
            insight = "本轮融资 %s，资本正加码" % amount
        else:
            insight = "新一轮融资落地，资本正加码"
        dom = domains[0] if domains else ""
        insight += (dom + "赛道") if dom else "银发赛道"
        insight += "；"
    elif primary == "收购并购":
        insight = "并购整合加速，" if not event_visible else "这笔交易显示行业整合加速，"
    elif primary == "IPO上市":
        insight = "走向公开市场的信号，" if not event_visible else "登陆资本市场，"
    elif primary == "政策法规":
        insight = "政策端出现新动向，" if not event_visible else "新规落地，"
    elif primary == "产品发布":
        insight = "新产品/服务上线，" if not event_visible else "新品亮相，"
    else:
        insight = ""

    # 组装
    head = (subj + "：" if subj else "") + insight
    head = head.rstrip("，")
    # 随机选变体 + 去重（同类型模板最多用 2 次后强制换下一个变体）
    variants = CHINA_REF_VARIANTS.get(primary, CHINA_REF_VARIANTS["行业趋势"])
    usage_key = primary
    used_count = _seen.get(usage_key, 0)
    idx = min(used_count // 2, len(variants) - 1)
    offset = random.randint(0, min(1, len(variants) - idx - 1))
    chosen_idx = min(idx + offset, len(variants) - 1)
    ref = variants[chosen_idx].rstrip("。")
    _seen[usage_key] = used_count + 1
    parts = [p for p in (head, ref) if p]
    if novelty and novelty >= 6:
        parts.append("此事反常识，适合做差异化切入")
    rec = "。".join(parts)
    if rec and not rec.endswith("。"):
        rec += "。"
    return rec


def run_daily_step():
    """重算 scored_latest.json 全部条目的 recommendation（及 tags/event/domains 回写）。"""
    if not os.path.exists(SCORED_LATEST_PATH):
        print("[recommend] scored_latest.json 不存在，跳过")
        return
    try:
        from generator import classify_event_type, classify_domain
    except Exception:
        # 兜底：若 generator 不可导入，用最简分类
        def classify_event_type(t, s, tags):
            return "行业趋势"
        def classify_domain(t, s, tags):
            return []
    with open(SCORED_LATEST_PATH, "r", encoding="utf-8") as f:
        arts = json.load(f)
    n = 0
    _seen = {}  # 批次内去重计数器
    for art in arts:
        title = (art.get("title_cn") or art.get("title") or "")
        summary = (art.get("summary") or art.get("summary_cn")
                   or art.get("raw_content") or "")
        tags = art.get("tags") or []
        event_type = classify_event_type(title, summary, tags)
        domains = classify_domain(title, summary, tags)
        # 带上 event_type 进 tags 首位（与 score_and_merge 行为一致，便于展示）
        if event_type not in tags and len(tags) < 5:
            tags = [event_type] + tags
        entity = art.get("entity_name", "") or ""
        try:
            novelty = float(art.get("novelty") or 0)
        except Exception:
            novelty = 0
        rec = gen_recommendation(art, tags, entity, domains, novelty, _seen=_seen)
        art["recommendation"] = rec
        art["tags"] = tags
        art["event_type"] = event_type
        art["domains"] = domains
        n += 1
    with open(SCORED_LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(arts, f, ensure_ascii=False, indent=2)
    print("[recommend] 重算推荐理由完成：%d 条" % n)


if __name__ == "__main__":
    run_daily_step()
