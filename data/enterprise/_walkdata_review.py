# -*- coding: utf-8 -*-
"""walk-data 数据质量审查脚本（只读，不改库）"""
import json, re
from collections import Counter, defaultdict

PATH = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json'
with open(PATH, encoding='utf-8') as f:
    data = json.load(f)

N = len(data)
print('='*70)
print('企业总数:', N)

# ---- 批次识别 ----
batch_B = [d for d in data if d.get('ingest_time')]   # 供需对接(有 ingest_time)
batch_B_marker = [d for d in data if '【提供资源】' in str(d.get('desc_cn','')) or '【需求资源】' in str(d.get('desc_cn',''))]
print('批次B(有 ingest_time):', len(batch_B))
print('批次B(含【提供资源】/【需求资源】):', len(batch_B_marker))

# ---- 检查1: 模板残留扫描 ----
# 模板句式: "面向银发人群的…企业" / "主营…相关的产品" / 其他套模板空话
tpl_patterns = [
    r'面向银发人群',          # 经典模板开头
    r'相关的产品',             # "主营…相关的产品"
    r'是一家致力于', 
    r'是一家专注于',
    r'致力于为.*提供',
    r'主营业务包括',
    r'一站式.*解决方案',
    r'一体化解决方案',
]
def template_hits(s):
    if not s: return []
    hits=[]
    for p in tpl_patterns:
        if re.search(p, s):
            hits.append(p)
    return hits

residue=[]
for d in data:
    s = str(d.get('desc_cn',''))
    # 排除否定语境 "并非专门面向银发人群"
    if '并非专门面向银发人群' in s or '并非专门面向' in s or '不是专门面向' in s:
        continue
    h = template_hits(s)
    if h:
        residue.append((d, h, s))

print('\n'+'='*70)
print('【检查1】模板残留扫描: 命中', len(residue), '家 (已排除否定语境)')
for d,h,s in residue[:30]:
    print(' -', d.get('name'), '|', d.get('source'), '|', h, '|', s[:80])

# ---- 检查2: 空简介扫描 ----
def is_empty(v, th=10):
    if v is None: return True
    s=str(v).strip()
    return len(s) < th
empty=[]
for d in data:
    cn = d.get('desc_cn')
    en = d.get('description')
    if is_empty(cn) and is_empty(en):
        empty.append(d)
    elif is_empty(cn) and not is_empty(en):
        # desc_cn 空但英文有 -> 也计入"中文简介空"
        empty.append(d)
print('\n'+'='*70)
print('【检查2】空/极短简介扫描(desc_cn与description都<10字或缺失):', len(empty))
# 仅 desc_cn 空
cn_empty=[d for d in data if is_empty(d.get('desc_cn'))]
print('  其中仅 desc_cn 为空/极短:', len(cn_empty))
for d in empty[:30]:
    print(' -', d.get('name'), '|', 'cn=', repr(str(d.get('desc_cn'))[:30]), '| en=', repr(str(d.get('description'))[:30]))

# ---- 检查4: 异常标签组合 ----
# 定义互斥/罕见共存标签
conflict_pairs = [
    ('投资机构','居家护理'),
    ('投资机构','养老机构'),
    ('投资机构','适老化'),
    ('养老机构','智能硬件'),
    ('投资机构','老年食品'),
    ('行业媒体','养老机构'),
    ('医药研发','养老机构'),
]
def tags_of(d):
    l1 = d.get('tag_l1') or []
    l2 = d.get('tag_l2') or []
    return set(l1), set(l2)

anomalies=[]
for d in data:
    l1,l2 = tags_of(d)
    alltags = l1 | l2
    for a,b in conflict_pairs:
        if a in alltags and b in alltags:
            anomalies.append((d, a, b))
# 也找: 同时挂多个一级大类的极端混杂
for d in data:
    l1,_ = tags_of(d)
    if len(l1)>=3:
        anomalies.append((d,'MANY_L1', ','.join(sorted(l1))))
print('\n'+'='*70)
print('【检查4】异常/矛盾标签组合:', len(anomalies))
seen=set()
for d,a,b in anomalies:
    key=d.get('name')
    if key in seen: continue
    seen.add(key)
    l1,l2=tags_of(d)
    print(' -', d.get('name'),'| L1=',list(l1),'| L2=',list(l2),'| 冲突:',a,'+',b)

# ---- 检查5: 重复企业 ----
# 按 name 与 name_cn 归并找重复
by_name=defaultdict(list)
by_namecn=defaultdict(list)
for d in data:
    nm=str(d.get('name','')).strip().lower()
    ncn=str(d.get('name_cn','')).strip().lower()
    if nm: by_name[nm].append(d)
    if ncn: by_namecn[ncn].append(d)

dup_name=[(k,v) for k,v in by_name.items() if len(v)>1]
dup_cn=[(k,v) for k,v in by_namecn.items() if len(v)>1]
print('\n'+'='*70)
print('【检查5】按 name 重复的组:', len(dup_name), '| 按 name_cn 重复的组:', len(dup_cn))
for k,v in dup_name:
    print('  NAME重复:', repr(k), '->', [ (x.get('name'), x.get('name_cn'), x.get('serial'), x.get('source')) for x in v])
for k,v in dup_cn:
    print('  NAME_CN重复:', repr(k), '->', [ (x.get('name'), x.get('name_cn'), x.get('serial'), x.get('source')) for x in v])

# 模糊相似(name 去掉空格/标点后前缀相同)
def norm(s):
    return re.sub(r'[\s\u3000()（）·・\-—_]+','', str(s).lower())
groups=defaultdict(list)
for d in data:
    groups[norm(d.get('name',''))].append(d)
fuzzy=[(k,v) for k,v in groups.items() if len(v)>1 and k]
print('  归一化后 name 模糊重复组:', len(fuzzy))
for k,v in fuzzy[:20]:
    print('    FUZZY:', repr(k), '->', [(x.get('name'),x.get('name_cn'),x.get('serial')) for x in v])

# ---- 检查3: 一致性抽查(抽样输出) ----
print('\n'+'='*70)
print('【检查3】标签-业务吻合度抽样(待人工判断)')
import random
random.seed(20260628)
# 抽: 批次B 10家 + 批次A疑似模板残留(从 residue 取,不足则补) + 普通随机抽样15家
sample_B = random.sample(batch_B, min(10, len(batch_B)))
sample_normal = random.sample([d for d in data if d not in batch_B], min(15, N-len(batch_B)))
sample = sample_B + sample_normal
random.shuffle(sample)
print('抽样数:', len(sample))
for i,d in enumerate(sample):
    l1,l2=tags_of(d)
    s=str(d.get('desc_cn',''))
    print(f'\n[{i+1}] {d.get("name")} ({d.get("name_cn","")})  serial={d.get("serial")} source={d.get("source")}')
    print('   L1=',list(l1),' L2=',list(l2))
    print('   desc_cn:', s[:160])
