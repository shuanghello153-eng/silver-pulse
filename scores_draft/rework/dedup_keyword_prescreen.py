# -*- coding: utf-8 -*-
"""
全库去重 · 关键词初筛脚本（步骤 2.1 落地版）

定位：在精确匹配 / AI 增量比对之前，先用纯代码做一轮**关键词提取 + 模糊匹配**，
把"明显不重复"的企业先排除掉，减少后续 AI 比对工作量（省积分）。

原理：
  1. 提取企业核心名称：去掉公司后缀（公司/有限公司/股份有限公司/集团/Inc./Corp.…）
     再去掉已知城市 / 国家前缀（北京/上海/Tokyo/New York…）。
  2. 用核心词在全库 name / name_cn 中做双向子串匹配。
  3. 命中的列为"疑似重复候选"，连同匹配方式一起输出，交给 AI 做信息增量比对。

全程纯字符串操作，**不调用任何模型，不消耗积分**。

用法：
  python dedup_keyword_prescreen.py                      # 扫描 data/enterprise/_drafts/ 下 draft_*.json
  python dedup_keyword_prescreen.py --candidates x.json  # x.json = [{serial,name,name_cn?}, ...]
  python dedup_keyword_prescreen.py --name "北京乐龄养老科技有限公司"
  python dedup_keyword_prescreen.py --out report.md      # 指定输出
"""
import json
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS = os.path.join(HERE, "drafts_v5")
DRAFTS_FALLBACK = os.path.join(BASE, "data/enterprise/_drafts")

# ---- 公司后缀（去掉后剩下核心词）----
SUFFIXES = [
    "股份有限公司", "有限责任公司", "有限公司", "集团有限公司", "集团公司",
    "控股有限公司", "控股集团", "科技发展有限公司", "科技有限公司", "信息技术有限公司",
    "网络科技有限公司", "生物医药科技有限公司", "健康管理有限公司", "养老服务有限公司",
    "医疗科技有限公司", "智能科技有限公司", "科技股份有限公司", "实业有限公司",
    "投资管理有限公司", "企业管理有限公司", "咨询有限公司", "文化传播有限公司",
    "教育科技有限公司", "软件有限公司", "集团", "公司", "科技", "技术", "网络",
    "信息", "软件", "生物", "医疗", "健康", "养老", "文化", "传媒", "教育",
    "投资", "管理", "咨询", "服务", "实业", "发展", "国际",
    "Inc.", "Inc", "Corp.", "Corp", "Co.", "Co", "Ltd.", "Ltd", "LLC",
    "GmbH", "PLC", "plc", "S.A.", "S.A", "Pte", "B.V.", "K.K.",
    "株式会社", "股份有限公司", "주식회사", "유한회사", "SAS", "Sarl", "S.à r.l.",
]
# ---- 国家 / 城市前缀（去掉后剩下核心词）----
PREFIXES = [
    "中国", "美国", "日本", "德国", "英国", "法国", "新加坡", "澳大利亚", "加拿大",
    "荷兰", "瑞士", "瑞典", "丹麦", "芬兰", "挪威", "以色列", "韩国", "印度",
    "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "重庆",
    "天津", "苏州", "无锡", "青岛", "宁波", "厦门", "长沙", "郑州", "合肥", "福州",
    "济南", "昆明", "贵阳", "南宁", "哈尔滨", "沈阳", "长春", "大连", "常州", "佛山",
    "东莞", "珠海", "中山", "惠州", "嘉兴", "绍兴", "金华", "台州", "温州", "泉州",
    "东京", "大阪", "名古屋", "京都", "纽约", "旧金山", "洛杉矶", "波士顿", "西雅图",
    "芝加哥", "伦敦", "巴黎", "柏林", "慕尼黑", "法兰克福", "阿姆斯特丹", "斯德哥尔摩",
    "哥本哈根", "苏黎世", "日内瓦", "特拉维夫", "新加坡", "香港", "台北", "首尔", "孟买",
    "班加罗尔", "悉尼", "墨尔本", "多伦多", "温哥华",
]


def core_name(name):
    """提取企业核心名称：去后缀 + 去城市/国家前缀 + 去空格标点。"""
    if not name:
        return ""
    s = name.strip()
    # 去掉括号及其中内容（如 (中国) / (Beijing)）
    s = re.sub(r"[（(][^（）()]*[)）]", "", s)
    s = re.sub(r"\s+", "", s)
    # 反复去后缀，直到不再变化（处理 "科技有限公司" -> "科技" -> "" 的情况）
    changed = True
    while changed:
        changed = False
        for suf in SUFFIXES:
            if s.endswith(suf) and len(s) > len(suf):
                s = s[: -len(suf)]
                changed = True
                break
    # 去前缀
    changed = True
    while changed:
        changed = False
        for pre in PREFIXES:
            if s.startswith(pre) and len(s) > len(pre):
                s = s[len(pre):]
                changed = True
                break
    return s.strip()


def load_db():
    if not os.path.exists(DB):
        return []
    return json.load(open(DB, encoding="utf-8"))


def match_one(cand_core, db_index):
    """用核心词在 db_index(name_core -> list of (serial,name)) 中做双向子串匹配。"""
    hits = []
    if not cand_core:
        return hits
    for db_core, entries in db_index.items():
        if not db_core:
            continue
        # 双向子串：核心词互相包含即视为疑似
        if cand_core in db_core or db_core in cand_core:
            # 长度过短（<=1字）容易误命中，跳过
            if len(cand_core) <= 1 and len(db_core) <= 1:
                continue
            hits.extend(entries)
    return hits


def build_index(db):
    idx = {}
    for e in db:
        nm = e.get("name") or ""
        nmc = e.get("name_cn") or ""
        serial = str(e.get("serial", "")).lstrip("#")
        for raw in (nm, nmc):
            c = core_name(raw)
            if c:
                idx.setdefault(c, []).append((serial, raw))
    return idx


def load_candidates(args):
    if args.name:
        return [{"serial": "CLI", "name": args.name, "name_cn": ""}]
    if args.candidates:
        return json.load(open(args.candidates, encoding="utf-8"))
    # 扫描 drafts 目录
    d = DRAFTS if os.path.isdir(DRAFTS) else DRAFTS_FALLBACK
    if not os.path.isdir(d):
        print("未找到候选人来源（--candidates / --name / drafts 目录）")
        return []
    cands = []
    for fp in sorted(os.listdir(d)):
        if not fp.startswith("draft_") or not fp.endswith(".json"):
            continue
        try:
            j = json.load(open(os.path.join(d, fp), encoding="utf-8"))
        except Exception:
            continue
        cands.append({
            "serial": j.get("serial", fp),
            "name": j.get("name", ""),
            "name_cn": j.get("name_cn", ""),
        })
    return cands


def main():
    ap = argparse.ArgumentParser(description="全库去重·关键词初筛")
    ap.add_argument("--candidates", help="候选人 JSON 文件")
    ap.add_argument("--name", help="单个企业名测试")
    ap.add_argument("--out", help="输出 markdown 报告路径")
    args = ap.parse_args()

    db = load_db()
    idx = build_index(db)
    cands = load_candidates(args)
    if not cands:
        print("无候选人可处理")
        return

    rows = []
    for c in cands:
        raw = c.get("name") or ""
        raw_cn = c.get("name_cn") or ""
        core = core_name(raw) or core_name(raw_cn)
        hits = match_one(core, idx)
        # 按 serial 去重（同家企业 name/name_cn 可能各命中一次）
        seen = set()
        dedup_hits = []
        for serial, nm in hits:
            if serial not in seen:
                seen.add(serial)
                dedup_hits.append((serial, nm))
        rows.append({
            "serial": c.get("serial", ""),
            "name": raw,
            "name_cn": raw_cn,
            "core": core,
            "matches": dedup_hits,  # [(serial, name), ...]
        })

    # 输出
    n_cand = len(rows)
    n_suspect = sum(1 for r in rows if r["matches"])
    lines = []
    lines.append(f"# 去重关键词初筛报告（{n_cand} 家候选，{n_suspect} 家疑似重复）\n")
    lines.append("> 纯代码初筛（不耗积分）。疑似重复候选交 AI 做信息增量比对（步骤 2.2）。\n")
    for r in rows:
        if r["matches"]:
            lines.append(f"## ⚠️ {r['serial']} · {r['name']}（核心词：{r['core']}）")
            for serial, nm in r["matches"]:
                lines.append(f"- 疑似重复 → #{serial} {nm}")
            lines.append("")
        else:
            lines.append(f"- ✅ {r['serial']} · {r['name']}（核心词：{r['core']}）— 初筛无重复")
    md = "\n".join(lines)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(md)
        print(f"已写报告：{args.out}")
    else:
        print(md)
    print(f"\n初筛完成：{n_cand} 家 / 疑似重复 {n_suspect} 家 / 无重复 {n_cand - n_suspect} 家")


if __name__ == "__main__":
    main()
