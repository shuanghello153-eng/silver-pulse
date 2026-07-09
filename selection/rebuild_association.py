# -*- coding: utf-8 -*-
"""
selection/rebuild_association.py — 企业-资讯关联重建（T40）。

问题：1130 家企业里 related_news_ids 全为空，导致
  事件簇对照卡 / 近期有动态排序 / 匹配资讯数排序 全部失效。

做法（反向匹配：对企业，找它在 scored_latest.json 里被哪些新闻提到/覆盖）：
  1) 强匹配（高准）：企业 name / name_cn 出现在新闻标题或正文中；
     或新闻 entity_name 精确等于企业 name。
  2) 主题匹配（中准，标题级，宁缺毋滥）：用企业 tags + business_model_cn
     里"非泛化"的关键词短语，在【新闻标题】中出现即视为覆盖。关键词须
     长度>=2 且不在泛化黑名单里，且只匹配标题（标题精炼、误命中率低）。
     典型价值：一条"养老机器人融资"新闻，除了点名的企业，还能关联到
     其它带"机器人"标签的企业 —— 这正是事件簇对照卡想要的"同事件企业群"。

原则：
  - 不编造：只写确实命中的新闻 url。
  - 多对多：一条新闻可关联多家企业，一家企业可关联多条新闻。
  - 写入 enterprise_scores.json[serial]["related_news_ids"]（list[url]），
    与 gen_enterprise.py 的 news_map.get(rid) 消费方式一致。
  - 只动 enterprise_scores.json 的 related_news_ids 字段；不动 all_enterprises.json。

运行：
  python selection/rebuild_association.py            # 落盘（写前自动备份）
  python selection/rebuild_association.py --dry      # 只统计不写盘
"""
import os
import sys
import re
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
ENT_PATH = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
SCORES_PATH = os.path.join(DATA_DIR, "enterprise", "enterprise_scores.json")

# 泛化黑名单：这些词作为关键词会过度匹配（几乎每篇银发新闻都含），必须剔除。
# 只剔除"确切等于下列短语"的标签/关键词；包含这些词的更长短语（如"居家养老"）
# 不受限，因为更长短语有区分度。
GENERIC = {
    "银发", "银发经济", "养老", "养老服务", "老年", "老龄化", "老龄",
    "健康", "健康服务", "医疗", "医疗服务", "科技", "科技创新", "科学技术",
    "智能", "智能化", "智慧", "数字化", "数字", "数据", "大数据",
    "投资", "融资", "有融资", "行业", "行业媒体", "行业服务", "产业",
    "服务", "平台", "互联网", "在线", "消费", "消费电子", "护理", "生活",
    "社区", "创新", "企业", "企业服务", "公司", "集团", "研究院", "实验室",
    "中心", "解决方案", "运营商", "提供商", "软件", "系统", "设备", "硬件",
    "网络", "云", "人工智能", "AI", "趋势", "市场", "用户", "产品",
    "中国", "美国", "国内", "海外", "全球", "经济", "信息", "咨询",
    "管理", "技术", "业务", "综合", "其他", "未知", "通用", "标准",
}

# 允许的 2 字高区分度关键词白名单（否则默认要求长度>=3）
DISTINCTIVE_2 = {
    "陪诊", "陪伴", "认知", "康复", "保险", "康养", "照护", "护理",
    "助听", "助行", "助浴", "养老",  # 养老单字被 GENERIC 拦，这里不再放
}


def _clean_tokens(values):
    """从标签/业务模式串里抽取非泛化关键词短语。"""
    out = []
    for v in values:
        if not v:
            continue
        # 按常见分隔符切分
        for part in str(v).replace("/", " ").replace("、", " ").replace(
                ",", " ").replace(";", " ").split():
            part = part.strip()
            if not part:
                continue
            if part in GENERIC:
                continue
            # 长度门槛：中文>=3，或白名单里的2字，或含字母的英文词>=2
            has_cjk = any("\u4e00" <= c <= "\u9fff" for c in part)
            if has_cjk:
                if len(part) >= 3 or part in DISTINCTIVE_2:
                    out.append(part)
            else:
                if len(part) >= 2:
                    out.append(part.lower())
    # 去重
    seen = set()
    uniq = []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def _is_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)


def _kw_in_text(kw, text_low):
    """中文关键词：子串匹配（标题已足够精炼）。
    英文关键词：整词边界匹配，避免 'st'/'ot'/'ces' 误命中 Services/State 等。"""
    if _is_cjk(kw):
        return kw in text_low
    # 英文：\b 边界（大小写已在抽取时 lower）
    return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", text_low) is not None


def _match_enterprise_news(ent, news_list):
    """返回 (matched_urls, match_types_set)。"""
    name = (ent.get("name") or "").strip()
    name_cn = (ent.get("name_cn") or "").strip()
    keywords = _clean_tokens(
        (ent.get("tags") or []) + [ent.get("business_model_cn") or ""]
    )
    name_low = name.lower()
    hits = {}  # url -> set(types)
    for n in news_list:
        title = (n.get("title_cn") or n.get("title") or "")
        summary = (n.get("summary_cn") or n.get("summary") or "")
        body = title + " " + summary
        body_low = body.lower()
        url = n.get("url")
        if not url:
            continue
        types = set()
        # 强匹配
        if name and len(name) >= 3 and name in body:
            types.add("name")
        if name_cn and len(name_cn) >= 2 and name_cn in body:
            types.add("name_cn")
        en = (n.get("entity_name") or "").strip()
        if en and name and en.lower() == name_low:
            types.add("entity")
        # 主题匹配（仅标题级，宁缺毋滥）
        if not types and keywords:
            title_low = title.lower()
            for kw in keywords:
                if _kw_in_text(kw, title_low):
                    types.add("topic")
                    break
        if types:
            hits.setdefault(url, set()).update(types)
    return hits


def rebuild(dry=False):
    scored = json.load(open(SCORED_PATH, "r", encoding="utf-8"))
    ents = json.load(open(ENT_PATH, "r", encoding="utf-8"))
    scores = json.load(open(SCORES_PATH, "r", encoding="utf-8"))

    total_links = 0
    covered = 0
    type_counter = {"name": 0, "name_cn": 0, "entity": 0, "topic": 0}
    examples = []

    for ent in ents:
        serial = ent.get("serial")
        if not serial or serial not in scores:
            continue
        hits = _match_enterprise_news(ent, scored)
        if not hits:
            # 清空（确保旧数据被覆盖为最新结果）
            scores[serial]["related_news_ids"] = []
            continue
        # 按命中类型优先级排序：强匹配优先，其次主题；同一url取并集类型
        urls = list(hits.keys())
        # 排序：强匹配(url)在前
        def _rank(u):
            t = hits[u]
            return 0 if (t & {"name", "name_cn", "entity"}) else 1
        urls.sort(key=_rank)
        scores[serial]["related_news_ids"] = urls
        covered += 1
        total_links += len(urls)
        for u, t in hits.items():
            for k in t:
                type_counter[k] += 1
        if len(examples) < 12:
            examples.append((ent.get("name"), len(urls), sorted(
                {x for s in hits.values() for x in s})))

    if dry:
        print("[rebuild/DRY] 覆盖企业数: %d / %d" % (covered, len(ents)))
        print("[rebuild/DRY] 关联链接总数: %d" % total_links)
        print("[rebuild/DRY] 命中类型计数: %s" % type_counter)
        print("[rebuild/DRY] 示例(企业, 关联数, 类型):")
        for ex in examples:
            print("   ", ex)
        return covered, total_links, type_counter

    # 落盘：先备份
    bak = SCORES_PATH + ".bak_association_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(SCORES_PATH, bak)
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    print("[rebuild] 备份 -> %s" % os.path.basename(bak))
    print("[rebuild] 覆盖企业数: %d / %d" % (covered, len(ents)))
    print("[rebuild] 关联链接总数: %d" % total_links)
    print("[rebuild] 命中类型计数: %s" % type_counter)
    print("[rebuild] 示例(企业, 关联数, 类型):")
    for ex in examples:
        print("   ", ex)
    return covered, total_links, type_counter


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    rebuild(dry=dry)
