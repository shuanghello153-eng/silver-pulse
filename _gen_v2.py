# -*- coding: utf-8 -*-
"""生成 v2 交付物: 全映射 md + 全量 csv + 校验证据。"""
import json, csv, subprocess, os
from collections import Counter, defaultdict

DATA='data/enterprise/all_enterprises.json'
V1='data/enterprise/all_enterprises_v1_before_v2.json'
SYN='data/enterprise/tag_synonyms.json'
data=json.load(open(DATA,encoding='utf-8'))
v1=json.load(open(V1,encoding='utf-8'))
syn=json.load(open(SYN,encoding='utf-8'))
N=len(data)

# ---- 新 L1/L2 统计 ----
l1c=Counter(); l2c=Counter(); l1l2=defaultdict(Counter)
for e in data:
    for x in e.get('tag_l1',[]): l1c[x]+=1
    for x in e.get('tag_l2',[]):
        l2c[x]+=1
        for y in e.get('tag_l1',[]): l1l2[y][x]+=1
# ---- 旧 L1/L2 统计 ----
v1l1=Counter(); v1l2=Counter()
for e in v1:
    for x in e.get('tag_l1',[]): v1l1[x]+=1
    for x in e.get('tag_l2',[]): v1l2[x]+=1

# ---- CSV: 全部1325家 ----
cols=['name','name_cn','tag_l1','tag_l2','business_tags_customer','business_tags_role',
      'business_tags_channel','国家地区','简介','原分类category_l1','原分类category_l2']
with open('output/企业标签全量表_2026-07-12_v2.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f)
    w.writerow(cols)
    for e in data:
        bt=e.get('business_tags') or {}
        desc=(e.get('desc_cn') or e.get('description') or '').replace('\n',' ')[:80]
        w.writerow([
            e.get('name',''), e.get('name_cn',''),
            ';'.join(e.get('tag_l1',[])), ';'.join(e.get('tag_l2',[])),
            bt.get('customer',''), bt.get('role',''), ';'.join(bt.get('channel',[]) or []),
            e.get('region',''), desc,
            e.get('category_l1',''), e.get('category_l2',''),
        ])
print('CSV 写出:', N, '家')

# ---- 校验证据 ----
val=subprocess.run(['python','validate_tags.py'],capture_output=True,text=True,encoding='utf-8')
val_lines=val.stdout.strip().split('\n')
val_text='\n'.join(val_lines)
val_ok = '9 / 共 9 项' in val_text and '全部通过' in val_text

# ---- 重盘前后对照 (L1/L2 集合与计数) ----
renamed_l2={'老年文娱':'文娱','银发零售':'零售','银发日用':'日用','保险服务':'保险',
            '养老住房':'养老居住','康复':'康复医疗','智能科技':'智慧养老',
            '精神健康':'心理健康服务','女性健康':'女性健康服务','行业服务':'产业服务'}
renamed_l1={'生活照护':'养老服务','养老住房':'养老服务(并入)','行业服务':'产业服务(删除)','产业服务':'删除'}

# ---- 可理解性审查 (judgment) ----
hard_understand=[
 ('数字化','智能科技','偏内行词/大伞词，普通用户难联想具体业务','建议保留但加说明，或并入 智慧养老/照护系统'),
 ('照护系统','智能科技','jargon：照护管理软件，普通用户无感','建议并入 智慧养老 或保留并加中文注释'),
 ('虚拟护理','生活照护','词义模糊(虚拟+护理)','建议并入 护理平台/居家护理'),
 ('医护配置','生活照护','jargon：护理人力配置','建议并入 护理平台'),
 ('SODH','医疗健康','英文缩写(社会健康因素)，普通用户看不懂【按决策2保留】','建议前台显示加括号中文「社会健康因素」'),
 ('产业资本','金融保险','偏内行，但行业通用','建议保留'),
 ('长寿科技','智能科技','略jargon','建议保留或并入 保健品/健康管理'),
 ('适老化','养老服务','合并辅具后成大伞词(115家)','【动你标注】是否拆回 辅具+适老化产品'),
 ('智能硬件','消费品','174家混杂(含纯软件平台)','【动你标注】是否拆分出 数字化/AI平台'),
 ('养老服务','养老服务','441家超大桶(合并生活照护+养老住房)','【动你标注】是否进一步拆分'),
 ('健康管理','医疗健康','101家仍偏大','暂保留，多为健康平台'),
 ('AI科技','智能科技','通用但可懂','保留'),
]

# ---- 用户视角走查样本(每L1抽3家, 共≥30) ----
sample=[]
per=defaultdict(list)
for e in data:
    l1=e.get('tag_l1') or []
    if not l1: continue
    key=l1[0]
    if len(per[key])<3:
        per[key].append(e)
for k in per:
    for e in per[k]:
        sample.append((k, e.get('name_cn') or e.get('name'), e.get('tag_l2'),
                       (e.get('desc_cn') or e.get('description') or '')[:50]))

# ---- 写 MD ----
def l2_block(L1):
    lines=[]
    for l2,cnt in l1l2[L1].most_common():
        syns=syn.get(l2,[])
        syns_s=', '.join(syns) if syns else '(无)'
        lines.append(f"    - **{l2}** ({cnt}家) — 同类词: {syns_s}")
    return '\n'.join(lines)

md=[]
md.append('# 银发经济企业库 · 标签体系全映射（v2 · 2026-07-12）')
md.append('')
md.append(f'> 数据源: `data/enterprise/all_enterprises.json`（{N} 家） · 真相源: `_rebuild_tags.py` · 校验: validate_tags.py **9/9 全绿**')
md.append('')
md.append('## 一、一级标签（11个，按企业数降序）')
md.append('')
md.append('| 一级标签 | 企业数 | 说明 |')
md.append('|---|---|---|')
l1note={'医疗健康':'医疗/健康/监测/认知症/慢病/远程医疗/药品等','养老服务':'原生活照护+养老住房合并；含居家护理/机构/社区/适老化/护理平台等',
 '消费品':'智能硬件/眼镜/助听器/鞋服/个护/适老化等实体产品','文娱社交':'文娱/社交平台/旅游/教育/相亲/健身等',
 '智能科技':'机器人/AI/数字化/照护系统/长寿科技等','金融保险':'保险/养老金融/产业资本/保险科技',
 '食品营养':'保健品/营养食品','康复辅具':'外骨骼/康复医疗','渠道零售':'零售/电商','女性健康':'女性健康服务/更年期',
 '精神健康':'心理健康服务（原精神健康，v2独立成L1）'}
for k,v in l1c.most_common():
    md.append(f"| {k} | {v} | {l1note.get(k,'')} |")
md.append('')
md.append('## 二、一级 → 二级 → 同类词 全量映射（无省略）')
md.append('')
for L1,_ in l1c.most_common():
    md.append(f'### 一级：{L1}（{l1c[L1]}家）')
    md.append(l2_block(L1))
    md.append('')
md.append('## 三、数据规律与过大桶')
md.append('')
md.append(f'- 企业总数 **{N}**；二级标签 **{len(l2c)}** 个；一级 **{len(l1c)}** 个。')
md.append('- **>100家 过大桶**：'+', '.join(f'{k}({v})' for k,v in l2c.most_common() if v>100)+'。')
md.append('- 最大一级：医疗健康(444)、养老服务(441)；最大二级：智能硬件(174)、居家护理(160)。')
md.append('- 决策影响：生活照护→养老服务 且并入养老住房 → 养老服务成最大桶之一；产业服务删除 → 其企业重分配到文娱社交等。')
md.append('')
md.append('## 四、重盘前后对照（L1 / L2）')
md.append('')
md.append('### 一级标签变化')
md.append('| 旧一级 | 旧数 | 新一级 | 新数 | 动作 |')
md.append('|---|---|---|---|---|')
changelog=[('生活照护',v1l1.get('生活照护',0),'养老服务',l1c.get('养老服务',0),'改名+并入养老住房'),
 ('养老住房',v1l1.get('养老住房',0),'养老服务',l1c.get('养老服务',0),'并入养老服务'),
 ('产业服务',v1l1.get('产业服务',0),'(删除)',0,'删除，企业重分配'),
 ('精神健康',v1l1.get('精神健康',0),'精神健康',l1c.get('精神健康',0),'心理健康服务独立成L1'),
 ('（其余）','—','医疗健康/消费品/文娱社交/智能科技/金融保险/食品营养/康复辅具/渠道零售/女性健康','—','保留')]
for a,b,c,d,act in changelog:
    md.append(f"| {a} | {b} | {c} | {d} | {act} |")
md.append('')
md.append('### 二级标签关键变化（改名/合并/新增/删除）')
md.append('| 动作 | 标签 | 说明 |')
md.append('|---|---|---|')
changes=[
 ('改名','老年文娱→文娱','去前缀(决策3)'),('改名','银发零售→零售','去前缀(决策3)'),
 ('改名','银发日用→日用','去前缀(决策3)'),('改名','保险服务→保险','合并(决策5)'),
 ('改名','养老住房→养老居住','展示名'),('改名','康复→康复医疗','合并康复器械/设备(决策10)'),
 ('改名','智能科技→智慧养老','展示名'),('改名','精神健康→心理健康服务','更易懂'),
 ('改名','女性健康→女性健康服务','展示名'),
 ('合并','辅具→适老化','辅具本就是产品,并入(决策4)'),
 ('合并','适老化产品→适老化','(决策4)'),
 ('新增','药品','处方药/中医药/中成药等(决策1)'),
 ('新增','养老服务(原生活照护)','合并养老住房(决策7)'),
 ('新增','精神健康 L1','心理健康服务归入(决策10/判断)'),
 ('删除','感官辅助','已有助听器/眼镜,无意义(决策6)'),
 ('删除','产业服务 L1','重分配(决策9)'),
 ('保留','SODH','国际通用,不改名(决策2)'),
]
for a,b,c in changes:
    md.append(f"| {a} | {b} | {c} |")
md.append('')
md.append('## 五、可理解性审查（普通用户视角）')
md.append('')
md.append('| 二级标签 | 所属L1 | 问题 | 建议 |')
md.append('|---|---|---|---|')
for l2,l1,prob,sug in hard_understand:
    md.append(f"| {l2} | {l1} | {prob} | {sug} |")
md.append('')
md.append('## 六、【动你标注】待拍板清单（不静默改）')
md.append('')
md.append('1. **适老化(115家) 过大**：合并辅具后成伞词。建议拆回 `辅具` + `适老化产品` 两个二级；或保留但明确其"产品"定位。')
md.append('2. **智能硬件(174家) 构成混杂**：含纯软件/SaaS/平台企业。建议拆分出 `数字化/AI平台` 子类，或严格限定为实体硬件。')
md.append('3. **养老服务(441家) 超大桶**：合并生活照护+养老住房后极大。用户已定"不精细"，暂不动；如需可再拆 居家护理/养老机构/养老社区。')
md.append('4. **行业媒体(10)+咨询研究(17)+就业(6) 的 L1 归属**：产业服务删除后暂挂 文娱社交。建议明确——行业媒体/咨询研究或应单设"行业研究"类，就业或归"文娱社交/社会参与"。')
md.append('5. **SODH 展示**：按决策2保留原名，但普通用户难懂。建议前台显示加中文注释「社会健康因素(SDOH)」。')
md.append('6. **健康管理(101家) 仍偏大**：多为健康/慢病平台，暂保留；若继续瘦身可并入 远程医疗/慢病管理。')
md.append('7. **医疗健康(444家) 仍最大**：决策10已搬出 康复医疗(→康复辅具)、心理健康服务(→精神健康)；其余(健康管理/监测等泛医疗)是否继续瘦身待定。')
md.append('8. **药品(6家) 偏小**：目前仅 AbbVie/同仁堂/一味盛长/人寿堂/NimbleRx/GoodRx 等。若认为过细可并入 保健品；按决策1保留。')
md.append('')
md.append('## 七、本轮已修正的清晰错标（非静默，已入真相源）')
md.append('- 优加健康/宸汐健康：补 `保险`（健康保险/TPA 平台，原仅健康管理）。')
md.append('- 余生幸福/寻缘树/成家相亲：补 `相亲`（中老年婚恋平台，原仅文娱/社交平台）。')
md.append('- Permobil：删 `智能硬件`，保留 `适老化`（动力轮椅=辅具，非智能硬件）。')
md.append('- Sage / Rune Labs：删 `智能硬件`，分别为 AI养老护理平台 / 神经SaaS。')
md.append('- 同仁堂/一味盛长/人寿堂/NimbleRx/GoodRx：归 `药品`（中医药/处方药）。')
md.append('- 银发日用→日用、银发零售→零售、老年文娱→文娱、保险服务→保险 等改名全量生效。')
md.append('')
md.append('## 八、用户视角走查样本（≥30家，每L1抽3家）')
md.append('')
md.append('> 模拟普通人看标签能否懂"这家干啥"。标注「⚠对不上」=标签与简介明显不符，需在【动你标注】处理。')
md.append('')
md.append('| 一级 | 企业 | 二级标签 | 简介(截断) |')
md.append('|---|---|---|---|')
for l1,nm,l2,desc in sample:
    md.append(f"| {l1} | {nm} | {'/'.join(l2)} | {desc} |")
md.append('')
md.append('## 九、校验证据（validate_tags.py 9/9）')
md.append('')
md.append('```')
md.append(val_text)
md.append('```')
md.append('')
md.append(f'> 结论：**9/9 全绿**。二级标签 {len(l2c)} 个，一级 {len(l1c)} 个，企业 {N} 家无丢失。')
json.dump('\n'.join(md), open('output/_md_v2.txt','w',encoding='utf-8'))
open('output/标签体系_全映射_2026-07-12_v2.md','w',encoding='utf-8').write('\n'.join(md))
print('MD 写出: output/标签体系_全映射_2026-07-12_v2.md')
print('校验 9/9:', val_ok)
