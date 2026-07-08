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
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORED_LATEST_PATH = os.path.join(DATA_DIR, "scored_latest.json")

# 国内参照模板（按事件/领域差异化）
CHINA_REF = {
    "融资": "中国银发企业可参照其融资节奏与估值逻辑，关注同赛道国内玩家。",
    "收购": "美国银发赛道并购活跃，中国创业者可关注被并购方的产品能力是否可引入国内。",
    "IPO上市": "海外银发企业上市路径值得研究，国内同类企业可参考其商业模式与合规框架。",
    "战略合作": "战略合作往往预示生态卡位，中国创业者可思考同类联盟机会。",
    "产品发布": "新产品发布揭示用户需求演进，国内团队可对照自身产品路线图。",
    "政策法规": "海外政策变动是中国政策的先行指标，长护险/支付端改革可提前研判。",
    "居家养老": "居家养老是中美共同主战场，服务模式差异值得深度对标。",
    "养老地产": "养老地产存量改造经验对中国大量老旧设施有参考价值。",
    "认知症": "认知症照护是刚需赛道，海外照护模式可为中国家庭提供范本。",
    "数字疗法": "数字疗法/远程医疗的支付与落地模式，中国可少走弯路。",
    "保险科技": "保险科技降低银发风险成本，国内长护险商业化可借鉴。",
    "健康服务": "护理人力是共性瓶颈，海外用工模式对中国有参照意义。",
    "康复设备": "康复辅具国产化空间大，海外产品定义值得研究。",
    "养老用品": "智能硬件+服务是趋势，国内供应链优势可放大。",
    "长寿科技": "长寿科技是长期赛道，早期布局者值得跟踪。",
    "智慧养老": "AI+养老的落地场景，国内可结合本地数据优势。",
    "行业趋势": "行业报告揭示结构性机会，可作为选题地图。",
}


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


def gen_recommendation(article, tags, entity_name="", domains=None, novelty=0):
    """生成差异化、去冗余的推荐理由。"""
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
    ref = CHINA_REF.get(primary, CHINA_REF["行业趋势"])
    parts = [p for p in (head, ref.rstrip("。")) if p]
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
        rec = gen_recommendation(art, tags, entity, domains, novelty)
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
