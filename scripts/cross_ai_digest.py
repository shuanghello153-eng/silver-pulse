# -*- coding: utf-8 -*-
"""
跨 AI 笔记摘要器（V7.4 新增）

按目标 AI 名列出 handoff/cross_ai_notes/ 下"待处理"的笔记，供各 AI 每周自动化查看。

用法：
  python cross_ai_digest.py --ai 企业库AI          # 列出给"企业库AI"的待处理笔记
  python cross_ai_digest.py --ai 全体              # 列出给全体的
  python cross_ai_digest.py --ai 企业库AI --all    # 含已处理
"""
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
NOTES = os.path.join(BASE, "handoff", "cross_ai_notes")


def parse_note(fp):
    txt = open(fp, encoding="utf-8").read()
    head = {}
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                head[k.strip()] = v.strip()
    body = txt[m.end():].strip() if m else txt.strip()
    return head, body


def main():
    ap = argparse.ArgumentParser(description="跨 AI 笔记摘要")
    ap.add_argument("--ai", required=True, help="目标 AI 名（企业库AI/标签AI/资讯AI/信源扩充AI/全体）")
    ap.add_argument("--all", action="store_true", help="包含已处理")
    args = ap.parse_args()

    if not os.path.isdir(NOTES):
        print("无 cross_ai_notes 目录")
        return
    rows = []
    for fp in sorted(os.listdir(NOTES)):
        if not fp.endswith(".md") or fp.lower().startswith("readme"):
            continue
        head, body = parse_note(os.path.join(NOTES, fp))
        to = head.get("to", "")
        status = head.get("status", "待处理")
        if args.ai not in (to, "全体"):
            continue
        if status == "已处理" and not args.all:
            continue
        rows.append((fp, head, body[:120]))

    if not rows:
        print(f"✅ 给「{args.ai}」无待处理笔记")
        return
    print(f"# 给「{args.ai}」的笔记（{len(rows)} 条）\n")
    for fp, head, body in rows:
        print(f"## {fp}")
        print(f"- from: {head.get('from','?')} | date: {head.get('date','?')} | status: {head.get('status','待处理')}")
        print(f"- 摘要：{body}")
        print("")


if __name__ == "__main__":
    main()
