# -*- coding: utf-8 -*-
"""步骤2：把粗筛疑似重复对逐一拉出来对比（候选 vs 库内），供 AI 裁决"""
import json, os, sys, io, re, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

# 重跑粗筛拿到结构化结果
r = subprocess.run([sys.executable, 'scores_draft/rework/dedup_keyword_prescreen.py',
                    '--candidates', '_qa_tmp/ingest_187/screened_candidates.json'],
                   capture_output=True, text=True, encoding='utf-8')
txt = r.stdout

cands = {c['name']: c for c in json.load(open('_qa_tmp/ingest_187/screened_candidates.json', encoding='utf-8'))}
lib = json.load(open('data/enterprise/all_enterprises.json', encoding='utf-8'))
by_serial = {e.get('serial'): e for e in lib}

cur = None
pairs = {}
for line in txt.splitlines():
    m = re.match(r'## ⚠️  · (.+?)（核心词', line)
    if m:
        cur = m.group(1)
        pairs[cur] = []
        continue
    m2 = re.match(r'- 疑似重复 → (#\d+) (.+)', line)
    if m2 and cur:
        pairs[cur].append((m2.group(1), m2.group(2).strip()))

print('疑似重复对：', len(pairs))
for name, hits in pairs.items():
    c = cands.get(name, {})
    print('=' * 70)
    print(f"候选: {name} [{c.get('batch','')[:8]}] {c.get('website','')}")
    print(f"  业务: {c.get('business','')[:100]} | 国家: {c.get('country','')}")
    for serial, libname in hits:
        e = by_serial.get(serial, {})
        print(f"  库内 {serial} {libname} | {e.get('website_url','')}")
        print(f"    desc: {str(e.get('description',''))[:100]}")
