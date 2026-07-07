# -*- coding: utf-8 -*-
"""prep_translation.py (v2) — 准备翻译待办清单 + 回填已经是中文的字段(纯复制)。

规则: 任意字段若已含中文(CJK) -> 直接回填对应 _cn 字段(复制, 不调用模型, 不编造)。
      仅当字段为英文时才进入待 HY3 翻译清单。
输出:
  data/enterprise/_todo_translate.json : [{serial, field, text}]  (仅英文文本)
"""
import json, os, re

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enterprise")
SRC = os.path.join(BASE, "all_enterprises.json")

def cjk(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

data = load(SRC)
todo = []          # 需要 HY3 翻译的英文文本
copied = 0

for e in data:
    serial = e['serial']
    # name_cn
    nm = e.get('name', '')
    if not e.get('name_cn'):
        if cjk(nm):
            e['name_cn'] = nm
        else:
            todo.append({'serial': serial, 'field': 'name_cn', 'text': nm})
        if e.get('name_cn'):
            copied += 1
    # desc_cn
    desc = e.get('description', '')
    if not e.get('desc_cn') and desc:
        if cjk(desc):
            e['desc_cn'] = desc
        else:
            todo.append({'serial': serial, 'field': 'desc_cn', 'text': desc})
        if e.get('desc_cn'):
            copied += 1
    # business_model_cn
    bm = e.get('business_model', '')
    if not e.get('business_model_cn') and bm:
        if cjk(bm):
            e['business_model_cn'] = bm
        else:
            todo.append({'serial': serial, 'field': 'business_model_cn', 'text': bm})
        if e.get('business_model_cn'):
            copied += 1

with open(SRC, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open(os.path.join(BASE, "_todo_translate.json"), 'w', encoding='utf-8') as f:
    json.dump(todo, f, ensure_ascii=False, indent=1)

# 统计
import collections
by_field = collections.Counter(t['field'] for t in todo)
print("已复制(中文已是)字段数:", copied)
print("待 HY3 翻译的英文字段总数:", len(todo), dict(by_field))
