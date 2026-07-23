"""
清洗飞书供需表导入的脏数据（173家）。
两类处理：
  Type A (50家): description前半段有正经内容→截取【提供资源】之前的部分
  Type B (123家): 截后太短→基于名称+标签+highlights+funding等字段合成新介绍

同时清洗 desc_cn 中同类脏标记。
"""
import json, re, sys

DB_PATH = 'data/enterprise/all_enterprises.json'
DIRTY_MARKERS = ['【提供资源】', '【需求数源】', '【供需】', '【邀请函】']
AGECLUB_SUFFIX = re.compile(r'\s*（AgeClub供需对接补充[：:].*?$')
MIN_DESC_LEN = 25


def find_first_marker_pos(text):
    """返回第一个脏标记的位置，无标记返回 -1"""
    pos = len(text)
    for m in DIRTY_MARKERS:
        idx = text.find(m)
        if 0 <= idx < pos:
            pos = idx
    return pos if pos < len(text) else -1


def clean_text(text):
    """基础文本清洗：去多余空白、去 AgeClub 后缀、去编号前缀"""
    text = text.strip()
    # 去 AgeClub 补充后缀
    text = AGECLUB_SUFFIX.sub('', text).strip()
    # 去掉开头的 "1、" "2、" 等编号列表（有些是复制粘贴带进来的）
    text = re.sub(r'^[\d]+[、.．\s]+', '', text).strip()
    # 压缩连续换行和空格
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def build_desc_from_fields(e, clean_seed):
    """当截取后太短时，基于原始短描述种子+其他字段合成介绍。
    
    策略：clean_seed 是企业自己写的原始描述（可能只有5-20字），
    这是真实信息，比任何模板都有价值。在此基础上用标签补充上下文。
    """
    name = e.get('name', '')
    tag_l2 = e.get('tag_l2', []) or []
    tag_l1 = e.get('tag_l1', []) or []
    
    # 1. 用 clean_seed 作为核心（去掉无意义短语）
    seed = clean_seed.strip()
    # 去掉纯无信息的 seed
    meaningless = ['有团队', '大健康', '自媒体', '持续关注', '无', '流量',
                   '居家', '技术', '资金', '服务', '客户', '渠道', '资源整合',
                   '认识银发人群', '保司ziy', '未披露', '关注']
    if seed in meaningless or len(seed) <= 2:
        seed = ''
    
    # 2. highlights（仅当有真实内容时使用）
    h = e.get('highlights')
    hl_text = ''
    if h:
        if isinstance(h, list) and h and h[0] not in ('未搜到', '', None):
            hl_text = str(h[0])[:150]
        elif isinstance(h, str) and h not in ('未搜to', ''):
            hl_text = h[:150]
    
    # 3. funding（仅当有真实数据时）
    fl = e.get('funding_latest')
    fin_text = ''
    if isinstance(fl, dict):
        amount = fl.get('amount', '') or ''
        round_info = fl.get('round', '') or ''
        investors = fl.get('investors', '') or ''
        if amount and amount not in ('未披露', '未知', ''):
            fin_text = f"获{round_info}融资{amount}"
            if investors and investors not in ('未披露', ''):
                fin_text += f"（{investors}）"
    
    # === 组装 ===
    parts = []
    if seed:
        parts.append(seed)
    if hl_text:
        parts.append(hl_text)
    if fin_text:
        parts.append(fin_text)
    
    if parts:
        result = '。'.join(parts)
        if not result.endswith(('。', '！', '？')):
            result += '。'
        
        # 如果还是太短但有真实种子，用标签补充
        if len(result) < 20:
            tag_ctx = '、'.join(tag_l2[:2]) if tag_l2 else ''
            if tag_ctx:
                result += f"涉及{tag_ctx}领域。"
    else:
        # 真的没有任何信息——标记为信息不足
        tag_ctx = '、'.join(tag_l2[:2]) if tag_l2 else '、'.join(tag_l1[:1]) if tag_l1 else '银发经济相关'
        result = f"信息不足：仅公开名称与赛道（{tag_ctx}），无公开规模、营收或投融资数据。"
    
    return result


def main():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    stats = {'trimmed': 0, 'rewritten': 0, 'already_clean': 0, 'desc_cn_cleaned': 0}
    changes = []
    
    for e in db:
        serial = e.get('serial', '')
        name = e.get('name', '')
        
        # === 处理 description ===
        desc = e.get('description', '')
        marker_pos = find_first_marker_pos(desc)
        
        if marker_pos >= 0:
            clean_part = clean_text(desc[:marker_pos])
            
            if len(clean_part) > MIN_DESC_LEN:
                # Type A: 截取
                e['description'] = clean_part
                stats['trimmed'] += 1
                changes.append(f"{serial} {name}: TRIMMED ({len(desc)}→{len(clean_part)})")
            else:
                # Type B: 基于短种子+字段合成
                new_desc = build_desc_from_fields(e, clean_part)
                e['description'] = new_desc
                stats['rewritten'] += 1
                changes.append(f"{serial} {name}: REWRITTEN ({len(desc)}→{len(new_desc)})")
        else:
            stats['already_clean'] += 1
        
        # === 处理 desc_cn（同步清洗）===
        dc = e.get('desc_cn', '')
        if isinstance(dc, str):
            dc_marker = find_first_marker_pos(dc)
            if dc_marker >= 0:
                dc_clean = clean_text(dc[:dc_marker])
                if len(dc_clean) > MIN_DESC_LEN:
                    e['desc_cn'] = dc_clean
                else:
                    e['desc_cn'] = e['description']  # 回填 description
                stats['desc_cn_cleaned'] += 1
    
    # 写回
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"=== 清洗完成 ===")
    print(f"总企业数: {len(db)}")
    print(f"Type A (截取): {stats['trimmed']}")
    print(f"Type B (重写): {stats['rewritten']}")
    print(f"无需处理: {stats['already_clean']}")
    print(f"desc_cn 同步清洗: {stats['desc_cn_cleaned']}")
    print()
    print("=== 变更清单(前30条) ===")
    for c in changes[:30]:
        print(f"  {c}")
    if len(changes) > 30:
        print(f"  ... 还有 {len(changes)-30} 条")
    
    # 验证：确认没有遗漏的脏标记
    remaining = 0
    for e in db:
        d = e.get('description', '')
        if any(m in d for m in DIRTY_MARKERS):
            remaining += 1
            print(f"  ⚠️ 遗漏: {e['serial']} {e.get('name','')}")
    print(f"\n残留脏标记: {remaining} (应为0)")


if __name__ == '__main__':
    main()
