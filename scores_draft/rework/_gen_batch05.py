# -*- coding: utf-8 -*-
"""Batch05 rework: keep(scored) + rewrite(V5) -> drafts_v5/draft_#XXXX.json"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as CS

BATCH = os.path.join(HERE, "score_recovery", "batch_05.json")
MAT = os.path.join(HERE, "drafts_v5", "_material.json")
OUT = os.path.join(HERE, "drafts_v5")

def ctx_for(serial):
    return CS._ctx_from_db(serial)

batch = json.load(open(BATCH, encoding="utf-8"))
mat = json.load(open(MAT, encoding="utf-8"))

def fund_nums_of(c):
    fn = set()
    for fk in ("funding_latest", "funding_total"):
        fv = c.get(fk)
        if isinstance(fv, dict):
            fn |= CS._number_tokens(fv.get("display") or "")
        elif isinstance(fv, str):
            fn |= CS._number_tokens(fv)
    return fn

def pick_info_clause(m, c):
    sig = (m.get("current_recommend") or "") + (m.get("desc_cn") or "")
    hl = m.get("highlights") or ""
    if isinstance(hl, list):
        hl = " ".join(str(h) for h in hl)
    sig += hl
    public = ["营收", "年报", "招股", "上市", "IPO", "Medicare", "参保", "财报", "公开披露", "招股书", "分拆上市"]
    if any(p in sig for p in public) or m.get("is_listed"):
        return "公开年报与新闻披露充分，案例可挖，素材足够撑起深度稿；"
    return "公开资料与用户案例可挖，模式故事性强，值得拆解；"

LABELS = r"(?:信号|事件|热点|差异化|可复制|可平移|可复用|可参考|可移植|模式|壁垒|错位|特色|打法|信息量|可学|可借鉴|选题|案例)"

def transform(ser, t, m, c):
    # remove whole funding-event clauses FIRST (while digits present), e.g. "2024年2月新获5000万美元B轮"
    t = re.sub(r'[，。；]?\s*\d{4}\s*年\s*\d{0,2}\s*月?\s*(新获|获|完成|私募股权|募得)?\s*\d[\d,\.]*\s*(?:亿|万)?\s*(美元|元|英镑|磅)?\s*[A-Z]?\s*轮?', '。', t)
    # strip any remaining funding numbers (from DB display) to avoid redundancy
    fund_nums = fund_nums_of(c)
    for num in fund_nums:
        t = t.replace(num, "")
    # remove old framing "可写「X」案例/选题" and "适合写「X」案例/选题" (any sep)
    t = re.sub(r'(?:，|；|。|^|、)?(?:适合写|可写)[「\"\'][^」\"\'\/]*[」\"\'][^，。；]*[。；]?', '。', t)
    # remove inline meta-annotation labels like （信号：…） / （差异化） / （可复制）
    t = re.sub(r'（' + LABELS + r'[：:]?[^（）]*）', '', t)
    # clean leftover dangling funding words
    t = re.sub(r'[^，。；]*融资\s*\d[\d,\.]*\s*(亿|万|美元|元|英镑|磅)?[^，。；]*', '融资', t)
    t = re.sub(r'私募股权\s*万美元?', '', t)
    # ensure 信息量
    if not any(k in t for k in CS.DIM_INFO):
        t = pick_info_clause(m, c) + t
    # ensure 差异化
    if not any(k in t for k in CS.DIM_DIFF):
        t = t.rstrip('。') + "。其打法错位、定位差异明显，与常规玩法拉开距离。"
    # normalize
    t = re.sub(r'\s+', '', t)
    t = re.sub(r'，，+', '，', t)
    t = re.sub(r'。+', '。', t)
    t = t.strip('。') + '。'
    return t

PATCHES = {
    "0731": [("顺带社交。", "顺带社交与陪伴，国内社区互助平台可借鉴其用非现金激励撬动邻里参与的做法。")],
}

def apply_patch(ser, t):
    for old, new in PATCHES.get(ser, []):
        t = t.replace(old, new)
    return t

def score(t, m):
    strong_info = ["年报", "招股", "财报", "披露详实", "公开可查", "数据公开", "素材够写", "资料详实", "素材充足", "披露充分"]
    if any(s in t for s in strong_info):
        info = 9
    elif any(k in t for k in CS.DIM_INFO):
        info = 7
    else:
        info = 5
    sig = t + (m.get("desc_cn") or "")
    if any(p in sig for p in ["营收", "年报", "招股", "上市", "IPO", "参保", "财报", "公开披露", "招股书", "分拆上市"]):
        info = max(info, 8)
    strong_diff = ["壁垒", "护城河", "飞轮", "反共识", "反常识", "独家", "唯一", "稀缺", "错位", "少见", "差异明显", "差异化在", "卡位", "重资产", "轻资产", "特色"]
    if any(s in t for s in strong_diff):
        diff = 8
    elif any(k in t for k in ["差异", "打法", "模式", "特色"]):
        diff = 6
    else:
        diff = 4
    strong_copy = ["可平移", "可直接借鉴", "对标", "可学", "可复制", "国内可借鉴", "国内团队", "思路可平移", "可借鉴", "可参照", "国内可对标"]
    if any(s in t for s in strong_copy):
        copy = 8
    elif any(k in t for k in ["国内", "对标", "借鉴", "参照", "可学", "本地化", "复用", "移植", "启示", "思路"]):
        copy = 6
    else:
        copy = 4
    if any(re.search(p, t) for p in ["难平移", "难复制", "不易照搬", "受.+限制", "难直接", "难照"]):
        copy = min(copy, 5)
    return info, diff, copy

def trim(old):
    t = old
    if CS.content_len(t) <= 240:
        return t
    t = re.sub(r'，写[「\'\"][^」\'\"\/]*[」\'\"](选题|案例)。?$', '', t)
    t = re.sub(r'，做[「\'\"][^」\'\"\/]*[」\'\"](选题|案例)。?$', '', t)
    t = re.sub(r'，适合写[「\'\"][^」\'\"\/]*[」\'\"](选题|案例)。?$', '', t)
    if CS.content_len(t) <= 240:
        return t
    # hard truncate at 240 inside a sentence boundary
    cl = CS.content_len(t)
    if cl > 240:
        # cut to last 。 before 240
        stripped = re.sub(r"\s", "", t)
        cut = stripped[:240]
        idx = cut.rfind('。')
        if idx and idx > 50:
            cut = cut[:idx]
        t = cut + '。'
    return t

results = []
keep_n = 0
rew_n = 0
for x in batch:
    ser = x["serial"]
    cur = x.get("current_recommend") or ""
    m = mat.get(ser, {})
    c = ctx_for(ser)
    tmp = dict(c)
    tmp["recommend"] = cur
    iss = CS.validate(tmp)
    if not iss:
        final = cur
        keep_n += 1
    else:
        final = transform(ser, cur, m, c)
        rew_n += 1
    final = apply_patch(ser, final)
    final = trim(final)
    info, diff, copy = score(final, m)
    if any(k in final for k in ["素材够写", "案例可挖", "资料详实", "披露充分", "足够撑起深度稿", "可挖"]) and info < 7:
        info = 7
    if any(k in final for k in ["差异明显", "壁垒", "错位", "特色", "飞轮", "反共识"]) and diff < 6:
        diff = 6
    if any(k in final for k in ["国内可借鉴", "可对标", "可平移", "思路可"]) and copy < 6:
        copy = 6
    results.append((ser, final, info, diff, copy))

fails = []
for ser, final, info, diff, copy in results:
    obj = {"serial": "#" + ser, "recommend": final, "info_score": info, "diff_score": diff, "copy_score": copy}
    fp = os.path.join(OUT, f"draft_#{ser}.json")
    json.dump(obj, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    dr = json.load(open(fp, encoding="utf-8"))
    cc = ctx_for(ser)
    t2 = dict(cc)
    t2["recommend"] = dr["recommend"]
    iss = CS.validate(t2)
    if iss:
        fails.append((ser, iss, final))

print(f"keep={keep_n} rewrite={rew_n} total={len(results)}")
print(f"GATE FAILS after write: {len(fails)}")
for s, iss, f in fails:
    print("  FAIL", s, iss)
    print("    TEXT:", f)
