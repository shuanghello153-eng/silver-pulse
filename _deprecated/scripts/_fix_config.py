# -*- coding: utf-8 -*-
"""修复：上轮插入把 8 个新源误嵌进 age_uk 字典内，现移至 SOURCES 顶层。"""
lines = open("config.py", encoding="utf-8").read().split("\n")

# 定位 age_uk 起始
start = next(i for i, l in enumerate(lines) if l.strip().startswith('"age_uk":'))
# 括号配平找 age_uk 闭合 }
depth = 0; close = None
for i in range(start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0 and i > start:
        close = i; break
assert close is not None, "未找到 age_uk 闭合"

# 找到 age_uk 内 "kind": "primary", 行（其后即为误嵌的 8 个源）
kind_idx = next(i for i in range(start, close) if '"kind": "primary",' in lines[i])
nested = lines[kind_idx + 1: close]  # 8 个新源条目（含各自闭合）

# 重组：保留 age_uk 到 kind 行 + age_uk 闭合 } + 8 新源(顶层) + 其余
new_lines = lines[: kind_idx + 1] + [lines[close]] + nested + lines[close + 1:]

open("config.py", "w", encoding="utf-8").write("\n".join(new_lines))
print("修复完成：8 个新源已从 age_uk 内移至 SOURCES 顶层")
