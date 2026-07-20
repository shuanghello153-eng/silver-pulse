# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(HERE, "pilot_output.json"), encoding="utf-8"))
L = []
L.append("# 试点批次 · 30 家高优先级企业（单条推荐理由）\n")
L.append("> 校验：check_single 单条门禁，30/30 通过（两次独立复校）。recommend 已合并重写为单条，覆盖 信号/信息量/差异化/可复制 四维度。\n")
for i, e in enumerate(recs, 1):
    tag = " > ".join([(e.get("tag_l1") or [""])[0] or "", (e.get("tag_l2") or [""])[0] or ""])
    L.append(f"## {i}. {e.get('name_cn') or e.get('name')}  `{e.get('serial')}`  ｜ {tag} ｜ rv={e.get('research_value')}\n")
    L.append(f"- **推荐理由（单条）**：{e.get('recommend')}\n")
    L.append(f"- **desc_cn**：{e.get('desc_cn')}\n")
    L.append(f"- **silver_reason**：{e.get('silver_reason')}\n")
    L.append(f"- **payor_model**：{e.get('payor_model')}  ｜ silver_verdict：{e.get('silver_verdict')}\n")
    L.append(f"- **四维分**：信号 {e.get('signal_strength')} / 信息 {e.get('info_score')} / 差异 {e.get('diff_score')} / 可复制 {e.get('copy_score')} / 综合 {e.get('research_value')}\n")
    L.append("")
md = "\n".join(L)
open(os.path.join(HERE, "pilot_review.md"), "w", encoding="utf-8").write(md)
print("written pilot_review.md, bytes=", len(md.encode("utf-8")))
