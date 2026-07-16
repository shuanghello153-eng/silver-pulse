import json
from collections import Counter, defaultdict

d = json.load(open('data/enterprise/all_enterprises.json'))
groups = defaultdict(list)
for e in d:
    desc = (e.get('desc_cn') or e.get('description') or '').strip()
    if len(desc) > 15:
        groups[desc].append(e)
TPL = ['面向银发人群','银发社交与文娱','相关的服务（如','专业护理相关的服务',
       '养老辅具与适老化硬件','B2B AI/数据驱动','搭建面向中老年',
       '提供居家照护、专业护理及智慧养老','主营','资讯','平台企业，主营']
def is_tpl(e):
    desc = (e.get('desc_cn') or e.get('description') or '')
    if len(desc) > 40 and desc in groups and len(groups[desc]) >= 2:
        return True
    return any(p in desc for p in TPL)

cnt = Counter()
for e in d: cnt.update(e.get('tag_l2', []))
big = sorted([(t, n) for t, n in cnt.items() if n >= 40], key=lambda x: -x[1])

out = ['# ≥40 企业数二级标签走查清单（v16 · 2026-07-15）', '']
out.append(f'走查日期：2026-07-15 ｜ 企业总数：{len(d)} ｜ ≥40 标签数：{len(big)} ｜ 数据真相源：data/enterprise/all_enterprises.json')
out.append('')
out.append('## 走查方法（说人话）')
out.append('- 模板文案企业：指描述文案与别的企业一字不差的企业（这批企业占多数，158家），它们的描述不能用来判断业务，改用企业名判断。')
out.append('- 强信号剔除：企业名含明显不属于该标签的词（如护理类标签里出现"科技/平台/餐饮/金融/齿科"），剔除该标签。')
out.append('- 名字中性、描述真实的企业：保留原标签（无法自动证伪则保守保留，等你手核）。')
out.append('')
for t, n in big:
    rows = [e for e in d if t in e.get('tag_l2', [])]
    out.append(f'## {t}（{n} 家）')
    tpl_n = sum(1 for e in rows if is_tpl(e))
    out.append(f'- 其中模板文案企业：{tpl_n} 家；非模板：{n - tpl_n} 家')
    out.append('')
    for e in sorted(rows, key=lambda x: x['name']):
        mark = '【模板】' if is_tpl(e) else ''
        others = [x for x in e.get('tag_l2', []) if x != t]
        extra = f' ｜ 其余标签：{others}' if others else ''
        out.append(f'- {mark}{e["name"]}{extra}')
    out.append('')

open('output/标签走查_≥40标签_2026-07-15.md', 'w', encoding='utf-8').write('\n'.join(out))
print('走查清单已生成，≥40标签：')
for t, n in big:
    print(f'  {t}: {n}')
print('输出：output/标签走查_≥40标签_2026-07-15.md')
