#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, 'data/enterprise/all_enterprises.json'), encoding='utf-8'))

def desc_of(e, n=90):
    d = (e.get('description') or e.get('desc_cn') or e.get('desc_en') or '')
    d = d.replace('\n',' ')
    return d[:n]

tags = sys.argv[1:]
for tag in tags:
    members = [e for e in data if tag in e.get('tag_l2',[])]
    print(f'\n================= {tag}  ({len(members)} 家) =================')
    for e in sorted(members, key=lambda x:(x.get('name_cn') or x.get('name') or '')):
        nm = (e.get('name_cn') or e.get('name') or '')
        print(f'  · {nm}  | {desc_of(e)}')
