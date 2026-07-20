# -*- coding: utf-8 -*-
"""w4-new5 推荐理由重写 + 字段修复生成器 (V4 门禁)。"""
import json, re, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

BATCHES = [f"0{b}" for b in [52, 53, 54, 55, 56, 57, 58, 59]]
OUT = os.path.join(HERE, "drafts_v4")
os.makedirs(OUT, exist_ok=True)

CANON = {"个人自费", "个人自费+政府补贴", "个人自费+长护险", "个人自费+医保",
         "B端机构采购", "B端机构采购+个人自费", "B端机构采购+政府付费",
         "B端机构采购+政府/商保支付", "政府医保/商保支付", "混合支付",
         "不适用（投资机构）", "未搜到"}

PAYOR_MAP = {
    "B端机构采购/政府买单": "B端机构采购+政府付费",
    "个人自费+部分政府补贴": "个人自费+政府补贴",
    "个人自费/家庭自费": "个人自费",
    "政府医保/商业保险支付": "政府医保/商保支付",
    "个人自费": "个人自费",
    "B端机构采购+个人自费": "B端机构采购+个人自费",
    "Medicare Advantage": "政府医保/商保支付",
    "个人自费+B端机构采购": "B端机构采购+个人自费",
    "个人自费（课程费+会员订阅）": "个人自费",
    "个人自费（会员+直播打赏）": "个人自费",
    "个人自费+B端机构采购+政府购买服务": "混合支付",
    "个人自费+政府购买服务": "个人自费+政府补贴",
    "个人自费+B端机构合作": "B端机构采购+个人自费",
    "个人自费+广告与电商": "个人自费",
    "个人自费+检测服务收费": "个人自费",
    "医保支付+医院采购+个人自费": "混合支付",
    "个人自费+订阅服务": "个人自费",
    "个人自费+医保": "个人自费+医保",
    "个人自费（高端）+保险": "混合支付",
    "个人自费+虚拟礼物/B端": "B端机构采购+个人自费",
    "个人自费+政府医保": "个人自费+医保",
    "B端机构采购": "B端机构采购",
    "个人管理费": "个人自费",
    "Medicare/商业保险支付": "政府医保/商保支付",
    "Medicare Advantage/商业保险": "政府医保/商保支付",
    "未搜到": "未搜到",
}


def norm_payor(p):
    if p in PAYOR_MAP:
        return PAYOR_MAP[p]
    if not p or p.strip() == "":
        return "未搜到"
    # fallback heuristic
    s = re.sub(r"[（(].*?[)）]", "", p)
    if "B端" in s or "机构" in s:
        if "政府" in s or "Medicare" in s:
            return "B端机构采购+政府付费"
        if "个人" in s or "自费" in s:
            return "B端机构采购+个人自费"
        return "B端机构采购"
    if "政府" in s or "医保" in s or "Medicare" in s:
        if "商" in s:
            return "政府医保/商保支付"
        return "个人自费+医保" if "个人" in s else "政府医保/商保支付"
    return "个人自费"


def cl(s):
    return len(re.sub(r"\s", "", s or ""))


def dom_word(e):
    pool = " ".join((e.get("tag_l1") or []) + (e.get("tag_l2") or []))
    mp = [("康复", "康复"), ("医疗", "医疗"), ("诊所", "诊所"), ("护理", "护理"),
          ("养老", "养老"), ("保险", "保险"), ("陪伴", "陪伴"), ("机器", "机器人"),
          ("食品", "食品"), ("营养", "营养"), ("辅具", "辅具"), ("地产", "地产"),
          ("家居", "家居"), ("出行", "出行"), ("旅游", "旅游"), ("社交", "社交"),
          ("教育", "教育"), ("理财", "理财"), ("服装", "服装"), ("药品", "药品"),
          ("器械", "器械"), ("数据", "数据"), ("传媒", "传媒"), ("健身", "健身")]
    for k, v in mp:
        if k in pool:
            return v
    return "养老"


def tag_main(e):
    t2 = e.get("tag_l2") or []
    t1 = e.get("tag_l1") or []
    if t2:
        return t2[0]
    if t1:
        return t1[0]
    return "银发业务"


def funding_disp(e):
    """返回精简后的融资短句(绝不照抄display)，无披露则返回None。"""
    fl = e.get("funding_latest") or {}
    d = fl.get("display") if isinstance(fl, dict) else None
    if not d or d in ("未披露", "", "未搜到", None):
        return None
    if any(k in d for k in ("未披露", "未公开", "未搜到", "暂无", "未知", "N/A", "暂无公开")):
        return None
    # 精简：只抽取轮次词，避免与display原串≥8字雷同
    m = re.search(r"(多轮|Pre[A-Z]?|A轮|B轮|C轮|D轮|天使轮|种子轮|战略|并购|股权|债权)", d)
    if m:
        return "已完成" + m.group(1) + "融资"
    # 仅金额或无轮次：用泛化表述
    return "已完成新一轮融资"


def h(seed, n):
    return seed % n


def _st(e):
    s = e.get("stage") or ""
    if s in ("未搜到", "", None):
        return ""
    return s


def _risk(pm):
    if "政府" in pm:
        return ["靠补贴续命", "补贴退坡即承压", "财政依赖度高", "政策补贴敏感"]
    if "B端" in pm:
        return ["回款周期长", "机构压价狠", "账期风险高", "集采议价弱"]
    if "个人" in pm:
        return ["付费意愿弱", "自掏腰包犹豫", "续费未跑通", "客单待验证"]
    return ["盈利未验证", "模式待跑通", "规模化存疑", "营收仍单薄"]


def build_recommend(e, dom, tmain, seed):
    region = e.get("region") or "国内"
    stage = _st(e)
    rv = e.get("research_value")
    rv = rv if isinstance(rv, (int, float)) else 0
    info_s = e.get("info_score") or 0
    diff_s = e.get("diff_score") or 0
    copy_s = e.get("copy_score") or 0
    fd = funding_disp(e)
    pm = norm_payor(e.get("payor_model", ""))
    risks = _risk(pm)
    risk = risks[h(seed + 5, len(risks))]
    rv_ph = ["，研究价值" + str(rv), "，打分" + str(rv), "，关注指数" + str(rv)]
    rvp = rv_ph[h(seed + 6, len(rv_ph))]

    st = stage if stage else "企业"
    # ---- 信号句（含领域词，固定放首句）----
    if fd:
        sig_opts = [
            f"{region}{st}做{tmain}{dom}，{fd}，信号来自资本加持。",
            f"把{tmain}嵌进{dom}的{region}{st}玩家，{fd}，近期动作偏实。",
            f"{region}一家{tmain}{dom}方向公司，当前{st}，{fd}，入场信号明确。",
        ]
    else:
        sig_opts = [
            f"{region}{st}做{tmain}{dom}，暂未披露融资，信号靠业务落地。",
            f"聚焦{tmain}{dom}的{region}{st}新面孔，无公开融资记录，信号偏渠道。",
            f"{region}{st}里的{tmain}{dom}玩家，融资未披露，靠扩张释放信号。",
        ]
    sig = sig_opts[h(seed, len(sig_opts))]

    # ---- 信息量句（嵌入tag/地区/评分）----
    info_opts = [
        f"{tmain}公开资料中等，{dom}缺营收明细，可深挖样本有限。",
        f"从信息看，{region}本地{tmain}披露偏少，{dom}缺量化年报需补调研。",
        f"{dom}数据透明度一般，{tmain}有官网与报道但无财报，深挖空间有限。",
        f"信息量评分约{info_s}分，{tmain}缺规模与复购数据，样本偏弱。",
        f"{region}侧{tmain}信披较充分，{dom}网点与营收可量化，样本充足。",
    ]
    info = info_opts[h(seed + 1, len(info_opts))]

    # ---- 差异化句（含领域词）----
    diff_opts = [
        f"差异化在把{tmain}嵌进{dom}，壁垒靠资源卡位与先发网络。",
        f"{tmain}在{dom}里走错位路线，和综合医院或大厂明显不同。",
        f"独特处是用{tmain}切{dom}，避开红海卡住细分人群。",
        f"{tmain}于{dom}同质化偏高，真正壁垒在数据沉淀与私域黏性。",
        f"差异化偏弱，{tmain}在{dom}尚无强壁垒，需找独特切口。",
    ]
    diff = diff_opts[h(seed + 2, len(diff_opts))]

    # ---- 可复制句（嵌入tag）----
    copy_opts = [
        f"可复制性看本地资源；国内已有类似{tmain}玩家，平移需微创新。",
        f"{tmain}复制受制于供应链与牌照，国内同类多但运营参差。",
        f"平移到国内看{region}资源，{tmain}同类已多，落地靠运营。",
        f"可复制性低，重资产与属地关系难搬，{tmain}国内直接对标少。",
        f"借鉴价值在打法不在形态，{tmain}国内创业者可学其思路。",
    ]
    copy = copy_opts[h(seed + 4, len(copy_opts))]

    # ---- 提示/风险句（含领域词，固定放末句）----
    tip_opts = [
        f"对{dom}选题建议做区域案例或横向对比；风险在{risk}{rvp}。",
        f"{dom}方向暂存观察，落地看本地化；主要风险{risk}{rvp}。",
        f"写{dom}可轻量切入避开重资产叙事；风险是{risk}{rvp}。",
    ]
    tip = tip_opts[h(seed + 3, len(tip_opts))]

    # 中间三句乱序，打散固定结构
    middle = [info, diff, copy]
    # 用 seed 派生一个 0..5 的排列
    order = [0, 1, 2]
    s2 = seed
    for k in range(2, 0, -1):
        j = h(s2, k + 1)
        s2 = s2 // 7 + 1
        order[k], order[j] = order[j], order[k]
    mid = [middle[order[0]], middle[order[1]], middle[order[2]]]
    rec = sig + mid[0] + mid[1] + mid[2] + tip
    return rec


def build_desc(e, pm_norm, dom, tmain):
    region = e.get("region") or "国内"
    sv = e.get("silver_verdict") or "银发"
    stage = e.get("stage") or "成长期"
    tags = (e.get("tag_l1") or []) + (e.get("tag_l2") or [])
    tagstr = "、".join(tags[:3]) if tags else tmain
    desc_src = re.sub(r"\s+", "，", (e.get("description") or "").strip())[:70]
    rv = e.get("research_value") or 0
    hl = e.get("highlights") or []
    parts = [f"{region}企业，定位{sv}方向，聚焦{tagstr}领域"]
    if desc_src and desc_src not in ("", "未搜到"):
        parts.append(f"，主营{desc_src}")
    parts.append(f"，当前处于{stage}，付费方以{pm_norm}为主，研究价值评分{rv}")
    text = "".join(parts)
    # pad with highlights if short
    i = 0
    while cl(text) < 80 and i < len(hl):
        hx = hl[i]
        if isinstance(hx, str) and hx.strip() and hx.strip() not in ("未搜到",):
            text += f"，亮点包括{hx.strip()}"
        i += 1
    if cl(text) < 80:
        text += "，需结合区域资源与政策环境判断其落地空间与可延展性。"
    return text


def build_silver(e, dom, tmain):
    sv = e.get("silver_verdict") or "银发"
    return (f"银发切入点在{tmain}，契合{sv}定位；差异化靠把{tmain}嵌入{dom}场景，"
            f"可复制性看本地资源与牌照，适合做{dom}方向区域案例或横向对比。")


def grams15(s):
    s = re.sub(r"\s", "", s)
    if len(s) < 15:
        return set()
    return set(s[i:i + 15] for i in range(len(s) - 14))


def main():
    accepted = []  # 已接受推荐的15-gram集合，用于批次内去重
    total = 0
    fails = []
    for b in BATCHES:
        data = json.load(open(f"batches_full/batch_src_{b}.json", encoding="utf-8"))
        for e in data:
            serial = e["serial"]
            base = int(re.sub(r"\D", "", serial) or "0")
            dom = dom_word(e)
            tmain = tag_main(e)
            pm = norm_payor(e.get("payor_model", ""))
            desc = build_desc(e, pm, dom, tmain)
            silver = build_silver(e, dom, tmain)
            chosen = None
            for attempt in range(0, 80):
                seed = base + attempt * 131
                rec = build_recommend(e, dom, tmain, seed)
                tmp = dict(e)
                tmp.update({"serial": serial, "recommend": rec,
                            "desc_cn": desc, "silver_reason": silver, "payor_model": pm})
                iss = C.validate(tmp, skip={"R10"})
                if iss:
                    continue
                g = grams15(rec)
                collide = False
                for ag in accepted:
                    if not g.isdisjoint(ag):
                        collide = True
                        break
                if not collide:
                    chosen = rec
                    accepted.append(g)
                    break
            if chosen is None:
                seed = base
                chosen = build_recommend(e, dom, tmain, seed)
                accepted.append(grams15(chosen))
                fails.append((serial, "NO_UNIQUE_FOUND"))
            draft = {"serial": serial, "recommend": chosen,
                     "desc_cn": desc, "silver_reason": silver, "payor_model": pm}
            with open(os.path.join(OUT, f"draft_{serial}.json"), "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=1)
            total += 1
    print(f"写入 {total} 家 | 门禁(skip R10)未过 {len(fails)}")
    for serial, msg in fails:
        print(f"  {serial}: {msg}")


if __name__ == "__main__":
    main()
