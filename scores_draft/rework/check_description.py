# -*- coding: utf-8 -*-
"""
Description（企业介绍）质量门禁脚本（V7.3 · D1–D4）

与 check_single.py（R1–R10 针对 recommend）互补，
共同构成企业库数据质量的完整机械检查层。

设计原则：
  - D1-D4 全部是**机械可判**的检查（字符串操作/正则/长度），不需要模型
  - 与 recommend 门禁合一次跑：先跑 D1-D4（description）+ R1-R10（recommend）
  - 复用 check_single.py 的 BANNED 词表，不维护两套

用法：
  python check_description.py draft_#XXXX.json        # 单条
  python check_description.py --batch batch_src.json   # 批量
  （被其他脚本 import：from check_description import validate_desc）

【规则清单】
  D1     description 非空且 ≥20 字
  D2     非纯英文（中文字符占比 > 30%）
  D3     命中 BANNED 模板句（复用 check_single.py 的词表）
  D4     无原始标记残留（【提供资源】【需求数源】等）
"""

import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))

# ---- 从 check_single.py 复用 BANNED 词表 ----
try:
    from check_single import BANNED, BANNED_RE
except ImportError:
    # 如果 check_single 不在路径中，定义最小版本
    BANNED = [
        "是一家致力于", "致力于为老年人", "专注于为老年",
        "切入行业媒体赛道", "切入XX赛道", "可作为选题储备", "归档备用",
        "信号偏弱、信息量一般", "整体信号偏弱",
        "信息量评分", "维度评分", "研究价值", "异类样本",
        "照搬难", "暂列观察", "翻译腔",
        "放到国内银发版图", "放到国内养老版图", "放到国内康复版图",
        "选题可写", "拆开看", "值得一写", "值得跟踪", "值得关注",
        "信号清晰", "信号偏弱", "信号尚可",
    ]
    BANNED_RE = [
        r"研究价值\d+(\.\d+)?分可作参考",
        r"放到国内.+版图",
        r"选题可写[「\"]", r"可写[\"\\\"]",
    ]

# ---- 原始标记残留（D4 检测）----
# 说明（2026-07-26 修复）：原实现把所有标记塞进一个列表并用 re.search 匹配，
# 但半角 "[提供资源]"/"[需求数源]" 在正则里是**字符集**（匹配 提/供/资/源 任一字），
# 会误杀几乎所有含"提供/资源/源"的中文描述（实测误杀现有库 165/300）。
# 按文档意图（检测字面占位标记），拆成"字面标记"与"正则标记"两类分别处理。
RAW_MARKERS_LITERAL = ["【提供资源】", "【需求数源】", "[提供资源]", "[需求数源]",
                       "【来源】", "【备注】"]
RAW_MARKERS_REGEX = [r"【待补充】.*未补充"]
# 兼容旧引用
RAW_MARKERS = RAW_MARKERS_LITERAL + RAW_MARKERS_REGEX


def content_len(s):
    """计算去空格后的字符长度。"""
    return len(re.sub(r"\s", "", s or ""))


def validate_desc(e, skip=None):
    """
    检查企业的 description 质量。
    返回 issues 列表（空=通过）。

    e 须含 description 字段。可选地也检查 recommend（如果需要联合报告）。
    """
    skip = set(skip or [])
    issues = []
    desc = e.get("description")

    # ── D1：非空且 ≥20 字 ──
    if "D1" not in skip:
        if not desc or not isinstance(desc, str) or not desc.strip():
            issues.append("D1:description 为空或非字符串")
        else:
            cl = content_len(desc)
            if cl < 20:
                issues.append(f"D1:description 过短({cl}<20)")

    # ── D2：非纯英文（中文占比 >30%）──
    if "D2" not in skip and desc and isinstance(desc, str):
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', desc))
        total_visible = len(desc.strip())
        if total_visible > 0 and chinese_chars / total_visible < 0.3:
            ratio = chinese_chars / total_visible * 100
            issues.append(f"D2:description 英文主导(中文仅{ratio:.0f}%)")

    # ── D3：命中 BANNED 模板句 ──
    if "D3" not in skip and desc and isinstance(desc, str):
        for b in BANNED:
            if b in desc:
                issues.append(f"D3:模板套话[{b}]")
        for pat in BANNED_RE:
            if re.search(pat, desc):
                issues.append(f"D3:模板套话正则[{pat}]")

    # ── D4：原始标记残留 ──
    if "D4" not in skip and desc and isinstance(desc, str):
        for m in RAW_MARKERS_LITERAL:
            if m in desc:                       # 字面子串匹配，方括号不再当字符集
                issues.append(f"D4:原始标记残留[{m}]")
        for m in RAW_MARKERS_REGEX:
            if re.search(m, desc):
                issues.append(f"D4:原始标记残留[{m}]")

    return issues


def validate_combined(e, others=None, skip=None):
    """
    联合检查 description(D1-D4) + recommend(R1-R10)。
    返回 {"desc_issues": [...], "rec_issues": [...]}。
    方便一次调用覆盖两个字段。
    """
    skip = set(skip or [])
    desc_issues = validate_desc(e, skip)

    rec_issues = []
    r = e.get("recommend")
    if r and isinstance(r, str):
        try:
            from check_single import validate as validate_rec
            rec_issues = validate_rec(e, others=others, skip=skip)
        except ImportError:
            rec_issues = ["[check_single 导入失败，无法校验 recommend]"]

    return {"desc_issues": desc_issues, "rec_issues": rec_issues}


def _ctx_from_db(serial):
    """从 all_enterprises.json 读取企业上下文。"""
    db_path = os.path.join(BASE, "data", "enterprise", "all_enterprises.json")
    if not os.path.exists(db_path):
        db_path = os.path.join(BASE, "data", "enterprise_allenterprises.json")  # 兼容旧路径
    if not os.path.exists(db_path):
        return {}
    with open(db_path, encoding="utf-8") as f:
        data = json.load(f)
    targets = data if isinstance(data, list) else data.get("enterprises", data.get("data", []))
    for item in targets:
        sid = str(item.get("serial", "")).lstrip("#")
        if sid == str(serial).lstrip("#"):
            return item
    return {}


def main():
    args = sys.argv[1:]
    if not args:
        print("用法:")
        print("  python check_description.py <draft_#XXXX.json>          # 单条")
        print("  python check_description.py --batch <batch_src.json>   # 批量（只查 description）")
        print("  python check_description.py --combined <batch_src.json> # 批量（description + recommend 联合查）")
        sys.exit(1)

    if args[0] == "--combined" and len(args) >= 2:
        # 联合模式：同时查 D1-D4 + R1-R10
        try:
            from check_single import validate as validate_rec
        except ImportError:
            print("[ERROR] 无法导入 check_single.py，联合模式不可用")
            sys.exit(1)
        recs = json.load(open(args[1], encoding="utf-8"))
        others_rec = [r.get("recommend", "") for r in recs if isinstance(r.get("recommend"), str)]
        desc_fails, rec_fails, both_ok = 0, 0, 0
        for r in recs:
            di = validate_desc(r)
            ri = validate_rec(r, others=others_rec) if r.get("recommend") else []
            if di or ri:
                desc_fails += (1 if di else 0)
                rec_fails += (1 if ri else 0)
                s = r.get("serial", "?")
                if di:
                    print(f"  {s} DESC: {di}")
                if ri:
                    print(f"  {s} REC:  {ri}")
            else:
                both_ok += 1
        total = len(recs)
        print(f"\n联合校验 {total} 家 | desc 通过 {total-desc_fails} | recommend 通过 {total-rec_fails} | 全通过 {both_ok}")
        if desc_fails + rec_fails > 0:
            sys.exit(1)
        sys.exit(0)

    if args[0] == "--batch" and len(args) >= 2:
        recs = json.load(open(args[1], encoding="utf-8"))
        fails = {}
        for r in recs:
            iss = validate_desc(r)
            if iss:
                fails[r.get("serial", "?")] = iss
        print(f"Description 校验 {len(recs)} 家 | 通过 {len(recs)-len(fails)} | 未过 {len(fails)}")
        for s, iss in fails.items():
            print(f"  {s}: {iss}")
        sys.exit(0 if not fails else 1)

    # 单条模式
    fp = args[0]
    dr = json.load(open(fp, encoding="utf-8"))
    ctx = _ctx_from_db(dr.get("serial", ""))
    tmp = dict(ctx)
    for k in ("description", "recommend", "name", "name_cn"):
        if k in dr and dr[k] is not None:
            tmp[k] = dr[k]
    iss = validate_desc(tmp)
    print("PASS" if not iss else f"FAIL: {iss}")


if __name__ == "__main__":
    main()
