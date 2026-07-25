# -*- coding: utf-8 -*-
"""
scripts/score_candidates.py — 给「候选名单」算评分（信号强度 + 总分），支持任意数量（1 家到全库）。

为什么有这个脚本（V8.5 新增，回应"想提交多少名单就提交多少"的灵活性需求）：
  正常入库时，AI 在「生产候选」阶段已经填好 description / recommend / info_score /
  diff_score / copy_score / funding_latest 等字段，写进候选.json。本脚本只补「脚本能算」的两项：
    * signal_strength：复用 selection.signal_strength.compute_signal_strength，
      从企业的「最新融资 / 大事件」拼成 article dict 喂入（保底 0.5、封顶 10，零模型成本）。
    * total_score：四维加权 = 信号×0.3 + 信息×0.3 + 差异×0.2 + 复制×0.2（封顶 0~10）。
  与 merge_batch_scores.py 的区别：本脚本面向「任意候选子集」，只读候选.json；
  merge_batch_scores.py 面向「公式/权重变了，重算全库 1773 家」，二者互不替代。
  enterprise_build.py 合并时本就只动候选里的 serial，所以「交多少算多少、合多少并多少」天然成立。

用法：
  python scripts/score_candidates.py --candidates 候选.json
  python scripts/score_candidates.py --candidates 候选.json --out 候选.scored.json
  python scripts/score_candidates.py --candidates 候选.json --source-tier 2 --keep-signal
"""
import json
import os
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(BASE, "selection"))
from signal_strength import compute_signal_strength  # noqa: E402


def _fmt_amount(amt):
    """把 funding_latest.amount 规整成信号脚本能识别的文本（'2亿美元' / '$200M'）。"""
    if amt is None:
        return ""
    if isinstance(amt, (int, float)):
        if amt >= 1e8:
            return f"{amt / 1e8:.2f}亿".replace(".00", "")
        if amt >= 1e4:
            return f"{amt / 1e4:.2f}万".replace(".00", "")
        return str(int(amt))
    return str(amt)


def build_article(c):
    """从企业候选拼一个 article dict 喂给 compute_signal_strength。"""
    name = c.get("name") or c.get("name_cn") or ""
    fl = c.get("funding_latest") or {}
    date = c.get("ingest_time") or ""
    title = name
    summary = ""

    if isinstance(fl, dict):
        rnd = (fl.get("round") or fl.get("type") or "")
        amt = fl.get("amount")
        date = fl.get("date") or date
        rnd_low = str(rnd).lower()
        if "ipo" in rnd_low or "上市" in str(rnd):
            title += " IPO 上市"
        elif "收购" in str(rnd) or "并购" in str(rnd):
            title += " 收购"
        else:
            title += f" {rnd} 融资" if rnd else " 融资"
        a = _fmt_amount(amt)
        if a:
            summary = f"融资 {a}"
    elif isinstance(fl, str) and fl.strip():
        title += " 融资"
        summary = fl
    else:
        # 无融资信息：退化为 description 首句 + ingest_time（只吃时效分，信号偏低）
        title = name
        summary = (c.get("description") or c.get("desc_cn") or "")[:120]

    return {"title": title.strip(), "summary": summary.strip(), "date": (date or "")[:10]}


def compute_signal(c, source_tier):
    art = build_article(c)
    s, _bd = compute_signal_strength(art, source_tier=source_tier)
    s = max(0.5, min(10.0, s))  # 保底 0.5、封顶 10
    return round(s, 2)


def compute_total(c):
    sig = float(c.get("signal_strength") or 0)
    info = float(c.get("info_score") or 0)
    diff = float(c.get("diff_score") or 0)
    copy = float(c.get("copy_score") or 0)
    return round(max(0.0, min(10.0, sig * 0.3 + info * 0.3 + diff * 0.2 + copy * 0.2)), 1)


def main():
    ap = argparse.ArgumentParser(description="给候选名单算 signal_strength + total_score（任意子集）")
    ap.add_argument("--candidates", required=True, help="候选 JSON（list 或 {enterprises:[...]}）")
    ap.add_argument("--out", help="输出文件（默认覆盖输入）")
    ap.add_argument("--source-tier", type=int, default=2, help="信源起点等级 1/2/3（默认 2）")
    ap.add_argument("--keep-signal", action="store_true", help="保留候选里已有的 signal_strength，不重算")
    args = ap.parse_args()

    raw = json.load(open(args.candidates, encoding="utf-8"))
    if isinstance(raw, dict):
        cands = raw.get("enterprises", raw)
    else:
        cands = raw

    n_total = 0
    n_no_total = 0
    for c in cands:
        if not args.keep_signal or c.get("signal_strength") is None:
            c["signal_strength"] = compute_signal(c, args.source_tier)
        else:
            c["signal_strength"] = max(0.5, min(10.0, float(c["signal_strength"])))
        if all(c.get(k) is not None for k in ("info_score", "diff_score", "copy_score")):
            c["total_score"] = compute_total(c)
            n_total += 1
        else:
            n_no_total += 1

    out = args.out or args.candidates
    json.dump(raw if isinstance(raw, dict) else cands, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"已写回 {out}：共 {len(cands)} 家 | 算 total {n_total} 家 | "
          f"{n_no_total} 家缺四维未算 total（需 AI 补 info/diff/copy）")


if __name__ == "__main__":
    main()
