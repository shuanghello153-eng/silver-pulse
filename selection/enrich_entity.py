# -*- coding: utf-8 -*-
"""
selection/enrich_entity.py — 企业实体名回填（零成本，纯脚本）。

在采集/评分管道中补一步：用企业库(all_enterprises.json)的「名称/中文名」
去匹配每条资讯的 标题+摘要(+正文)，命中则填 entity_name。

要点（见任务要求）：
  - 大小写不敏感（英文企业名统一小写比较）；
  - 中文按子串精确匹配（企业库名多为专名，误命中低）；
  - 排除信源同名误命中：命中名 == 该条 source 名则跳过
    （如 AgeClub 既是信源也是企业库条目，不可把整页 AgeClub 稿的
     主体都标成 AgeClub）；
  - 长度门槛：中文≥2字、英文≥3字符，避免极短串误命中；
  - 多命中取最长（最具体）的名称；
  - 匹配不到就留空，绝不瞎填。

不改动任何评分维度权重/命名（属禁区）。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORED_PATH = os.path.join(BASE_DIR, "data", "scored_latest.json")
ENT_PATH = os.path.join(BASE_DIR, "data", "enterprise", "all_enterprises.json")

# 绝不作为实体的泛词（即便企业库里有同名也忽略；保险起见，当前企业库无此类）。
# 任务要求的「美国/英国/融资/养老」等泛词本就不在企业名里，不会误命中；
# 这里保留扩展位，便于将来企业库混入通用词时仍安全。
_NOISE_NAMES = set()

# --------------------------------------------------------------------------- #
# 兜底规则（企业库未命中时使用）。
# 设计原则：高精确率优先，宁可留空也不要瞎填（避免污染聚类主规则）。
#   1) 中文：标题/摘要中带明确企业后缀（公司/集团/科技/医疗/养老…）的专名；
#      或出现「X融资 / X收购 / X推出」事件结构时，取其主语专名。
#   2) 英文：首字母大写的机构专名短语紧邻融资/收购/发布等事件动词。
# 命中后均经停用词守护过滤（不把「该公司 / 民政部 / 广东」等当企业名）。
# --------------------------------------------------------------------------- #
# 中文明确企业后缀（命中即视为企业名候选）
_CN_CORP_SUFFIX = re.compile(
    r"([一-龥]{2,8}(?:公司|集团|科技|技术|医疗|健康|养老|生物|制药|控股|股份|"
    r"实验室|研究院|医院|银行|保险|基金|企业|网络|数据|智能))"
)
# 中文「主语 + 事件动词」结构（融资/收购/上市/推出/发布…）
_CN_EVENT = re.compile(
    r"([一-龥]{2,10}?)\s*(?:完成|宣布|获得|拟|计划|成功|正式)?\s*(?:了)?"
    r"(?:融资|收购|并购|被收购|上市|IPO|推出|发布|上线|发布)"
)
# 英文「专名 + 事件动词」结构
_EN_EVENT = re.compile(
    r"([A-Z][A-Za-z0-9&.'\-]+(?:\s+[A-Z][A-Za-z0-9&.'\-]+){0,4})\s+"
    r"(?:raises|raised|acquires|acquired|launches|launched|unveils|unveiled|"
    r"announces|announced|completes|completed|closes|closed|ipo|goes\s+public|"
    r"partners|releases|released|debuts|introduces|introduced|names|hires|"
    r"appoints|appointed|increases|rolls?\s+out)\b",
    re.I,
)
# 兜底命中前的停用前缀 / 泛称，命中则丢弃（避免「这家公司 / 该公司 / 民政部」误填）
_CN_STOP_PREFIX = (
    "这家", "该", "那个", "本", "各", "某", "一些", "部分", "一家", "多家",
    "我国", "我省", "我市", "全国", "各地", "城乡", "近日", "目前", "随着",
    "通过", "针对", "关于", "对于", "广东", "北京", "上海", "香港", "中国",
    "美国", "民政", "新浪", "银龄", "观点", "潮新闻", "新京报", "大河",
    "广州市", "广州", "工行", "央行", "银保", "监管", "政府", "部门",
)
_EN_STOP = (
    "The", "This", "That", "New", "Home", "In", "On", "A", "An", "Its",
    "Their", "Our", "Report", "Study", "Survey", "State", "Federal",
)


def _cn_clean(s):
    s = s.strip().strip("「」“”\"'（）()：:，,。. ").strip()
    if len(s) < 2:
        return ""
    if s.startswith(_CN_STOP_PREFIX):
        return ""
    # 不含典型事件/政策泛词
    if any(w in s for w in ("指引", "改革", "网络建设", "服务网络", "管理办法",
                            "通知", "条例", "规划", "报告", "洞察", "简报")):
        return ""
    return s


def _en_clean(s):
    s = s.strip().strip("「」“”\"'（）()：:，,。. ").strip()
    if len(s) < 3:
        return ""
    if s in _EN_STOP or s.split()[0] in _EN_STOP:
        return ""
    return s


def match_entity_fallback(blob):
    """企业库未命中时的兜底抽取。返回企业名或 ''。"""
    if not blob:
        return ""
    # 中文：优先明确企业后缀
    for m in _CN_CORP_SUFFIX.finditer(blob):
        cand = _cn_clean(m.group(1))
        if cand:
            return cand
    # 中文：事件主语结构
    m = _CN_EVENT.search(blob)
    if m:
        cand = _cn_clean(m.group(1))
        if cand:
            return cand
    # 英文：专名 + 事件动词
    m = _EN_EVENT.search(blob)
    if m:
        cand = _en_clean(m.group(1))
        if cand:
            return cand
    return ""


def _norm(s):
    return (s or "").strip().lower()


def build_entity_index(enterprises):
    """返回可匹配列表 [(display_name, lower_form), ...]。"""
    idx = []
    seen = set()
    for e in enterprises:
        disp = e.get("name_cn") or e.get("name") or ""
        forms = set()
        for k in ("name", "name_cn"):
            v = _norm(e.get(k))
            if v:
                forms.add(v)
        for fm in forms:
            if fm in _NOISE_NAMES:
                continue
            # 长度门槛：中文2字起、英文3字符起，避免极短误命中
            if len(fm) < 2:
                continue
            if fm.isascii() and len(fm) < 3:
                continue
            if fm in seen:
                continue
            seen.add(fm)
            idx.append((disp, fm))
    return idx


def match_entity(blob, source_name, index):
    """在 blob 中找企业名。优先企业库精确匹配，未命中走兜底规则。"""
    if not blob:
        return ""
    low = blob.lower()
    src = _norm(source_name)
    best = None
    for disp, fm in index:
        if fm == src:
            # 信源同名误命中（如 AgeClub 既是信源也是企业库条目）
            continue
        if fm in low:
            if best is None or len(fm) > len(best[1]):
                best = (disp, fm)
    if best:
        return best[0]
    # 企业库未命中 -> 兜底规则（高精确率优先，宁可留空）
    fb = match_entity_fallback(blob)
    if fb and _norm(fb) != src:
        return fb
    return ""


def run_daily_step():
    """回填 scored_latest.json 的 entity_name 字段。"""
    if not os.path.exists(SCORED_PATH):
        print("[enrich_entity] scored_latest.json 不存在，跳过")
        return
    if not os.path.exists(ENT_PATH):
        print("[enrich_entity] 企业库不存在，跳过")
        return
    enterprises = json.load(open(ENT_PATH, encoding="utf-8"))
    index = build_entity_index(enterprises)
    arts = json.load(open(SCORED_PATH, encoding="utf-8"))
    total = len(arts)
    hit = 0
    for art in arts:
        if art.get("entity_name"):
            hit += 1
            continue
        title = (art.get("title_cn") or art.get("title") or "")
        summary = (art.get("summary_cn") or art.get("summary")
                   or art.get("raw_content") or "")
        blob = title + " " + summary
        ent = match_entity(blob, art.get("source"), index)
        if ent:
            art["entity_name"] = ent
            hit += 1
    json.dump(arts, open(SCORED_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[enrich_entity] 企业实体名回填完成：命中 %d / %d 条" % (hit, total))


if __name__ == "__main__":
    run_daily_step()
