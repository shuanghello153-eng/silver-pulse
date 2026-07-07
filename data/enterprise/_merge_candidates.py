#!/usr/bin/env python3
"""一次性合并 _candidates_websearch.json -> all_enterprises.json。

- 按归一化 name 去重（忽略大小写/空格），避免重复入库。
- 为新条目分配 #XXXX 自增 serial。
- 候选 12 字段映射到库 20 字段（缺失项填空，value_score=0 留给 enterprise_score 计算）。
- 不改写既有 992 条的任意字段。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
EXIST = os.path.join(BASE, "all_enterprises.json")
CAND = os.path.join(BASE, "_candidates_websearch.json")


def norm(s):
    return (s or "").strip().lower()


def main():
    existing = json.load(open(EXIST, encoding="utf-8"))
    cands = json.load(open(CAND, encoding="utf-8"))

    exist_names = {norm(e.get("name", "")) for e in existing}
    # 也用 name_cn 兜底去重
    for e in existing:
        nc = e.get("name_cn", "")
        if nc:
            exist_names.add(norm(nc))

    max_serial = max(
        (int(e.get("serial", "#0000").lstrip("#") or 0) for e in existing),
        default=0,
    )

    added, skipped = [], []
    for c in cands:
        nm = norm(c.get("name", ""))
        nm_cn = norm(c.get("name_cn", ""))
        if nm in exist_names or (nm_cn and nm_cn in exist_names):
            skipped.append(c.get("name", ""))
            continue
        max_serial += 1
        serial = "#%04d" % max_serial
        desc = c.get("description", "") or ""
        entry = {
            "serial": serial,
            "name": c.get("name", ""),
            "name_cn": c.get("name_cn", ""),
            "region": c.get("region", ""),
            "category_l1": c.get("category_l1", ""),
            "category_l2": c.get("category_l2", ""),
            "tags": c.get("tags", []) or [],
            "description": desc,
            "highlights": c.get("worth_note", "") or "",
            "funding_latest": c.get("funding_latest", "") or "",
            "funding_total": c.get("funding_total", "") or "",
            "investors": "",
            "founded": "",
            "value_score": 0,
            "source": c.get("source", "") or "",
            "crunchbase_url": "",
            "website_url": c.get("website_url", "") or "",
            "business_model": "",
            "desc_cn": desc,
            "business_model_cn": "",
            "news_coverage": "",
        }
        existing.append(entry)
        exist_names.add(nm)
        if nm_cn:
            exist_names.add(nm_cn)
        added.append(c.get("name", ""))

    json.dump(existing, open(EXIST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("MERGE DONE")
    print("  added:", len(added))
    print("  skipped(dup):", len(skipped))
    print("  total now:", len(existing))
    if skipped:
        print("  skipped names:", skipped[:20])


if __name__ == "__main__":
    main()
