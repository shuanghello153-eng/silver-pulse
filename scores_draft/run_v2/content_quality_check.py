# -*- coding: utf-8 -*-
"""
内容质量检测器（L9/L10 · 非格式校验）
检测推荐理由的模板化程度、重复率、信息密度。
用法：python content_quality_check.py            # 全量
      python content_quality_check.py sample 20   # 随机抽20家看详情
"""
import json, os, sys, re, random, collections, math

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")

db = json.load(open(DB_PATH, encoding="utf-8"))
n = len(db)

# === L9: 模板套话检测 ===
TEMPLATE_PATTERNS = {
    "切入X赛道": re.compile(r"切入.{2,10}(赛道|市场|领域|行业)"),
    "结合本地资源": re.compile(r"结合(本地|国内|本土|当地)资源"),
    "部分环节可借鉴": re.compile(r"部分环节可(借鉴|参考|复制|学习)"),
    "有一定差异点": re.compile(r"有(一定|较)?(差异|亮点|特色)(点)?"),
    "复制需结合本地": re.compile(r"复制需?结合.*资源"),
    "值得关注": re.compile(r"(值得)?(关注|研究)[，。]?$"),
    "有一定前景": re.compile(r"有(一)?定?(前景|潜力)(？)?$"),
    "模式较常规": re.compile(r"模式(较|挺)?(常规|普通|一般)"),
    "信息量一般": re.compile(r"信息(量|披露)?(一般|偏少|较弱)(？|[，。])"),
    "信号偏弱/中等": re.compile(r"信号(偏弱|中等|较强?)(？|[，。;；])"),
}

# === L10: 重复率检测（精确+模糊）===
def normalize_rec(rec):
    """标准化recommend用于模糊去重：去掉具体企业名/标签，保留句式骨架"""
    s = rec.strip()
    # 去掉引号内的具体内容
    s = re.sub(r'[「」【】\[\]]', '', s)
    return s

# === 运行 ===
mode = sys.argv[1] if len(sys.argv) > 1 else "full"

print("=" * 70)
print(f"内容质量检测 | 企业总数 {n} 家")
print("=" * 70)

# --- L9 模板套话统计 ---
print("\n[L9] 🚫 模板套话检测")
template_hits = collections.Counter()   # pattern -> count
violations_9 = []                       # (serial, name, pattern, snippet)

for e in db:
    rec = e.get("recommend", "")
    if not isinstance(rec, str): continue
    for pname, pat in TEMPLATE_PATTERNS.items():
        m = pat.search(rec)
        if m:
            template_hits[pname] += 1
            violations_9.append((e["serial"], e.get("name", ""), pname, rec[max(0,m.start()-15):m.end()+20]))

total_template_violations = sum(template_hits.values())
print(f"  模板套话命中总数: {total_template_violations} 条 (一家可能命中多条)")
print(f"  涉及企业数: {len(set(v[0] for v in violations_9))} / {n}")
print("  各模板频次:")
for pname, cnt in template_hits.most_common():
    pct = round(cnt / n * 100, 1)
    bar = "█" * min(int(pct) // 2, 50)
    status = "🔴 严重" if pct > 30 else ("🟡 注意" if pct > 10 else "🟢 可接受")
    print(f"    {pname}: {cnt} ({pct}%) {bar} {status}")

# --- L10 重复率 ---
print("\n[L10] 🔁 推荐理由重复率检测")
rec_list = [(e["serial"], e.get("name", ""), e.get("recommend", "")) for e in db]
exact_dups = collections.Counter(r[2] for r in rec_list if isinstance(r[2], str))
dup_count = sum(c for c in exact_dups.values() if c > 1)
dup_enterprises = sum(c for c in exact_dups.values() if c > 1)  # total entries that are dups
unique_rate = len(exact_dups) / n * 100 if n > 0 else 0
print(f"  完全相同的recommend: {dup_count} 条 (涉及 {sum(1 for c in exact_dups.values() if c > 1)} 组)")
print(f"  唯一率: {round(unique_rate, 1)}%")

# 结尾短语重复（最常见的问题）
ending_phrases = []
for _, _, rec in rec_list:
    if isinstance(rec, str) and len(rec) > 10:
        # 取最后25字作为结尾
        tail = rec[-25:]
        ending_phrases.append(tail)
ending_counter = collections.Counter(ending_phrases)
top_endings = ending_counter.most_common(10)
print("  最常见的结尾句式(TOP10):")
for phrase, cnt in top_endings:
    pct = round(cnt / n * 100, 1)
    print(f'    [{cnt}次({pct}%)] "{phrase}"')

# --- desc_cn 质量统计 ---
print("\n[L11] 📝 desc_cn 描述质量")
desc_lengths = []
short_desc = []  # <40字
for e in db:
    dc = e.get("desc_cn", "")
    if isinstance(dc, str):
        desc_lengths.append(len(dc))
        if len(dc) < 40:
            short_desc.append((e["serial"], e.get("name", ""), dc))

if desc_lengths:
    import statistics
    avg_l = round(statistics.mean(desc_lengths), 1)
    med_l = round(statistics.median(desc_lengths), 1)
    short_pct = len(short_desc) / n * 100
    print(f"  平均长度: {avg_l} 字 | 中位数: {med_l} 字 | 最短: {min(desc_lengths)} | 最长: {max(desc_lengths)}")
    print(f"  <40字(太短): {len(short_desc)} 家 ({round(short_pct, 1)}%) [标准: 50-150字]")
    if len(short_desc) <= 10:
        for s, nm, dc in short_desc[:5]:
            print(f'    [{s}] {nm}: "{dc}"')
    else:
        print(f"    (前5样例)")
        for s, nm, dc in short_desc[:5]:
            print(f'    [{s}] {nm}: "{dc}"')

# --- 信息熵评分 ---
print("\n[L12] 📊 推荐理由信息多样性评分")
all_recs = [e.get("recommend", "") for e in db if isinstance(e.get("recommend"), str)]
if all_recs:
    # 字符级熵
    all_text = "".join(all_recs)
    char_freq = collections.Counter(all_text)
    total_chars = len(all_text)
    entropy = -sum((c / total_chars) * math.log2(c / total_chars) for c in char_freq.values())
    max_entropy = math.log2(len(char_freq)) if char_freq else 1
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 0
    print(f"  字符级归一化熵: {round(norm_entropy, 3)} (1.0=最大随机性, 0=全部相同)")
    
    # 词级唯一度（用2-gram）
    bigrams = []
    for r in all_recs:
        words = r.replace("，", " ").replace("。", " ").replace("、", " ").split()
        bigrams.extend(zip(words, words[1:]))
    unique_bigrams = len(set(bigrams)) if bigrams else 0
    total_bigrams = len(bigrams)
    print(f"  2-gram唯一率: {round(unique_bigrams/max(total_bigrams,1)*100, 1)}% ({unique_bigrams}/{total_bigrams})")

# --- 综合评分 ---
print("\n" + "=" * 70)
print("综合质量评级:")
scores = {}
# L9: template score (lower is better)
s9 = max(0, 100 - total_template_violations / n * 100 * 3)  # each 1% of templates = -3 points
scores["模板套话"] = round(s9, 1)
# L10: uniqueness
s10 = unique_rate
scores["唯一率"] = round(s10, 1)
# L11: desc length
s11 = 100 - abs(avg_l - 100) / 100 * 50 if desc_lengths else 50  # target 100 chars
s11 = max(0, min(100, s11))
scores["描述长度"] = round(s11, 1)
overall = (s9 + s10 + s11) / 3
scores["综合"] = round(overall, 1)

for k, v in scores.items():
    bar_val = int(v / 5)
    bar = "█" * bar_val + "░" * (20 - bar_val)
    label = "✅" if v >= 70 else ("⚠️" if v >= 40 else "❌")
    print(f"  {label} {k}: {v}/100 {bar}")

print("=" * 70)
if mode == "sample":
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print(f"\n随机抽样 {k} 家详细查看:")
    sample = random.sample(db, min(k, n))
    for e in sample:
        rec = e.get("recommend", "") or ""
        dc = e.get("desc_cn", "") or ""
        print(f"\n  [{e['serial']}] {e.get('name','')}")
        print(f"    recommend({len(rec)}字): {rec}")
        print(f"    desc_cn({len(dc)}字): {dc}")
        # check which templates hit
        hits = []
        for pname, pat in TEMPLATE_PATTERNS.items():
            if pat.search(rec):
                hits.append(pname)
        if hits:
            print(f"    ⚠️ 模板套话: {hits}")
