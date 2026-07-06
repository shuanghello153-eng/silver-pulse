#!/usr/bin/env python3
"""Batch 10: Clean up empty fields - set None/empty to consistent values."""
import json

DATA_FILE = r'G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\all_enterprises.json'

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    data = load_data()
    
    updated = 0
    for e in data:
        changes = False
        
        # funding_latest: 如果为空，不设置（前端不展示）
        # funding_total: 如果为空，不设置
        
        # investors: 如果为空，设为空字符串
        if not e.get('investors'):
            e['investors'] = ''
            changes = True
        
        # founded: 如果为空，设为空字符串
        if not e.get('founded'):
            e['founded'] = ''
            changes = True
        
        # website_url: 如果为空，设为空字符串
        if not e.get('website_url'):
            e['website_url'] = ''
            changes = True
        
        # tags: 如果为空，设为空列表
        if not e.get('tags'):
            e['tags'] = []
            changes = True
        
        if changes:
            updated += 1
    
    print(f'Cleaned up: {updated} enterprises')
    save_data(data)
    print('Saved successfully.')
