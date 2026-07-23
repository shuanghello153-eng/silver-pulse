# -*- coding: utf-8 -*-
"""删除 SOURCES 闭合前误留的孤儿行 `        "kind": "primary",`。"""
lines = open("config.py", encoding="utf-8").read().split("\n")
out = []
i = 0
removed = 0
while i < len(lines):
    cur = lines[i]
    nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
    # 孤儿判定：本行是 `        "kind": "primary",` 且下一行是 SOURCES 闭合 `}`
    if cur.strip() == '"kind": "primary",' and nxt == "}":
        removed += 1
        i += 1
        continue
    out.append(cur)
    i += 1
open("config.py", "w", encoding="utf-8").write("\n".join(out))
print(f"删除孤儿行: {removed}")
