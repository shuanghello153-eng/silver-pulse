# -*- coding: utf-8 -*-
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

SAFE = ("recommend", "desc_cn", "silver_reason", "payor_model")

def main():
    # valid serials from CURRENT batch files
    valid = set()
    batch_of = {}
    for b in ['024','025','026','027']:
        try:
            d = json.load(open(f'batches_full/batch_src_{b}.json', encoding='utf-8'))
        except Exception as ex:
            print('batch load err', b, ex); continue
        for e in d:
            valid.add(e['serial']); batch_of[e['serial']] = (b, d)
    files = sorted(glob.glob(os.path.join(HERE, 'drafts_v4', 'draft_*.json')))
    drafts = {}
    for fp in files:
        dr = json.load(open(fp, encoding='utf-8'))
        if dr['serial'] in valid:
            drafts[dr['serial']] = dr
    others = [dr.get('recommend','') for dr in drafts.values()]
    fails = 0
    for s, dr in sorted(drafts.items()):
        b, d = batch_of[s]
        e = next((x for x in d if x['serial']==s), None)
        tmp = dict(e)
        for k in SAFE:
            if k in dr and dr[k] is not None:
                tmp[k] = dr[k]
        iss = C.validate(tmp, others=others, skip={'R10'})
        if iss:
            print(f'{s}: FAIL {iss}'); fails += 1
        else:
            print(f'{s}: PASS')
    print(f'\nChecked {len(drafts)} (mine) | FAIL {fails}')

if __name__ == '__main__':
    main()
