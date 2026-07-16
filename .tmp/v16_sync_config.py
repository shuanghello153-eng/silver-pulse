import json, re
from collections import defaultdict

l2l1 = json.load(open('data/enterprise/_l2_l1.json'))
L1_ORDER = ['产业资本','养老服务','医疗健康','康复辅具','文娱社交','智能科技','消费品','渠道零售','金融保险','食品营养']

# 主L1归属（避免重复）：取每个标签的第一个父L1
cat = {l1: [] for l1 in L1_ORDER}
for t, parents in l2l1.items():
    if not parents:
        continue
    main = parents[0]
    if main in cat and t not in cat[main]:
        cat[main].append(t)
for l1 in cat:
    cat[l1].sort()

text = open('config.py', encoding='utf-8').read()
m = re.search(r'ENTERPRISE_CATEGORIES\s*=\s*\{', text)
start_brace = m.end() - 1
depth = 0
end_brace = start_brace
for i in range(start_brace, len(text)):
    if text[i] == '{': depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            end_brace = i
            break
new_block = 'ENTERPRISE_CATEGORIES = ' + json.dumps(cat, ensure_ascii=False, indent=2)
new_text = text[:m.start()] + new_block + text[end_brace + 1:]
open('config.py', 'w', encoding='utf-8').write(new_text)

# 验证 import
import importlib.util
spec = importlib.util.spec_from_file_location('cfg', 'config.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
total = sum(len(v) for v in mod.ENTERPRISE_CATEGORIES.values())
print(f'config OK | L1={len(mod.ENTERPRISE_CATEGORIES)} | 二级标签总数(含跨L1唯一)={total}')
for l1 in L1_ORDER:
    print(f'  {l1}: {len(mod.ENTERPRISE_CATEGORIES.get(l1,[]))} 个')
