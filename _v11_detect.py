# -*- coding: utf-8 -*-
"""
v11 聚类规则自检/检测方法 (2026-07-12)
用途: 对 v11 落库结果做"语义精度"与"伞词剥离"双向校验, 作为独立教研智能体的基础工具。

检测维度:
  1) 新标签精度: 5 个新标签(纸尿裤/轮椅/护理床/家政生活服务/陪诊)的每个成员,
     其 name+description 必须命中至少 1 个种子词(含同类词), 否则判为潜在误标。
  2) 伞词剥离反向校验: 若企业已有具体标签, 不应残留伞词(UMBRELLA_TO_STRIP);
     若企业 tag_l2 仅含伞词, 单独列出(属 v11 设计上"冻结残留", 非错误)。
  3) L1 映射校验: 5 个新标签的 L1 归属必须与 seeds bank / CANON 一致。
  4) 智慧养老残留: 报告成员数与被具体标签覆盖的比例。

只读, 不改动任何文件。
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data/enterprise/all_enterprises.json')
BANK = os.path.join(ROOT, 'output/seeds_bottomup_v2.json')
SYN  = os.path.join(ROOT, 'data/enterprise/tag_synonyms.json')

# 与 _rebuild_tags.py v11 块 UMBRELLA_TO_STRIP 保持一致(单一真相, 改动需同步两处)。
# 注意: 智能硬件/健康监测/机器人 是合法具体叶子标签, 不在剥离集。
UMBRELLA_TO_STRIP = {'智慧养老','居家护理','养老社区','康复设备','投资机构','保健品','AI',
                     '社交','平台','营养食品','认知症','适老化改造','医疗器械',
                     '慢病管理','保险','养老金融','护理平台','临终关怀','医疗'}

NEW_TAGS = ['纸尿裤','轮椅','护理床','家政生活服务','陪诊']
NEW_TAG_L1 = {'纸尿裤':'消费品','轮椅':'康复辅具','护理床':'康复辅具',
              '家政生活服务':'养老服务','陪诊':'养老服务'}


def load():
    data = json.load(open(DATA, encoding='utf-8'))
    bank = json.load(open(BANK, encoding='utf-8'))
    try:
        syn = json.load(open(SYN, encoding='utf-8'))
    except Exception:
        syn = {}
    return data, bank, syn


def text_of(e):
    return ((e.get('name_cn') or e.get('name') or '') + ' ' +
            (e.get('description') or e.get('desc_cn') or '')).lower()


def tokens_for(tag, bank, syn):
    """新标签命名词集合 = bank seed ∪ 同类词(synonyms)"""
    toks = set()
    info = bank.get(tag)
    if isinstance(info, dict):
        for s in (info.get('seed') or []):
            toks.add(s.lower())
    # synonyms: 可能是 {canon:[...]} 或 {syn:canon}
    if isinstance(syn, dict):
        if tag in syn and isinstance(syn[tag], list):
            for s in syn[tag]:
                toks.add(s.lower())
        else:
            for k, v in syn.items():
                if v == tag:
                    toks.add(k.lower())
    return toks


def main():
    data, bank, syn = load()
    report = {'precision': {}, 'residual_umbrella': [], 'only_umbrella': [],
              'l1_mismatch': [], 'zhly_residual': {}}
    print('=' * 70)
    print('v11 聚类规则自检报告')
    print('=' * 70)
    print(f'企业总数: {len(data)}')

    # ---- 1) 新标签精度 ----
    print('\n[1] 新标签精度检测 (命中种子词/同类词)')
    for tag in NEW_TAGS:
        toks = tokens_for(tag, bank, syn)
        members = [e for e in data if tag in e.get('tag_l2', [])]
        fp = []
        for e in members:
            t = text_of(e)
            if not any(k in t for k in toks):
                fp.append(e.get('name_cn') or e.get('name'))
        prec = (len(members) - len(fp)) / len(members) * 100 if members else 100.0
        report['precision'][tag] = {
            'members': len(members), 'false_positives': fp, 'precision_pct': round(prec, 1)}
        print(f'  {tag}: 成员 {len(members)} | 精度 {prec:.1f}% | 潜在误标 {len(fp)}')
        for n in fp:
            print(f'      ⚠ 误标嫌疑: {n}')
    total_fp = sum(len(v['false_positives']) for v in report['precision'].values())
    print(f'  >> 新标签合计潜在误标: {total_fp}')

    # ---- 2) 伞词剥离反向校验 ----
    print('\n[2] 伞词剥离反向校验')
    for e in data:
        tags = e.get('tag_l2', [])
        if not tags:
            continue
        has_specific = any(t not in UMBRELLA_TO_STRIP for t in tags)
        has_umbrella = any(t in UMBRELLA_TO_STRIP for t in tags)
        if has_specific and has_umbrella:
            report['residual_umbrella'].append({
                'name': e.get('name_cn') or e.get('name'), 'tags': tags})
        if has_umbrella and not has_specific:
            report['only_umbrella'].append({
                'name': e.get('name_cn') or e.get('name'), 'tags': tags})
    print(f'  有具体标签却残留伞词: {len(report["residual_umbrella"])} 家')
    for r in report['residual_umbrella'][:30]:
        print(f'      ⚠ {r["name"]}: {r["tags"]}')
    print(f'  仅含伞词(冻结残留, 非错误): {len(report["only_umbrella"])} 家')

    # ---- 3) L1 映射校验 ----
    print('\n[3] 新标签 L1 映射校验')
    for tag in NEW_TAGS:
        expect = NEW_TAG_L1[tag]
        bad = []
        for e in data:
            if tag in e.get('tag_l2', []) and expect not in e.get('tag_l1', []):
                bad.append(e.get('name_cn') or e.get('name'))
        report['l1_mismatch'].append({'tag': tag, 'expect_l1': expect, 'bad': bad})
        if bad:
            print(f'  ⚠ {tag} 期望 L1={expect}, 缺失企业: {bad}')
        else:
            print(f'  ✓ {tag} -> {expect} 全部一致')

    # ---- 4) 智慧养老残留 ----
    print('\n[4] 智慧养老残留')
    zh = [e for e in data if '智慧养老' in e.get('tag_l2', [])]
    covered = sum(1 for e in zh if any(t not in UMBRELLA_TO_STRIP for t in e.get('tag_l2', [])))
    report['zhly_residual'] = {'total': len(zh), 'with_specific': covered}
    print(f'  智慧养老成员: {len(zh)} | 其中已被具体标签覆盖: {covered} | 纯残留: {len(zh)-covered}')

    # ---- 汇总 ----
    print('\n' + '=' * 70)
    print('汇总')
    print('=' * 70)
    ok = (total_fp == 0 and len(report['residual_umbrella']) == 0
          and all(not r['bad'] for r in report['l1_mismatch']))
    print(f'  新标签误标: {total_fp}')
    print(f'  伞词残留(应剥离却未): {len(report["residual_umbrella"])}')
    print(f'  L1 映射错误: {sum(len(r["bad"]) for r in report["l1_mismatch"])}')
    print(f'  结论: {"✓ 全部通过" if ok else "⚠ 存在需复核项(见上)"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
