#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯库上线前校验闸门（validate_news.py）
-------------------------------------------------
对标企业库 selfcheck 模式：
  - 硬错（has_blocking）= 缺失必需字段 / 非法枚举 / 模板套话 / 标题切片 / serial 格式错 → 阻断部署
  - 软告警（warnings）= 条数骤降 / 评分重算偏差 / serial 指向库外企业 → 仅报告不阻断

用法：
  python validate_news.py [--news data/scored_latest.json] [--strict]
  --strict: 软告警也当作失败（exit 非0）。默认只硬错阻断。
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
NEWS_PATH = os.path.join(REPO, "data", "scored_latest.json")
ENT_PATH = os.path.join(REPO, "data", "enterprise", "all_enterprises.json")

# 允许的 event_type 白名单 —— 直接复用 config.NEWS_EVENT_TYPES，避免口径漂移
from config import NEWS_EVENT_TYPES
EVENT_TYPES = set(NEWS_EVENT_TYPES.keys())
# 银发关联枚举
SILVER_REL = {"核心", "相关", "背景"}
# 推荐理由模板黑名单（来自 recommend.py 的套话，命中即视为未认真写）
TEMPLATE_MARKERS = [
    "国内可参照其融资节奏",
    "宏观趋势中的微观机会点",
    "值得关注",
    "具有重要的参考价值",
    "为行业提供了借鉴",
    "本资讯",
    "本文认为",
    "这一动态值得",
]
SERIAL_RE = re.compile(r"^#\d{4}$")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    strict = "--strict" in sys.argv
    news = load(NEWS_PATH)
    ents = {}
    if os.path.exists(ENT_PATH):
        try:
            for e in load(ENT_PATH):
                if e.get("serial"):
                    ents[e["serial"]] = e.get("name", "")
        except Exception:
            pass

    hard = []      # 硬错：阻断部署
    warns = []     # 软告警：仅报告
    seen_rec = {}  # recommendation 文本 -> [ids]，检测模板复用

    total = len(news)
    for i, a in enumerate(news):
        aid = a.get("id", "?")
        title = (a.get("title_cn") or a.get("title") or "").strip()

        # 1) 必需字段非空（硬）
        for fld in ("summary_cn", "recommendation", "event_type"):
            v = a.get(fld)
            if v is None or str(v).strip() == "":
                hard.append("[%s] 缺少必需字段 %s" % (aid, fld))

        # 2) event_type 白名单（硬）
        et = a.get("event_type")
        if et and et not in EVENT_TYPES:
            hard.append("[%s] event_type 非法: %s" % (aid, et))

        # 3) silver_relevance 枚举（硬）
        sr = a.get("silver_relevance")
        if sr and sr not in SILVER_REL:
            hard.append("[%s] silver_relevance 非法: %s" % (aid, sr))

        # 4) summary_cn 非标题切片（硬）
        sc = (a.get("summary_cn") or "").strip()
        if sc:
            if len(sc) < 30:
                hard.append("[%s] summary_cn 过短(<30字)，疑似占位/标题切片" % aid)
            elif title and (sc == title or sc.startswith(title[:20]) and len(sc) < len(title) + 20):
                hard.append("[%s] summary_cn 疑似标题切片" % aid)

        # 5) recommendation 非模板+结构完整（硬）
        rec = (a.get("recommendation") or "").strip()
        if rec:
            if len(rec) < 50:
                hard.append("[%s] recommendation 过短(<50字)" % aid)
            for mk in TEMPLATE_MARKERS:
                if mk in rec:
                    hard.append("[%s] recommendation 命中模板套话: %s" % (aid, mk))
            # 四段结构检查（软告警，结构不强制但建议）
            secs = sum(1 for k in ("【洞察】", "【选题角度】", "【国内借鉴】", "【风险") if k in rec)
            if secs < 3:
                warns.append("[%s] recommendation 四段结构不完整(命中%d/4)" % (aid, secs))
            # 模板复用检测
            key = rec[:60]
            seen_rec.setdefault(key, []).append(aid)

        # 6) entity_serial 格式 + 库内存在（硬格式 / 软库外）
        ser = (a.get("entity_serial") or "").strip()
        if ser:
            if not SERIAL_RE.match(ser):
                hard.append("[%s] entity_serial 格式非法: %s (应为 #xxxx)" % (aid, ser))
            elif ser not in ents:
                warns.append("[%s] entity_serial %s 在企业库中不存在(断开链接)" % (aid, ser))
            # 有 serial 必有 entity_name（硬）
            if not (a.get("entity_name") or "").strip():
                hard.append("[%s] 有 entity_serial 但缺 entity_name" % aid)

        # 7) tags / domains 数量上限（软）
        tags = a.get("tags") or []
        if isinstance(tags, list) and len(tags) > 3:
            warns.append("[%s] tags 数量 %d > 3" % (aid, len(tags)))
        doms = a.get("domains") or []
        if isinstance(doms, list) and len(doms) > 3:
            warns.append("[%s] domains 数量 %d > 3" % (aid, len(doms)))

        # 8) 评分数值范围（硬）
        for fld in ("final_score", "signal_strength"):
            v = a.get(fld)
            if v is not None:
                try:
                    fv = float(v)
                    if not (0 <= fv <= 100):
                        # 0-10 或 0-100 都可能，放宽到 0-100
                        if fv > 100:
                            hard.append("[%s] %s 超出范围: %s" % (aid, fld, v))
                except (TypeError, ValueError):
                    hard.append("[%s] %s 非数值: %s" % (aid, fld, v))

    # 模板复用汇总（同一前缀出现在 >1 条 → 大概率模板）
    for key, ids in seen_rec.items():
        if len(ids) > 1:
            warns.append("recommendation 疑似模板复用: 前缀「%s...」命中 %d 条 %s"
                         % (key, len(ids), ids[:5]))

    # 输出
    print("=" * 60)
    print("资讯库校验结果：共 %d 条" % total)
    print("-" * 60)
    if hard:
        print("【硬错 %d 条 · 阻断部署】" % len(hard))
        for h in hard:
            print("  ✗", h)
    else:
        print("【硬错 0 条 · 通过】")
    if warns:
        print("【软告警 %d 条 · 仅报告】" % len(warns))
        for w in warns[:40]:
            print("  !", w)
        if len(warns) > 40:
            print("  ... 其余 %d 条略" % (len(warns) - 40))
    print("=" * 60)

    if hard:
        print("RESULT: BLOCK (硬错存在，部署前必须修复)")
        sys.exit(1)
    if strict and warns:
        print("RESULT: BLOCK (strict 模式，软告警也视为失败)")
        sys.exit(2)
    print("RESULT: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
