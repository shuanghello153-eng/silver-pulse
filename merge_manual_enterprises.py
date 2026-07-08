#!/usr/bin/env python3
"""
merge_manual_enterprises.py — 把「一次性人工候选企业」合并进企业库。

用法:
    python merge_manual_enterprises.py [candidates.json]

默认读取 data/inc5000_candidates.json。候选 JSON 结构:
    [{"name","url","description","segment","hq","revenue","employees","why_relevant"}, ...]

合并规则:
- 按 name(忽略大小写) 与 website 域名去重，已存在则跳过。
- 新条目 value_score 置 0；流水线 enterprise_score 步骤会实时计算 research_value 并写 SCORES_PATH，
  gen_enterprise 优先用实时分，因此无需本脚本算分。
- 其余 21 字段按 schema 默认值填充；segment 映射到 category_l1/category_l2。
"""
import os
import sys
import json
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALL_PATH = os.path.join(BASE_DIR, "data", "enterprise", "all_enterprises.json")
DATA_DIR = os.path.join(BASE_DIR, "data")

SEG_MAP = {
    "居家护理": ("养老服务", "居家护理"),
    "养老社区": ("养老服务", "养老社区"),
    "退休社区": ("养老服务", "养老社区"),
    "养老金融": ("养老金融", "养老金融"),
    "退休金融": ("养老金融", "养老金融"),
    "辅具器械": ("辅具器械", "辅具器械"),
    "助听器": ("辅具器械", "助听器"),
    "康复器械": ("辅具器械", "康复器械"),
    "老年健康消费": ("老年消费", "老年健康消费"),
    "健康食品": ("老年消费", "健康食品"),
    "适老消费": ("老年消费", "适老消费"),
    "慢病管理": ("数字健康", "慢病管理"),
    "监护科技": ("数字健康", "监护科技"),
    "数字健康": ("数字健康", "数字健康"),
    "远程医疗": ("数字健康", "远程医疗"),
}


def domain_of(url):
    try:
        net = urlparse(url).netloc.lower()
        return net[4:] if net.startswith("www.") else net
    except Exception:
        return ""


def map_cat(segment):
    for k, v in SEG_MAP.items():
        if k in (segment or ""):
            return v
    return ("其他", segment or "其他")


def main():
    cand_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA_DIR, "inc5000_candidates.json")
    if not os.path.exists(cand_path):
        print("[merge] 候选文件不存在: %s (跳过)" % cand_path)
        return 0
    cands = json.load(open(cand_path, "r", encoding="utf-8"))
    if not cands:
        print("[merge] 候选为空，跳过")
        return 0

    ents = json.load(open(ALL_PATH, "r", encoding="utf-8"))
    existing_names = {e.get("name", "").strip().lower() for e in ents}
    existing_domains = {domain_of(e.get("website_url", "")) for e in ents if e.get("website_url")}

    # 下一个 serial
    max_n = 0
    for e in ents:
        s = e.get("serial", "")
        if s.startswith("#"):
            try:
                max_n = max(max_n, int(s[1:]))
            except Exception:
                pass

    added = 0
    skipped = 0
    for c in cands:
        name = (c.get("name") or "").strip()
        if not name:
            skipped += 1
            continue
        if name.lower() in existing_names:
            skipped += 1
            continue
        dom = domain_of(c.get("url", ""))
        if dom and dom in existing_domains:
            skipped += 1
            continue
        max_n += 1
        cat1, cat2 = map_cat(c.get("segment"))
        hl_parts = []
        if c.get("hq"):
            hl_parts.append("总部 %s" % c["hq"])
        if c.get("revenue"):
            hl_parts.append("营收 %s" % c["revenue"])
        if c.get("employees"):
            hl_parts.append("员工 %s" % c["employees"])
        desc = c.get("description") or c.get("why_relevant") or ""
        entry = {
            "serial": "#%04d" % max_n,
            "name": name,
            "region": "海外",
            "category_l1": cat1,
            "category_l2": cat2,
            "tags": ["INC5000"] + ([c["segment"]] if c.get("segment") else []),
            "description": desc,
            "highlights": "；".join(hl_parts),
            "funding_latest": {"date": "", "amount": "", "round": "", "display": ""},
            "funding_total": {"amount": "", "display": ""},
            "investors": "",
            "founded": "",
            "value_score": 0,
            "source": "INC5000手动补库",
            "crunchbase_url": "",
            "website_url": c.get("url", ""),
            "business_model": "",
            "desc_cn": desc,
            "business_model_cn": "",
            "news_coverage": "",
            "name_cn": "",
        }
        ents.append(entry)
        existing_names.add(name.lower())
        if dom:
            existing_domains.add(dom)
        added += 1
        print("  + [%s] %s (%s)" % (entry["serial"], name, cat1))

    json.dump(ents, open(ALL_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[merge] 完成：新增 %d，跳过 %d，企业库现 %d 家" % (added, skipped, len(ents)))
    return added


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 1)
