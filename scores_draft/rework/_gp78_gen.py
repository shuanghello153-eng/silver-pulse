# -*- coding: utf-8 -*-
"""general-purpose-78: batch_60 V5 rework.
- _is_v5_already=True: keep current_recommend, supply integer info/diff/copy (AI 三维精评).
- _is_v5_already=False (#1047): rewrite recommend (editorial layer, 3 dims, 50-240 chars) + score.
Output: drafts_v5/draft_#XXXX.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "batches_score", "batch_60.json")
OUT = os.path.join(HERE, "drafts_v5")

# serial -> (info, diff, copy)  integer 0~10 refined scores
SCORES = {
    "#0939": (6, 7, 6),
    "#0942": (6, 7, 5),
    "#0943": (6, 8, 6),
    "#0955": (6, 7, 6),
    "#1018": (6, 7, 6),
    "#1026": (6, 7, 6),
    "#1028": (6, 7, 6),
    "#1046": (6, 7, 6),
    "#1047": (6, 7, 6),
    "#1048": (6, 8, 6),
    "#1049": (6, 7, 6),
    "#1050": (6, 8, 6),
    "#1051": (7, 8, 5),
    "#1052": (7, 8, 6),
    "#1053": (7, 7, 6),
    "#1054": (7, 7, 6),
    "#1058": (7, 7, 6),
    "#1103": (8, 8, 5),
    "#1113": (8, 7, 5),
    "#1123": (7, 7, 6),
}

# #1047 Axena Health rewrite (editorial layer; no funding/scale; covers 信息量+差异化+可复制;
# avoids 企业名, avoids absolute 国内空白, 50-240 chars)
REWRITE = {
    "#1047": ("把处方级盆底训练做成居家非侵入系统，差异在卡位被忽视的老年女性失禁细分、走"
              "家用消费化而非院内设备，错位多数盆底方案只做医疗场景。素材可挖：其临床验证"
              "居家可练的数据、与国内麦澜德和伟思医疗（偏院内）的对比都具故事性，反共识点"
              "是失禁干预能消费化。国内麦澜德、伟思医疗做盆底偏院内，可借鉴其'家用非侵入加"
              "处方背书'的打法，把银发女性健康从医院搬到客厅。"),
}

def main():
    d = json.load(open(SRC, encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    for r in d:
        s = r["serial"]
        rec = r.get("current_recommend")
        if s in REWRITE:
            rec = REWRITE[s]
        assert isinstance(rec, str), f"{s} no recommend"
        info, diff, copy = SCORES[s]
        out = {"serial": s, "recommend": rec, "info": info, "diff": diff, "copy": copy}
        with open(os.path.join(OUT, f"draft_{s}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("wrote", f"draft_{s}.json", info, diff, copy)

if __name__ == "__main__":
    main()
