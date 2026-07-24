#!/usr/bin/env python3
"""从候选.json 生成企业库入库预览表 Excel（步骤 8 发给小爽审核用）。

用法：
  python scripts/build_preview.py --candidates 候选.json --out 预览表.xlsx

预览表列 = 步骤 8 要求的全字段；银发信号判定 / 去重结果 为流程判定列，留空由人填。
"""
import argparse
import json
import sys

try:
    from openpyxl import Workbook
except ImportError:
    sys.exit("需要 openpyxl：pip install openpyxl")

# (数据字段键, 预览表表头)；以 _note_ 开头的是流程判定列，留空
COLUMNS = [
    ("serial", "serial"),
    ("name", "name"),
    ("name_cn", "name_cn"),
    ("tag_l2", "tag_l2"),
    ("description", "description(全文)"),
    ("recommend", "recommend(全文)"),
    ("signal_strength", "signal_strength"),
    ("info_score", "info_score"),
    ("diff_score", "diff_score"),
    ("copy_score", "copy_score"),
    ("total_score", "total_score(×10显示)"),
    ("funding_latest", "funding_latest"),
    ("funding_total", "funding_total"),
    ("investors", "investors"),
    ("payor_model", "payor_model"),
    ("founded", "founded"),
    ("stage", "stage"),
    ("region", "region"),
    ("website_url", "官网"),
    ("crunchbase_url", "crunchbase"),
    ("deep_article_links", "deep_article_links"),
    ("news_coverage", "news_coverage"),
    ("ingest_time", "ingest_time"),
    ("update_time", "update_time"),
    ("source", "source"),
    ("_note_银发信号判定", "银发信号判定(通过/拒绝+理由)"),
    ("_note_去重结果", "去重结果(新/已存在/疑似重复)"),
]


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True, help="候选 JSON 路径（单条或列表）")
    ap.add_argument("--out", default="预览表.xlsx", help="输出 Excel 路径")
    args = ap.parse_args()

    with open(args.candidates, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]

    wb = Workbook()
    ws = wb.active
    ws.title = "预览"
    ws.append([h for _, h in COLUMNS])
    for ent in data:
        row = []
        for key, _ in COLUMNS:
            if key.startswith("_note_"):
                row.append("")  # 流程判定列，留空由人填
            else:
                row.append(fmt(ent.get(key)))
        ws.append(row)

    wb.save(args.out)
    print(f"已生成 {args.out}，共 {len(data)} 家企业")


if __name__ == "__main__":
    main()
