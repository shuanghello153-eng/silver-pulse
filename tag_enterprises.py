"""
tag_enterprises.py — 从资讯事件 + 融资字段，自动反哺企业库标签。

这是「一手信息反哺」的关键一步：
  - 一条新闻提到某企业在「融资 / IPO上市 / 收购」，该企业自动获得对应标签；
  - 企业自身融资字段若为「有融资 / 已IPO」，也自动打标。
这样企业库的标签筛选（融资 / IPO）始终与最新资讯同步，不用手工维护。

零模型成本（纯字符串匹配 + 字段推导），每天随 run_daily 执行一次。
"""
import json
import os
from collections import defaultdict

from config import DATA_DIR

ENT_PATH = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")

# 会从资讯事件类型映射成企业标签（跳过无信息量的「其他事件」）
EVENT_TAG_MAP = {
    "融资": "融资",
    "IPO上市": "IPO",
    "收购并购": "收购",
    "产品发布": "新品",
    "政策法规": "政策受益",
    "行业趋势": "行业热点",
    "人事变动": "人事",
}
IPO_HINTS = ["ipo", "上市", "纳斯达克", "nasdaq", "nyse", "港股",
             "主板", "挂牌", "公开募股", "public listing", "上市公司"]


def _has_funding(ent):
    for key in ("funding_total", "funding_latest"):
        blob = (ent.get(key) or {})
        disp = blob.get("display", "") if isinstance(blob, dict) else ""
        if disp and "未披露" not in disp and "未融资" not in disp:
            # 只要有具体金额/轮次就算有融资
            if any(c.isdigit() for c in disp) or any(
                k in disp for k in ["轮", "天使", "战略", "A轮", "B轮", "C轮", "融资"]
            ):
                return True
    return False


def _is_ipo(ent):
    parts = []
    for key in ("funding_latest", "funding_total"):
        blob = ent.get(key) or {}
        if isinstance(blob, dict):
            parts.append(str(blob.get("round", "")))
            parts.append(str(blob.get("display", "")))
        elif isinstance(blob, str):
            parts.append(blob)
    parts.append(ent.get("description", "") or "")
    parts.append(ent.get("desc_cn", "") or "")
    blob = " ".join(parts).lower()
    return any(k in blob for k in IPO_HINTS)


def _extract_fund_num(display):
    if not display:
        return 0.0
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z¥$€£亿万千百万]*)", display)
    if not m:
        return 0.0
    val = float(m.group(1))
    unit = m.group(2)
    if "亿" in unit:
        val *= 100.0
    elif "万" in unit:
        val *= 0.1
    return val


def run_daily_step():
    # 1) 读企业库
    with open(ENT_PATH, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    # 2) 建立 企业名 -> 索引（含 name / name_cn / aliases）
    name_to_idx = {}
    for i, e in enumerate(enterprises):
        for nm in [e.get("name", ""), e.get("name_cn", "")]:
            if nm:
                name_to_idx[nm.strip().lower()] = i
        # 别名（若存在）
        for al in (e.get("aliases") or []):
            if al:
                name_to_idx[al.strip().lower()] = i

    # 3) 从资讯聚合 实体 -> 标签集合
    news_tag_map = defaultdict(set)
    if os.path.exists(SCORED_PATH):
        with open(SCORED_PATH, "r", encoding="utf-8") as f:
            news = json.load(f)
        for art in news:
            ent_name = (art.get("entity_name") or "").strip().lower()
            if not ent_name:
                continue
            et = art.get("event_type", "")
            if et in EVENT_TAG_MAP:
                news_tag_map[ent_name].add(EVENT_TAG_MAP[et])

    # 4) 反哺标签
    added_from_news = 0
    added_fund = 0
    added_ipo = 0
    for i, e in enumerate(enterprises):
        tags = list(e.get("tags") or [])
        base = set(tags)
        changed = False

        # 4a) 资讯事件标签
        for nm in [e.get("name", ""), e.get("name_cn", "")]:
            key = nm.strip().lower()
            if key and key in news_tag_map:
                for t in news_tag_map[key]:
                    if t not in base:
                        base.add(t)
                        added_from_news += 1
                        changed = True

        # 4b) 融资 / IPO 派生标签
        if _has_funding(e) and "有融资" not in base:
            base.add("有融资")
            added_fund += 1
            changed = True
        if _is_ipo(e) and "已IPO" not in base:
            base.add("已IPO")
            added_ipo += 1
            changed = True

        if changed:
            # 保留原有顺序，新标签追加在后
            e["tags"] = [t for t in tags if t in base] + [t for t in base if t not in set(tags)]

    # 5) 写回
    with open(ENT_PATH, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"[tag_enterprises] 企业总数={len(enterprises)} | "
          f"资讯反哺标签+{added_from_news} | 有融资+{added_fund} | 已IPO+{added_ipo}")
    return enterprises


if __name__ == "__main__":
    run_daily_step()
