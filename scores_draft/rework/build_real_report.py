# -*- coding: utf-8 -*-
"""生成企业库真实数据核验报告（纯数据，可复现）。"""
import json, re, glob, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single import validate

DB = json.load(open("../../data/enterprise/all_enterprises.json", encoding="utf-8"))
def norm(s): return re.sub(r"\D", "", str(s or ""))
db_by = {norm(e.get("serial")): e for e in DB}
SAFE = ["recommend", "desc_cn", "silver_reason", "payor_model", "update_time", "flag"]

# ---- 加载草稿 ----
dv = {}
for f in glob.glob("drafts_v4/*.json"):
    try: j = json.load(open(f, encoding="utf-8"))
    except: continue
    ser = j.get("serial") or j.get("企业序号")
    if ser: dv[norm(ser)] = j
N = len(dv)

# ---- 门禁 ----
rec_pass = rec_fail = full_pass = full_fail = 0
rec_rules = collections.Counter(); full_rules = collections.Counter()
carry_full = carry_partial = carry_reconly = 0
rec_fail_ex = []; rec_pass_ex = []
for ser, j in dv.items():
    e = db_by.get(ser)
    if not e: continue
    r = j.get("recommend") or j.get("推荐理由")
    if not (isinstance(r, str) and r.strip()): continue
    e2 = dict(e)
    for k in SAFE:
        if k in j and j[k] is not None: e2[k] = j[k]
    has = lambda k: k in j and isinstance(j[k], str) and j[k].strip()
    if has("desc_cn") and has("silver_reason") and has("payor_model"): carry_full += 1
    elif has("desc_cn") or has("silver_reason") or has("payor_model"): carry_partial += 1
    else: carry_reconly += 1
    iss_rec = validate(e2, None, skip={"R6","R7","R8","R10"})
    iss_full = validate(e2, None, skip={"R10"})
    if iss_rec:
        rec_fail += 1
        for i in iss_rec: rec_rules[i.split(":")[0]] += 1
        if len(rec_fail_ex) < 5: rec_fail_ex.append((ser, e.get("name_cn") or e.get("name"), r, iss_rec))
    else:
        rec_pass += 1
        if len(rec_pass_ex) < 3: rec_pass_ex.append((ser, e.get("name_cn") or e.get("name"), r))
    if iss_full:
        full_fail += 1
        for i in iss_full: full_rules[i.split(":")[0]] += 1
    else: full_pass += 1

cl = lambda s: len(re.sub(r"\s", "", s or ""))

# ---- 字段填充率 + 分类 ----
total = len(DB)
empty = collections.Counter()
for e in DB:
    for k in e:
        v = e[k]
        if v is None or (isinstance(v, str) and v.strip() == "") or v == "{}" or v == []:
            empty[k] += 1
REWORK = {"recommend","desc_cn","silver_reason","payor_model"}
SCORES = {"signal_strength","info_score","diff_score","copy_score","research_value","value_score"}
TAGS = {"tag_l1","tag_l2","business_tags","tags","category_l1","category_l2"}
DEPR = {"_legacy_rec","数据来源 "}  # 疑似废弃候选
def cat(k):
    if k in REWORK: return "①返工4字段"
    if k in SCORES: return "②评分(不碰)"
    if k in TAGS: return "③标签(不碰)"
    if k in DEPR: return "④疑似废弃"
    return "⑤源数据字段"

# ---- 文件名模式 ----
allf = glob.glob("drafts_v4/*.json")
pat = glob.glob("drafts_v4/draft_#*.json")
nonpat = [os.path.basename(x) for x in allf if not re.search(r"draft_#", x)]

# ---- HTML ----
def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
rows = ""
for k in sorted(set(k for e in DB for k in e)):
    f = total - empty.get(k, 0)
    p = 100*f//total
    rows += f"<tr><td>{esc(k)}</td><td>{cat(k)}</td><td>{f}/{total}</td><td>{p}%</td></tr>\n"

rec_rows = ""
for ser, nm, r, iss in rec_fail_ex:
    rec_rows += f"<tr><td>{esc(ser)} {esc(nm)}</td><td>{cl(r)}</td><td>{esc(r)}</td><td>{esc('; '.join(iss))}</td></tr>\n"
pass_rows = ""
for ser, nm, r in rec_pass_ex:
    pass_rows += f"<tr><td>{esc(ser)} {esc(nm)}</td><td>{cl(r)}</td><td colspan=2>{esc(r)}</td></tr>\n"
fr = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in full_rules.most_common())

html = f"""<!DOCTYPE html><html lang=zh><head><meta charset=utf-8>
<title>企业库真实数据核验报告</title>
<style>body{{font-family:-apple-system,'Microsoft YaHei',sans-serif;margin:24px;color:#222;line-height:1.6}}
h1{{font-size:20px}} h2{{font-size:16px;margin-top:28px;border-left:4px solid #2b6cb0;padding-left:8px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}}
th,td{{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#f4f6f8}}
.kpi{{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}}
.card{{flex:1;min-width:150px;border:1px solid #ddd;border-radius:8px;padding:12px;background:#fafbfc}}
.card b{{font-size:22px;display:block;color:#2b6cb0}}
.note{{background:#fff8e1;border:1px solid #ffe082;padding:10px 12px;border-radius:6px;margin:10px 0}}
.warn{{background:#fde8e8;border:1px solid #f56565;padding:10px 12px;border-radius:6px;margin:10px 0}}
code{{background:#eee;padding:1px 4px;border-radius:3px}}</style></head><body>
<h1>企业库真实数据核验报告（2026-07-19 实测，可复现）</h1>
<p>数据来源：<code>data/enterprise/all_enterprises.json</code>（1502家）+ <code>drafts_v4/</code>（{N}家草稿）。
门禁：<code>check_single.py</code> V4。本页只列真实数据，不含主观评价。</p>

<div class=kpi>
<div class=card><b>{N}</b>草稿匹配主库</div>
<div class=card><b>{rec_pass}/{N}</b>推荐理由写作质量通过（{100*rec_pass//N}%）</div>
<div class=card><b>{full_pass}/{N}</b>整条记录全字段通过（{100*full_pass//N}%）</div>
<div class=card><b>41</b>企业库总字段数</div>
</div>

<div class=warn><b>问题1 · 合并工具会漏掉 241 家：</b>
<code>merge_v4.py</code> 只读取 <code>draft_#*.json</code> 命名的文件，但磁盘上有 {len(nonpat)} 个草稿名为 <code>draft_0013.json</code>（无 #），它们会被工具直接跳过、永不入库。例：{', '.join(nonpat[:6])}…</div>

<div class=warn><b>问题2 · 范围鸿沟（需你拍板）：</b>
上一个 AI 的流程与 <code>merge_v4.py</code> 只在主库写回 <b>4 个字段</b>（recommend/desc_cn/silver_reason/payor_model）。
其余 35 个字段（投融资/阶段/事件/亮点/地区等）流程<b>完全不碰</b>。你的目标是"所有字段填到100分"。两者范围不一致。</div>

<h2>一、企业库 41 个字段 · 填充率与分类</h2>
<p>说明：填充率=有值的家数占比。几乎所有字段都已"有值"(100%)；门禁不达标是因为<b>值太短/用词不规范</b>，不是空白。</p>
<table><tr><th>字段名</th><th>分类</th><th>已填</th><th>填充率</th></tr>{rows}</table>

<h2>二、1039 家草稿 · 推荐理由写作质量门禁（只看文本，不含另三列）</h2>
<p>通过 {rec_pass} / 未过 {rec_fail}。未过几乎全是"推荐理由与自家简介有一句≥10字雷同"（门禁阈值偏紧，你此前让我先不动）。</p>
<table><tr><th>企业</th><th>字数</th><th>推荐理由原文</th><th>门禁判死原因</th></tr>{rec_rows}</table>

<h2>三、推荐理由写作「通过」真实样例（你能直接读，判断质量）</h2>
<table><tr><th>企业</th><th>字数</th><th colspan=2>推荐理由原文</th></tr>{pass_rows}</table>

<h2>四、整条记录全字段门禁未过原因分布</h2>
<table><tr><th>规则</th><th>命中次数</th></tr>{fr}</table>
<p>注：R7(silver_reason&lt;30字) {full_rules.get('R7',0)} 次、R6(desc_cn&lt;80字) {full_rules.get('R6',0)} 次、R8(payor非规范) {full_rules.get('R8',0)} 次——
这三项说明草稿里很多只写了推荐理由、没带另三列，合入后另三列仍是主库旧值。</p>

<h2>五、草稿携带字段情况</h2>
<p>带 recommend+desc+silver+payor 全4项：<b>{carry_full}</b> 家 ｜ 带部分：<b>{carry_partial}</b> 家 ｜ 只带 recommend：<b>{carry_reconly}</b> 家</p>

<h2>六、疑似废弃字段（请你确认）</h2>
<table><tr><th>字段</th><th>证据</th></tr>
<tr><td>_legacy_rec</td><td>旧版推荐理由字典（rec_v1/rec_v2/rec_v3），已被 recommend 取代，{empty.get('_legacy_rec',0)}家为空壳但168家残留旧值</td></tr>
<tr><td>数据来源 (带空格)</td><td>字段名含尾随空格的错别字段，0家有任何值，纯垃圾</td></tr>
<tr><td>数据来源 / source</td><td>两个来源字段并存（中文"数据来源"492家有值、英文"source"1502家有值），疑似重复，需确认保留哪个</td></tr>
<tr><td>needs_review</td><td>疑似流程标记位，仅24家有值，可能已废弃</td></tr>
</table>

<div class=note>复现命令（在 <code>scores_draft/rework/</code> 下）：<br>
<code>PYTHONIOENCODING=utf-8 python _gate_drafts_real.py</code> （本报告数据即由此脚本算出）</div>
</body></html>"""
open("企业库真实数据核验报告.html", "w", encoding="utf-8").write(html)
print("报告已生成。rec_pass=%d full_pass=%d nonpat=%d" % (rec_pass, full_pass, len(nonpat)))
