# -*- coding: utf-8 -*-
"""
单条推荐理由硬门禁（V5 · 编辑视角版）

设计原则（2026-07-20 小爽明确后重写）：
  推荐理由(recommend)是「编辑判断层」——告诉小爽"这家为什么值得写深度稿、切口在哪、
  国内创业者能学什么"。它和企业卡片上已展示的其他字段(des_cn基础描述 / highlights
  ★编辑注 / 投融资金额 / 阶段上市状态 / 近期动态)是**同一屏**，所以：

  ★ 禁止重复列表已有信息：不复述融资额、不复述上市/被收购状态、不复述规模数字、
    不逐字抄 description / highlights。这些字段用户已经看过了，重复展示=看 2~3 遍。
  ★ 不做"换汤不换药"：把"50岁以上女性"改成"半百女性"也算重复，门禁用 4-gram 重合度
    抓近逐字抄，用"不出现融资数字/状态词"抓数据复述。

  门禁只做机械可判的检查；语义是否真有增量，靠写作时人工把关。不堆无意义规则。

用法：
  python check_single.py draft_#XXXX.json
  python check_single.py --batch batch_src.json
  (被 merge 脚本 import：from check_single import validate, lcs_len)

【规则清单】
  R1     recommend 必须是单字符串
  R2     字数 50~240（扫读舒适，不为凑字牺牲表达）
  R3     禁模板套话签名句 / 结构级正则（真敌人）
  R5     须覆盖三维度（信息量=素材可挖 / 差异化 / 可复制）——编辑视角。
          ★不要求"信号"维度：融资/收购/上市等事件已在列表投融资/阶段字段展示，
            禁止在推荐理由里复述（小爽 2026-07-20 明确）。
  R-name 禁重复企业名（列表已有）
  ★R-redundancy  禁重复列表字段：融资数字 / 阶段状态词 / 近逐字抄 description·highlights
  R-integrity    前后半段同一赛道（防拼接串内容）
  R-noabs         禁绝对化"国内空白"论断
  R-jargon        禁技术黑话/废话
  R6/R7/R8        合并时跳过（不写这些字段）
  R10             跨企业雷同（合并且单独跑）
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")

# ---- 四维度关键词（编辑视角：研究价值，不是数据复述） ----
# 信号：为什么"现在"值得写（趋势/政策/竞品动作/窗口），不是企业自己的融资
DIM_SIG = ["信号", "热点", "近期", "当下", "当前", "趋势", "风口", "政策", "新规",
           "窗口", "时机", "升温", "走高", "受关注", "刚", "新", "启动", "落地",
           "值得跟", "值得写", "可写", "选题", "赛道热", "需求起", "红利"]
# 信息量：有没有足够素材可挖（年报/招股书详实、模式有反共识点），不列具体数字
DIM_INFO = ["信息", "资料", "透明", "公开", "年报", "招股", "披露", "财报", "报道",
            "深度", "研报", "样本", "案例", "素材", "可挖", "信息密度", "材料",
            "详实", "丰富", "有得写", "值得拆", "可拆解", "故事性", "反共识", "反常识"]
# 差异化：模式里非显然、独特之处
DIM_DIFF = ["差异", "反常识", "独特", "壁垒", "模式", "打法", "少见", "稀缺", "护城河",
            "唯一", "领先", "卡位", "特色", "另类", "错位", "集成", "优势", "亮点",
            "黏性", "飞轮", "重资产", "轻资产", "非显然", "反直觉", "意想不到", "巧"]
# 可复制：国内创业者能学什么（点名可比公司/赛道）
DIM_COPY = ["可复制", "借鉴", "国内", "平移", "落地", "对标", "赛道", "复用", "学",
            "移植", "参考", "模仿", "可学", "可搬", "国内团队", "国内创业者", "对表",
            "本地化", "微创新", "启示", "思路", "打法可学", "方法", "国内可", "参照"]

# ---- 模板套话签名（命中即毙） ----
BANNED = ["复制需结合本地资源", "国内宜学其思路而非形态", "轻模式易复制，国内创业者可直接借鉴落地",
          "切入行业媒体赛道", "信号偏弱、信息量一般", "信号偏弱,信息量一般",
          "整体信号偏弱", "是一家致力于", "致力于为老年人", "专注于为老年",
          "切入XX赛道", "切入xx赛道", "可作为选题储备", "归档备用",
          "但信号偏弱，暂", "暂无近期大事件，但",
          "信息量评分", "维度评分", "评分约", "可写「", "深度案例", "对标样本",
          "对比报道", "只吃细分不吃全", "物业与人力双高", "数据侧错位",
          "照搬难", "暂列观察", "翻译腔",
          "要防政策与医保规则变动吃掉利润", "研究价值", "异类样本", "可参照的异类样本",
          "按本土合规重新设计", "横向比", "机构打法", "放到国内银发版图",
          "放到国内养老版图", "放到国内康复版图", "放到国内保险版图", "放到国内社交版图",
          "放到国内医疗版图", "放到国内食品版图", "放到国内旅游版图", "放到国内诊所版图",
          "放到国内药品版图", "放到国内健身版图", "放到国内文娱版图", "放到国内护理版图",
          "选题可写", "拆开看", "值得一写", "值得跟踪", "值得关注", "可成选题",
          "信号清晰", "信号偏弱", "信号尚可", "信号与信息量都足", "信号与信息都强",
          "信号与信息都足", "信号与信息均足", "信号、信息量都足", "信号强。", "信号足"]

# ---- 模板套话正则签名（结构级命中即毙） ----
BANNED_RE = [
    r"要防政策与医保规则变动吃掉利润",
    r"研究价值\d+(\.\d+)?分可作参考",
    r"放到国内.+版图.+异类样本",
    r"放到国内.+版图.+值得",
    r"成立\d{4}年至今、.+可挖年报",
    r"按本土合规重新设计",
    r"机构打法可学", r"机构打法思路", r"机构打法可参考",
    r"国内若抄其机构打法", r"国内想学其机构打法",
    r"信号偏中等、缺时间锚", r"信号尚可。在成熟市场",
    r"轻资产打法快速试错", r"轻模式易起量、易复制",
    r"累计融资约\$",
    r"成立\d{4}年至今、从招股与新闻",
    r"要防政策与医保",
    r"选题可写[「\"]", r"可写[「\"]",
]

# ---- 技术黑话 / 废话 ----
JARGON = ["血脑屏障", "CNS", "并购补管线", "MODEL递送", "CDD自治", "按人头付费绑定医保结余",
          "风险调整", "价值医疗", "VBC", "PBM", "HMO", "DRG", "DIP",
          "DTP", "B2B2C", "SaaS化", "五级医疗", "双向转诊"]
FILLER = ["赋能", "一站式", "全生命周期", "组合拳", "底层逻辑", "抓手", "闭环生态", "链路"]

# ---- 绝对化论断 ----
ABSOLUTE = ["国内缺乏", "市场空白", "国内尚无", "完全空白", "国内没有", "尚无竞品",
            "一片空白", "国内仍是空白", "国内基本空白", "国内仍属空白", "国内尚属空白",
            "国内空白", "还是空白", "仍属空白", "独家垄断", "没有对手", "无竞品",
            "尚属空白", "尚是空白", "国内独家", "国内唯一做"]

OPENERS_BAD = ("是一家", "致力于", "专注于", "作为一家", "作为国内")

# 阶段/状态词：若出现在 recommend 且与企业 stage 一致，视为重复状态信息
STATUS_WORDS = ["上市", "IPO", "被收购", "并购", "退市", "摘牌", "已私有化", "分拆上市"]


def content_len(s):
    return len(re.sub(r"\s", "", s or ""))


def lcs_len(a, b):
    """最长公共子串长度（中文逐字）。"""
    if not a or not b:
        return 0
    a, b = re.sub(r"\s", "", a), re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0
    if n * m > 4_000_000:
        a, b = a[:2000], b[:2000]
        n, m = len(a), len(b)
    dp = [0] * (m + 1)
    best = 0
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
                if dp[j] > best:
                    best = dp[j]
            else:
                dp[j] = 0
            prev = tmp
    return best


def _fourgrams(text):
    t = re.sub(r"\s", "", text or "")
    if len(t) < 4:
        return set()
    return set(t[i:i + 4] for i in range(len(t) - 3))


def _number_tokens(text):
    """抽取文本中的连续数字串（>=2位），用于检测融资额复述。"""
    return set(re.findall(r"\d{2,}", text or ""))


def _field_texts(e):
    """提取与 recommend 可能冗余的字段：description / highlights / 融资展示 / 阶段。
    注：比对素材用 description（前端实际展示的介绍字段）。desc_cn 为历史遗留字段，
    内容可能过期，不再作为比对素材。"""
    pairs = []
    dc = e.get("description") or ""
    if dc:
        pairs.append(("description", dc))
    hl = e.get("highlights") or []
    if isinstance(hl, list):
        for i, h in enumerate(hl):
            if isinstance(h, str) and h.strip():
                pairs.append((f"highlights[{i}]", h))
    fl = e.get("funding_latest") or {}
    if isinstance(fl, dict):
        fd = fl.get("display") or ""
        if fd:
            pairs.append(("funding_latest", fd))
    ft = e.get("funding_total") or {}
    if isinstance(ft, dict):
        ftd = ft.get("display") or ""
        if ftd:
            pairs.append(("funding_total", ftd))
    stage = e.get("stage") or ""
    if stage:
        pairs.append(("stage", stage))
    return pairs


def validate(e, others=None, skip=None):
    """
    返回 issues 列表（空=通过）。
    e 须含 recommend 及上下文(name/name_cn/tag_*/description/serial/stage/funding_*)。
    others: 其他企业的 recommend 字符串列表（用于 R10 跨企业去重）。
    """
    skip = set(skip or [])
    issues = []
    r = e.get("recommend")
    if not isinstance(r, str):
        issues.append("R1:recommend必须为单字符串(非dict)")
        return issues
    cl = content_len(r)
    txt = r

    # ── R2 字数（软绑） ──
    if "R2" not in skip:
        if cl < 50:
            issues.append(f"R2:字数过短({cl}<50)")
        if cl > 240:
            issues.append(f"R2:字数过长({cl}>240)")

    # ── R3 模板套话 ──
    if "R3" not in skip:
        for b in BANNED:
            if b in txt:
                issues.append("R3:模板套话[" + b + "]")
        for pat in BANNED_RE:
            if re.search(pat, txt):
                issues.append("R3:模板套话正则[" + pat + "]")

    # ── R5 三维覆盖（编辑视角；不要求"信号"，因融资/收购已在列表字段） ──
    if "R5" not in skip:
        miss = []
        if not any(k in txt for k in DIM_INFO):
            miss.append("信息量")
        if not any(k in txt for k in DIM_DIFF):
            miss.append("差异化")
        if not any(k in txt for k in DIM_COPY):
            miss.append("可复制")
        if miss:
            issues.append("R5:缺维度-" + ",".join(miss))

    # ── R-name 禁企业名 ──
    if "R-name" not in skip:
        nm = e.get("name") or ""
        nmc = e.get("name_cn") or ""
        if nm and nm in txt:
            issues.append("R-name:重复企业名(列表已有，勿写)")
        if nmc and nmc in txt:
            issues.append("R-name:重复企业中文名(列表已有，勿写)")

    # ══════════════════════════════════════════════
    # ★ R-redundancy 禁重复列表已有字段 ═════════════
    # ══════════════════════════════════════════════
    if "R-redundancy" not in skip:
        fpairs = _field_texts(e)
        # (a) 融资数字复述：recommend 含 funding 字段里的数字串
        fund_nums = set()
        for fname, ftext in fpairs:
            if fname.startswith("funding"):
                fund_nums |= _number_tokens(ftext)
        rec_nums = _number_tokens(txt)
        hit_nums = fund_nums & rec_nums
        if hit_nums:
            issues.append("R-redundancy:复述融资数字" + "/".join(sorted(hit_nums)[:3]) +
                          "(列表投融资字段已有，勿重复)")
        # (b) 阶段/状态词复述
        stage = e.get("stage") or ""
        for sw in STATUS_WORDS:
            if sw in stage and sw in txt:
                issues.append(f"R-redundancy:复述阶段状态[{sw}](卡片阶段字段已有)")
                break
        # (c) 近逐字抄 description / highlights（4-gram 重合度）
        rec_grams = _fourgrams(txt)
        for fname, ftext in fpairs:
            if fname.startswith("funding") or fname == "stage":
                continue
            fgrams = _fourgrams(ftext)
            if not rec_grams or not fgrams:
                continue
            union = rec_grams | fgrams
            jac = len(rec_grams & fgrams) / len(union)
            if jac > 0.65:
                issues.append(f"R-redundancy:与{fname}近逐字重复(重合{jac:.0%})，换编辑视角写")

    # ── R-integrity 内部一致性 ──
    if "R-integrity" not in skip and cl >= 50:
        _DOMAIN_WORDS = ["殡葬", "康复", "养老", "保险", "陪伴", "机器人", "食品", "辅具",
                         "护理", "地产", "医疗", "诊所", "健身", "社交", "旅游", "教育",
                         "理财", "服装", "营养", "药品", "器械", "家居", "出行", "传媒", "数据"]
        half = cl // 2
        first_dom = [w for w in _DOMAIN_WORDS if w in txt[:half]]
        second_dom = [w for w in _DOMAIN_WORDS if w in txt[half:]]
        if first_dom and second_dom and not (set(first_dom) & set(second_dom)):
            issues.append(
                f"R-integrity:前后半段讲不同赛道(前{first_dom}→后{second_dom})，疑似拼接错误"
            )

    # ── R-noabs / R-jargon ──
    if "R-noabs" not in skip:
        for a in ABSOLUTE:
            if a in txt:
                issues.append("R-noabs:绝对化国内论断[" + a + "]改'国内竞品较少/已有类似'")
    if "R-jargon" not in skip:
        for j in JARGON:
            if j in txt:
                issues.append("R-jargon:技术黑话[" + j + "]需大白话或加短解释")
        for f in FILLER:
            if f in txt:
                issues.append("R-filler:废话[" + f + "]")

    # ── R10 跨企业去重 ──
    if others:
        for o in others:
            if o and o != txt and lcs_len(txt, o) >= 15 and content_len(txt) > 0:
                sa, sb = set(re.sub(r"\s", "", txt)), set(re.sub(r"\s", "", o))
                if sa and sb and len(sa & sb) / len(sa | sb) > 0.5:
                    issues.append("R10:跨企业雷同(重合>0.5)")
                break

    return issues


def _ctx_from_db(serial):
    if not os.path.exists(DB):
        return {}
    d = json.load(open(DB, encoding="utf-8"))
    for e in d:
        if str(e.get("serial", "")).lstrip("#") == str(serial).lstrip("#"):
            return e
    return {}


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: check_single.py <draft_#XXXX.json> | --batch <src.json>")
        sys.exit(1)
    if args[0] == "--batch":
        recs = json.load(open(args[1], encoding="utf-8"))
        others = [r.get("recommend", "") for r in recs if isinstance(r.get("recommend"), str)]
        fails = {}
        for r in recs:
            iss = validate(r, others)
            if iss:
                fails[r.get("serial")] = iss
        print(f"校验 {len(recs)} 家 | 通过 {len(recs)-len(fails)} | 未过 {len(fails)}")
        for s, iss in fails.items():
            print(f"  {s}: {iss}")
        sys.exit(0)
    fp = args[0]
    dr = json.load(open(fp, encoding="utf-8"))
    ctx = _ctx_from_db(dr.get("serial", ""))
    tmp = dict(ctx)
    for k in ("recommend", "description", "desc_cn", "highlights", "stage", "funding_latest", "funding_total"):
        if k in dr and dr[k] is not None:
            tmp[k] = dr[k]
    iss = validate(tmp)
    print("PASS" if not iss else "FAIL:" + str(iss))


if __name__ == "__main__":
    main()
