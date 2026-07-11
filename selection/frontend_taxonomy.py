#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前台领域映射层（分类/标签 redesign 草案）。

设计原则
--------
- 后台 `data/enterprise/all_enterprises.json` 的 category_l1 / category_l2 / tags **一律不变**
  （每日自动化会写它，改了会被覆盖）。
- 本模块只读后台字段，算出一个「前台领域(frontend domain)」用于导航/筛选/徽章。
- 媒体（行业媒体）与资本（产业资本）按用户要求 **维持现状**：仍在企业库列表里，
  但归为独立前台领域，不再和业务分类混在一起误导「选题找企业」。

映射优先级
----------
1. 是媒体（l2==行业媒体 或 tags 含 行业媒体）→ 行业媒体
2. 否则按 category_l1 查 match_l1 表 → 对应前台领域
3. 都不命中 → 其他/综合

资讯库（generator.py）后续可复用同一套 FRONTEND_DOMAINS 词表，使跨页领域一致。
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_SPEC_PATH = os.path.join(_HERE, "..", "data", "enterprise", "frontend_taxonomy.json")


def _load_spec():
    with open(_SPEC_PATH, encoding="utf-8") as f:
        return json.load(f)


SPEC = _load_spec()
FRONTEND_DOMAINS = [d["name"] for d in SPEC["domains"]]  # 有序
_MEDIA_DOMAIN = SPEC.get("media_domain", "行业媒体")
_OTHER_DOMAIN = SPEC.get("other_domain", "其他/综合")

_L1_MAP = {}
for _d in SPEC["domains"]:
    for _l1 in _d.get("match_l1", []):
        _L1_MAP[_l1] = _d["name"]

_MEDIA_L2 = set(SPEC.get("media_l2", []))
_MEDIA_TAGS = set(SPEC.get("media_tags", []))


def is_media(ent):
    """判断一家企业是否为行业媒体（发布方角色）。"""
    l2 = (ent.get("category_l2") or "") if isinstance(ent, dict) else ""
    tags = (ent.get("tags") or []) if isinstance(ent, dict) else []
    return (l2 in _MEDIA_L2) or any(t in _MEDIA_TAGS for t in tags)


def map_enterprise_domain(ent):
    """返回一家企业的前台领域名。ent 为 all_enterprises.json 的单个元素。"""
    if not isinstance(ent, dict):
        return _OTHER_DOMAIN
    if is_media(ent):
        return _MEDIA_DOMAIN
    l1 = ent.get("category_l1") or ""
    if l1 in _L1_MAP:
        return _L1_MAP[l1]
    return _OTHER_DOMAIN


def build_fdom_counts(enterprises):
    """统计每个前台领域下的企业数，返回 {domain: count}。"""
    counts = {}
    for e in enterprises:
        d = map_enterprise_domain(e)
        counts[d] = counts.get(d, 0) + 1
    return counts


def domain_composition(enterprises):
    """返回 {domain: {l1: count, ...}}，用于预览映射来源构成。"""
    comp = {}
    for e in enterprises:
        d = map_enterprise_domain(e)
        l1 = (e.get("category_l1") or "(空)")
        comp.setdefault(d, {})
        comp[d][l1] = comp[d].get(l1, 0) + 1
    return comp


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(_HERE, ".."))
    from config import ENTERPRISE_CATEGORIES  # noqa
    data = json.load(open(os.path.join(_HERE, "..", "data", "enterprise", "all_enterprises.json"), encoding="utf-8"))
    if isinstance(data, dict):
        data = list(data.values())
    counts = build_fdom_counts(data)
    comp = domain_composition(data)
    print("=== 前台领域分布（按数量降序）===")
    for d in sorted(FRONTEND_DOMAINS, key=lambda x: -counts.get(x, 0)):
        print(f"  {counts.get(d,0):5d}  {d}")
        for l1, c in sorted(comp.get(d, {}).items(), key=lambda x: -x[1]):
            print(f"           {c:5d}  ← {l1}")
    print("\n总计:", sum(counts.values()), "家 · 前台领域数:", len(FRONTEND_DOMAINS))
