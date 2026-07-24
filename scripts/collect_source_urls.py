# -*- coding: utf-8 -*-
"""
字段补全时的「网址记录 + 渠道去重」工具（步骤 3 辅助，纯代码、不耗积分）

解决两件事：
  1. 有用网址统计：把补全字段过程中被引用过的网址汇总，若某个网站被大量引用，
     标记为"潜在企业库 / 资讯信息来源"，反馈给信源治理研究员。
  2. 渠道去重：把统计到的网址主域名，与现有渠道列表（config.SOURCES）做去重比对。
     比对规则：只看主频道域名（eTLD+1，如 example.com），**不看二级子域名 / 栏目路径**
     （如 www.example.com、example.com/column/x 都算 example.com）。

用法：
  python collect_source_urls.py                      # 扫描全库 + drafts，输出报告到 stdout
  python collect_source_urls.py --out report.md      # 写文件
  python collect_source_urls.py --min 8              # 潜在源引用阈值（默认 10）

前置：AI 在补全字段时，把用过的参考网址写进企业记录的 `source_urls` 字段（list[str]）。
"""
import json
import os
import re
import sys
import argparse
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIRS = [
    os.path.join(BASE, "scores_draft/rework/drafts_v5"),
    os.path.join(BASE, "data/enterprise/_drafts"),
    os.path.join(BASE, "data/enterprise/_namechunks"),
]

# URL 可能出现的字段
URL_FIELDS = ["website_url", "crunchbase_url", "source_urls", "reference_urls"]
# 多部分后缀（用于提取 eTLD+1）
MULTI_TLD = {
    "co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "net.au", "org.au", "gov.au",
    "co.nz", "com.nz", "co.jp", "or.jp", "ne.jp", "go.jp", "com.cn", "net.cn",
    "org.cn", "gov.cn", "com.tw", "com.hk", "com.sg", "co.kr", "com.br", "co.il",
    "com.mx", "co.za", "com.tr",
}

URL_RE = re.compile(r"https?://[^\s\"'\)\]]+", re.I)


def reg_domain(url):
    """提取主频道域名（eTLD+1），忽略子域名与路径。失败返回空。"""
    if not url:
        return ""
    m = URL_RE.search(url) if ("://" not in url) else None
    if m:
        url = m.group(0)
    try:
        net = urlparse(url if "://" in url else "http://" + url).netloc.lower()
    except Exception:
        return ""
    net = net.split(":")[0]
    if net.startswith("www."):
        net = net[4:]
    parts = net.split(".")
    if len(parts) <= 2:
        return net
    last2 = ".".join(parts[-2:])
    if last2 in MULTI_TLD:
        return ".".join(parts[-3:])
    return last2


def collect_from_record(rec):
    """从一条企业记录抽取所有 URL 字符串。"""
    urls = []
    for f in URL_FIELDS:
        v = rec.get(f)
        if not v:
            continue
        if isinstance(v, list):
            urls.extend(str(x) for x in v if x)
        elif isinstance(v, str):
            # source 字段若是 URL 也收；否则忽略
            if v.startswith("http://") or v.startswith("https://"):
                urls.append(v)
            elif f == "source_urls" or f == "reference_urls":
                urls.append(v)
    return urls


def load_existing_channels():
    """从 config.SOURCES 取现有渠道主域名集合。

    SOURCES 每个源把域名存在 `l1_domain`，把各频道 URL 存在 `l2_channels`
    （list of (name, url, type)）。老结构可能用 `url`/`feeds`。这里全都兼容读取，
    统一归并到主域名（eTLD+1）。之前只读 `s['url']` 导致渠道去重从未生效（已修）。
    """
    domains = set()
    try:
        sys.path.insert(0, BASE)
        import config
        for s in getattr(config, "SOURCES", {}).values():
            # 1) 主域名字段
            for key in ("l1_domain", "url"):
                d = reg_domain(s.get(key) or "")
                if d:
                    domains.add(d)
            # 2) 各频道 URL（l2_channels / feeds 都是 (name, url, type) 元组列表）
            for key in ("l2_channels", "feeds"):
                for ch in s.get(key) or []:
                    url = ch[1] if isinstance(ch, (list, tuple)) and len(ch) > 1 else (ch if isinstance(ch, str) else "")
                    d = reg_domain(url)
                    if d:
                        domains.add(d)
    except Exception as e:
        print(f"[warn] 读取 config.SOURCES 失败：{e}（将只做统计，不做渠道比对）")
    return domains


def main():
    ap = argparse.ArgumentParser(description="网址记录 + 渠道去重")
    ap.add_argument("--out", help="输出 markdown 报告路径")
    ap.add_argument("--min", type=int, default=10, help="潜在源引用阈值（默认 10）")
    args = ap.parse_args()

    per_domain = {}        # domain -> count
    per_domain_serials = {}  # domain -> set(serial)  （用于跨企业判定）
    per_domain_samples = {}  # domain -> 样本企业 serial
    scanned = 0

    def feed(domain, serial):
        if not domain:
            return
        per_domain[domain] = per_domain.get(domain, 0) + 1
        per_domain_serials.setdefault(domain, set()).add(serial)
        per_domain_samples.setdefault(domain, serial)

    # 全库
    if os.path.exists(DB):
        db = json.load(open(DB, encoding="utf-8"))
        for e in db:
            for u in collect_from_record(e):
                feed(reg_domain(u), str(e.get("serial", "")).lstrip("#"))
            scanned += 1
    # drafts
    for d in DRAFTS_DIRS:
        if not os.path.isdir(d):
            continue
        for fp in os.listdir(d):
            if not fp.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(d, fp), encoding="utf-8"))
            except Exception:
                continue
            for u in collect_from_record(j):
                feed(reg_domain(u), j.get("serial", fp))
            scanned += 1

    existing = load_existing_channels()

    # 报告
    lines = []
    lines.append(f"# 网址记录 + 渠道去重报告（扫描 {scanned} 条记录，提取 {sum(per_domain.values())} 个 URL 引用）\n")
    lines.append(f"> 纯代码统计，不耗积分。比对规则：只看主频道域名（eTLD+1），忽略子域名与栏目路径。\n")

    # 1. 潜在信息源（按"跨企业"引用次数，排除企业自家官网的单次引用噪声）
    #    已在渠道库的高频域名无需报备，只报个数；只显性列"不在渠道库、需评估收录"的
    lines.append(f"## 一、被多家企业共同引用（≥{args.min} 家）且**不在渠道库**的域名 → 需评估收录")
    flagged = sorted(
        [(d, len(s)) for d, s in per_domain_serials.items() if len(s) >= args.min],
        key=lambda x: -x[1],
    )
    flagged_new = [(d, n) for d, n in flagged if d not in existing]
    flagged_known = [(d, n) for d, n in flagged if d in existing]
    if not flagged_new:
        lines.append(f"- 无（当前无「不在渠道库」的域名被 {args.min} 家以上企业共同引用）")
    else:
        for d, n in flagged_new:
            lines.append(f"- {d} ：被 {n} 家企业引用 （样本 #{per_domain_samples[d]}） 【⚠️ 建议评估收录】")
    if flagged_known:
        lines.append(f"\n> 另有 {len(flagged_known)} 个高频域名已在渠道库（无需报备）：{'、'.join(d for d, _ in flagged_known[:10])}{' 等' if len(flagged_known) > 10 else ''}")
    lines.append("")

    # 2. 渠道去重比对（只列"跨企业共享"且不在渠道表的域名，过滤企业自家官网噪声）
    lines.append("## 二、渠道去重比对（跨企业共享域名 vs 现有渠道表）")
    new_domains = sorted(
        [(d, len(s)) for d, s in per_domain_serials.items()
         if d not in existing and len(s) >= 2],
        key=lambda x: -x[1],
    )
    if new_domains:
        lines.append(f"### 被 ≥2 家企业引用、但不在现有渠道表的域名（{len(new_domains)} 个，建议评估收录）")
        for d, n in new_domains:
            lines.append(f"- {d} ：{n} 家企业引用")
    else:
        lines.append("- 跨企业共享的域名全部已在现有渠道表中 ✅")
    lines.append("")
    if existing:
        lines.append(f"### 现有渠道表域名数：{len(existing)}（供参考，不逐一列出）")
        lines.append("")

    # 3. 全量引用 Top 20
    lines.append("## 三、引用频次 Top 20（全部域名）")
    top = sorted(per_domain.items(), key=lambda x: -x[1])[:20]
    for d, c in top:
        lines.append(f"- {d} ：{c} 次")
    lines.append("")

    md = "\n".join(lines)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(md)
        print(f"已写报告：{args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
