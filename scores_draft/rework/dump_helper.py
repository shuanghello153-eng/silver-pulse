# -*- coding: utf-8 -*-
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

def dump(batch, idxs):
    d = json.load(open(f'batches_full/{batch}', encoding='utf-8'))
    for i in idxs:
        e = d[i]
        print("="*70)
        print(f"[{i}] {e['serial']} | {e.get('name_cn','')} / {e.get('name','')}")
        print("tags:", e.get('tag_l1'), e.get('tag_l2'), "| region:", e.get('region'), "| stage:", e.get('stage'))
        print("desc_cn:", e.get('desc_cn',''))
        print("silver_reason:", e.get('silver_reason',''))
        print("highlights:", e.get('highlights'))
        fl = e.get('funding_latest') or {}
        ft = e.get('funding_total') or {}
        print("funding_latest.display:", fl.get('display') if isinstance(fl,dict) else fl)
        print("funding_total.display:", ft.get('display') if isinstance(ft,dict) else ft)
        print("payor_model:", e.get('payor_model'), "| source:", e.get('source'))
        sc = {k:e.get(k) for k in ['signal_strength','info_score','diff_score','copy_score','research_value']}
        print("scores:", sc)
        print("recommend(原):", e.get('recommend',''))
        print()

if __name__ == "__main__":
    batch = sys.argv[1]
    idxs = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else list(range(20))
    dump(batch, idxs)
