# -*- coding: utf-8 -*-
"""Read all_enterprises.json, group overseas enterprises by serial, split into chunk files
for HY3 translation. Each chunk file: {serial: {name, description, business_model}}.
Also includes any domestic with English name (already handled in prep, but name_cn todo remains)."""
import json, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enterprise")
data = json.load(open(os.path.join(BASE, "all_enterprises.json"), encoding='utf-8'))

# group needed fields by serial from todo list
todo = json.load(open(os.path.join(BASE, "_todo_translate.json"), encoding='utf-8'))
by_serial = {}
for t in todo:
    s = t['serial']
    by_serial.setdefault(s, {'name': '', 'description': '', 'business_model': ''})
    if t['field'] == 'name_cn':
        by_serial[s]['name'] = t['text']
    elif t['field'] == 'desc_cn':
        by_serial[s]['description'] = t['text']
    elif t['field'] == 'business_model_cn':
        by_serial[s]['business_model'] = t['text']

serials = list(by_serial.keys())
print("total serials to translate:", len(serials))

CHUNK = 90
outdir = os.path.join(BASE, "_chunks")
os.makedirs(outdir, exist_ok=True)
for i in range(0, len(serials), CHUNK):
    chunk = serials[i:i+CHUNK]
    obj = {s: by_serial[s] for s in chunk}
    path = os.path.join(outdir, f"chunk_{i//CHUNK:02d}.json")
    json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("wrote", (len(serials)+CHUNK-1)//CHUNK, "chunk files to", outdir)
