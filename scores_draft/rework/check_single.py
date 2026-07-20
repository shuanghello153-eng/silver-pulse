# -*- coding: utf-8 -*-
"""
单条推荐理由硬门禁（V4 · 全面跨字段去重版）
本文件是「不可绕过的真相源」：工人必须逐家跑它到 PASS 才许交付；主智能体合并时再独立跑一遍。

V3 → V4 变更记录（2026-07-18 小爽反馈后紧急升级）：
  根因：200家返工中 143家(72%)存在跨字段雷同或内部矛盾，旧门禁形同虚设。
  变更：
  - R-dedup(旧) → R-field-dedup(新)：从只查desc_cn+阈值20 → 查6组字段+阈值收紧到10/8字
  - 新增 R-integrity：推荐理由前后半段不能讲完全不同赛道（防拼接串内容）
  - 新增 R-novelty：推荐理由必须有增量信息（不能全抄卡片其他字段）
  - R10 跨企业阈值从20降到15

用法：
  python check_single.py draft_#XXXX.json            # 单文件（工人自校）
  python check_single.py --batch batch_src.json       # 对一组源/草稿批量校验
  (被 rework_merge.py import：from check_single import validate)

【门禁规则完整清单】
  R1     recommend 必须是单字符串（不是 dict）
  R2     字数 70~220（去掉空白）
  R3     禁模板套话签名句
  R4     必须落到本企业具体事实（数字 或 tag 词）
  R5     单条须覆盖四维度（信号/信息量/差异化/可复制）
  R-name 禁重复企业名
  ★R-field-dedup  禁与卡片内任何字段大段雷同（desc/silver/highlights/funding等）
  ★R-integrity    内部一致性（前后半段不能讲不同赛道）
  ★R-novelty      必须有增量信息（不能全抄已有字段）
  R-jargon        禁技术黑话/废话
  R-noabs         禁绝对化「国内空白」论断
  R6     desc_cn >= 80 字且不以禁忌词开头
  R7     silver_reason >= 30 字
  R8     payor_model 必须在规范词表
  R10    跨企业雷同（重合>0.5，阈值从0.6收紧）
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")

# ---- 四维度关键词 ----
DIM_SIG = ["信号", "热点", "融资", "收购", "IPO", "上市", "事件", "近期", "大额",
           "政策", "新规", "获批", "过审", "风口", "扩张", "合作", "启动", "上线", "发布",
           "新获", "获投", "中标", "申报", "刚获", "落地", "推", "当下", "当前", "刚",
           "减持", "回购", "退市", "摘牌", "违约", "破产", "关停", "转型", "收缩", "亏损"]
DIM_INFO = ["信息", "资料", "透明", "公开", "年报", "招股", "报道", "深度", "数据", "数据量",
            "披露", "财报", "营收", "净利", "复购", "中标", "用户", "月活", "临床", "专利",
            "招股书", "公告", "研报", "样本", "规模", "交易额", "装机", "病例", "金额", "亿元",
            "估值", "量化", "指标", "明细", "覆盖", "触达", "融资额", "获投", "领投", "服务量",
            "门店", "网点", "床位", "会员", "客户", "付费", "续费", "网点数"]
DIM_DIFF = ["差异", "反常识", "独特", "壁垒", "模式", "打法", "少见", "起落", "颠覆",
            "首创", "独家", "定位", "稀缺", "护城河", "唯一", "领先", "第一", "卡位",
            "特色", "另类", "不一样", "不同", "重资产", "轻资产", "错位", "集成", "优势", "亮点",
            "黏性", "飞轮", "网络效应", "低频", "高频"]
DIM_COPY = ["可复制", "借鉴", "国内", "平移", "照搬", "落地", "红海", "对标", "赛道",
            "复用", "学", "移植", "参考", "模仿", "可学", "可搬", "国内团队", "国内创业者",
            "对表", "本地化", "微创新", "启示", "思路", "打法可学", "方法"]

# ---- 模板套话签名（命中即毙） ----
BANNED = ["复制需结合本地资源", "国内宜学其思路而非形态", "轻模式易复制，国内创业者可直接借鉴落地",
          "切入行业媒体赛道", "信号偏弱、信息量一般", "信号偏弱,信息量一般",
          "整体信号偏弱", "是一家致力于", "致力于为老年人", "专注于为老年",
          "切入XX赛道", "切入xx赛道", "可作为选题储备", "归档备用",
          "但信号偏弱，暂", "暂无近期大事件，但",
          # 2026-07-19 增补：V4 旧草稿套话模板签名（"信息量评分约X.0"体），命中即毙
          "信息量评分", "维度评分", "评分约", "可写「", "深度案例", "对标样本",
          "对比报道", "只吃细分不吃全", "物业与人力双高", "数据侧错位",
          "照搬难", "暂列观察", "翻译腔",
          # 2026-07-19 晚 增补：第二批模板签名（"放到国内X版图…异类样本"体），命中即毙
          "要防政策与医保规则变动吃掉利润", "研究价值", "异类样本", "可参照的异类样本",
          "按本土合规重新设计", "横向比", "机构打法", "放到国内银发版图",
          "放到国内养老版图", "放到国内康复版图", "放到国内保险版图", "放到国内社交版图",
          "放到国内医疗版图", "放到国内食品版图", "放到国内旅游版图", "放到国内诊所版图",
          "放到国内药品版图", "放到国内健身版图", "放到国内文娱版图", "放到国内护理版图"]

# ---- 模板套话正则签名（结构级命中即毙，专防"换变量填空"型模板） ----
BANNED_RE = [
    r"要防政策与医保规则变动吃掉利润",          # 第二批模板固定尾句
    r"研究价值\d+(\.\d+)?分可作参考",            # 固定伪评分残留
    r"放到国内.+版图.+异类样本",                 # "放到国内X版图，X算可参照的异类样本"
    r"放到国内.+版图.+值得",                     # 变体尾句
    r"成立\d{4}年至今、.+可挖年报",              # 固定背书句式
    r"按本土合规重新设计",                       # 固定套话
    r"机构打法可学", r"机构打法思路", r"机构打法可参考",
    r"国内若抄其机构打法", r"国内想学其机构打法",
    r"信号偏中等、缺时间锚", r"信号尚可。在成熟市场",
    r"轻资产打法快速试错", r"轻模式易起量、易复制",
    r"累计融资约\$",                             # 海外模板固定"累计融资约$X"填空
    r"成立\d{4}年至今、从招股与新闻",            # 固定拼图句式
    r"要防政策与医保",                           # 兜底
]

# ---- 技术黑话 ----
JARGON = ["血脑屏障", "CNS", "并购补管线", "MODEL递送", "CDD自治", "按人头付费绑定医保结余",
          "风险调整", "价值医疗", "VBC", "PBM", "HMO", "DRG", "DIP",
          "DTP", "B2B2C", "SaaS化", "五级医疗", "双向转诊"]
FILLER = ["赋能", "一站式", "全生命周期", "组合拳", "底层逻辑", "抓手", "闭环生态", "链路"]

# ---- 绝对化论断 ----
ABSOLUTE = ["国内缺乏", "市场空白", "国内尚无", "完全空白", "国内没有", "尚无竞品",
            "一片空白", "国内仍是空白", "国内基本空白", "国内仍属空白", "国内尚属空白",
            "国内空白", "还是空白", "仍属空白", "独家垄断", "没有对手", "无竞品",
            "尚属空白", "尚是空白", "国内独家", "国内唯一做"]

CANON = {"个人自费", "个人自费+政府补贴", "个人自费+长护险", "个人自费+医保",
         "B端机构采购", "B端机构采购+个人自费", "B端机构采购+政府付费", "B端机构采购+政府/商保支付",
         "政府医保/商保支付", "混合支付", "不适用（投资机构）", "未搜到"}

OPENERS_BAD = ("是一家", "致力于", "专注于", "作为一家", "作为国内")

# 赛道关键词（用于内部一致性检测）
_DOMAIN_WORDS = [
    "殡葬", "康复", "养老", "保险", "陪伴", "机器人", "食品", "辅具", "护理",
    "地产", "医疗", "诊所", "健身", "社交", "旅游", "教育", "理财", "服装",
    "营养", "药品", "器械", "家居", "出行", "传媒", "数据"
]

_dc = None


def _comp():
    global _dc
    if _dc is None:
        from _domestic_comp import DomesticComp
        _dc = DomesticComp()
    return _dc


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


def _field_texts(e):
    """提取需要做跨字段去重的所有字段文本列表。返回 [(字段名, 文本), ...]"""
    pairs = []
    dc = e.get("desc_cn") or ""
    if dc:
        pairs.append(("desc_cn", dc))
    sr = e.get("silver_reason") or ""
    if sr:
        pairs.append(("silver_reason", sr))
    hl = e.get("highlights") or []
    if isinstance(hl, list):
        for i, h in enumerate(hl):
            if isinstance(h, str) and h.strip():
                pairs.append((f"highlights[{i}]", h))
    fl = e.get("funding_latest") or {}
    if isinstance(fl, dict):
        fd = fl.get("display") or ""
        if fd:
            pairs.append(("funding_latest.display", fd))
    ft = e.get("funding_total") or {}
    if isinstance(ft, dict):
        ftd = ft.get("display") or ""
        if ftd:
            pairs.append(("funding_total.display", ftd))
    desc_en = e.get("description") or ""
    if desc_en:
        pairs.append(("description(英文)", desc_en))
    return pairs


def _domain_keywords(text):
    """从文本中提取命中的赛道关键词列表。"""
    return [w for w in _DOMAIN_WORDS if w in text]


def validate(e, others=None, skip=None):
    """
    返回 issues 列表（空=通过）。
    e 须含 recommend 及上下文(name/name_cn/tag_*/desc_cn/serial)。
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

    # ── R2 字数 ──
    if "R2" not in skip:
        if cl < 70:
            issues.append(f"R2:字数过短({cl}<70)")
        if cl > 220:
            issues.append(f"R2:字数过长({cl}>220，疑似啰嗦)")

    # ── R3 模板套话（含结构级正则）──
    if "R3" not in skip:
        for b in BANNED:
            if b in txt:
                issues.append("R3:模板套话[" + b + "]")
        for pat in BANNED_RE:
            if re.search(pat, txt):
                issues.append("R3:模板套话正则[" + pat + "]")

    # ── R5 四维覆盖 ──
    if "R5" not in skip:
        miss = []
        if not any(k in txt for k in DIM_SIG):
            miss.append("信号")
        if not any(k in txt for k in DIM_INFO):
            miss.append("信息量")
        if not any(k in txt for k in DIM_DIFF):
            miss.append("差异化")
        if not any(k in txt for k in DIM_COPY):
            miss.append("可复制")
        if miss:
            issues.append("R5:缺维度-" + ",".join(miss))

    # ── R4 落到本企业事实 ──
    if "R4" not in skip:
        has_digit = bool(re.search(r"\d", txt))
        tags = (e.get("tag_l1") or []) + (e.get("tag_l2") or [])
        has_tag = any(t and t in txt for t in tags)
        if not (has_digit or has_tag):
            issues.append("R4:未落到本企业具体事实(无数字/无tag锚点)")

    # ── R-name 禁企业名 ──
    if "R-name" not in skip:
        nm = e.get("name") or ""
        nmc = e.get("name_cn") or ""
        if nm and nm in txt:
            issues.append("R-name:重复企业名(列表已有，勿写)")
        if nmc and nmc in txt:
            issues.append("R-name:重复企业中文名(列表已有，勿写)")

    # ══════════════════════════════════════
    # ★ V4 新增：R-field-dedup 全字段去重 ════
    # ══════════════════════════════════════
    if "R-field-dedup" not in skip:
        field_pairs = _field_texts(e)
        # 阈值配置：(字段类型, 最大允许LCS长度)
        thresholds = {
            "desc_cn": 10,
            "silver_reason": 10,
            "description": 10,
            "highlights": 8,
            "funding_latest": 8,
            "funding_total": 8,
        }
        for fname, ftext in field_pairs:
            # 确定该用哪个阈值
            thr = 8  # default
            for prefix, t in thresholds.items():
                if fname.startswith(prefix):
                    thr = t
                    break
            overlap = lcs_len(txt, ftext)
            if overlap >= thr:
                issues.append(f"R-field-dedup:与{fname}雷同({overlap}字≥{thr}阈值)")

    # ══════════════════════════════════════
    # ★ V4 新增：R-integrity 内部一致性 ═════
    # ══════════════════════════════════════
    if "R-integrity" not in skip and cl >= 60:
        half = cl // 2
        first_txt = txt[:half] if len(txt) > half else txt
        second_txt = txt[half:] if len(txt) > half else ""
        first_dom = _domain_keywords(first_txt)
        second_dom = _domain_keywords(second_txt)
        if first_dom and second_dom:
            overlap = set(first_dom) & set(second_dom)
            if not overlap:
                issues.append(
                    f"R-integrity:前后半段讲不同赛道(前{first_dom}→后{second_dom})，疑似拼接错误"
                )

    # ══════════════════════════════════════
    # ★ V4 新增：R-novelty 增量信息 ═══════
    # ══════════════════════════════════════
    if "R-novelty" not in skip:
        field_pairs = _field_texts(e)
        all_field_text = " ".join(ft for _, ft in field_pairs)
        if all_field_text and content_len(all_field_text) > 20:
            # 推荐理由中必须有至少12个字不在所有字段文本的并集中出现
            # 用集合差集检测：recommend的字符集合 vs 所有字段字符集合
            rec_chars = set(re.sub(r"\s", "", txt))
            field_chars = set(re.sub(r"\s", "", all_field_text))
            novel_chars = rec_chars - field_chars
            # 更严格：LCS检测 — recommend与任一字段的最大LCS不能超过recommend长度的70%
            max_overlap_ratio = 0
            for fname, ftext in field_pairs:
                ov = lcs_len(txt, ftext)
                ratio = ov / cl if cl > 0 else 0
                if ratio > max_overlap_ratio:
                    max_overlap_ratio = ratio
            if max_overlap_ratio > 0.70:
                worst_field = max(field_pairs, key=lambda p: lcs_len(txt, p[1]) / cl if cl > 0 else 0)
                issues.append(
                    f"R-novelty:超70%内容与{worst_field[0]}重叠(比例{max_overlap_ratio:.0%})，缺少独立分析"
                )

    # ── R-jargon / R-filler ──
    if "R-jargon" not in skip:
        for j in JARGON:
            if j in txt:
                issues.append("R-jargon:技术黑话[" + j + "]需大白话或加短解释")
        for f in FILLER:
            if f in txt:
                issues.append("R-filler:废话[" + f + "]")

    # ── R-noabs 绝对化 ──
    if "R-noabs" not in skip:
        for a in ABSOLUTE:
            if a in txt:
                issues.append("R-noabs:绝对化国内论断[" + a + "]改'国内竞品较少/已有类似'")

    # ── R6 desc ──
    if "R6" not in skip:
        dc = e.get("desc_cn", "")
        if not isinstance(dc, str) or content_len(dc) < 80:
            issues.append(f"R6:desc_cn<80({content_len(dc) if isinstance(dc,str) else 0})")
        elif dc.startswith(OPENERS_BAD):
            issues.append("R6:desc开头禁忌")

    # ── R7 silver ──
    if "R7" not in skip:
        sr = e.get("silver_reason", "")
        if not isinstance(sr, str) or content_len(sr) < 30:
            issues.append(f"R7:silver_reason<30({content_len(sr) if isinstance(sr,str) else 0})")

    # ── R8 payor ──
    if "R8" not in skip:
        pm = e.get("payor_model", "")
        if pm not in CANON:
            issues.append("R8:payor非规范[" + str(pm) + "]")

    # ── R10 跨企业去重（阈值从0.6收紧到0.5）──
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
    for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
        if k in dr and dr[k] is not None:
            tmp[k] = dr[k]
    iss = validate(tmp)
    print("PASS" if not iss else "FAIL:" + str(iss))


if __name__ == "__main__":
    main()
