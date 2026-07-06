#!/usr/bin/env python3
"""Batch 9: Fill highlights for enterprises that have description but no highlights."""
import json

DATA_FILE = r'G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\all_enterprises.json'

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gen_highlight(desc, cat_l1, cat_l2):
    """Generate a short highlight from description."""
    if not desc:
        return f'{cat_l1}领域企业'
    
    # 从description中提取关键短语
    # 如果desc以品牌名开头，取第一个逗号后的内容
    parts = desc.split('，')
    if len(parts) > 1:
        # 取第二部分作为highlights（通常是核心定位）
        highlight = parts[1].strip()
        if len(highlight) > 40:
            highlight = highlight[:38] + '...'
        return highlight
    
    # 截取description前30字
    if len(desc) > 40:
        return desc[:38] + '...'
    return desc

if __name__ == '__main__':
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    for e in data:
        if not e.get('highlights') and e.get('description'):
            highlight = gen_highlight(e['description'], e.get('category_l1', ''), e.get('category_l2', ''))
            e['highlights'] = highlight
            updated += 1
    
    print(f'Updated highlights: {updated}')
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Saved successfully.')
