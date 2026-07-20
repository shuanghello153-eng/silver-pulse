import json, os, glob, random
from pathlib import Path

HERE = Path('G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework').resolve()
drafts = sorted(glob.glob(str(HERE / 'drafts_v4' / 'draft_*.json')))
print(f"总草稿: {len(drafts)}")

# 随机抽30个看格式
random.seed(42)
sample = random.sample(drafts, min(30, len(drafts)))
stats = {'single_str':0, 'dict':0, 'other':0, 'empty':0, 'has_recommend':0, 'rec_len_ok':0}
issues = []
for f in sample:
    try:
        d = json.load(open(f,'r',encoding='utf-8'))
    except:
        stats['empty']+=1
        continue
    r = d.get('recommend')
    if r is None:
        stats['empty']+=1
        issues.append(f"{os.path.basename(f)}: 无recommend字段")
        continue
    stats['has_recommend']+=1
    if isinstance(r, str):
        stats['single_str']+=1
        if 60<=len(r)<=240:
            stats['rec_len_ok']+=1
        else:
            issues.append(f"{os.path.basename(f)}: 字数{len(r)}超范围")
    elif isinstance(r, dict):
        stats['dict']+=1
        issues.append(f"{os.path.basename(f)}: 三版dict(旧格式,需重写)")
    else:
        stats['other']+=1
        issues.append(f"{os.path.basename(f)}: 未知格式{type(r)}")

print(f"\n=== 抽样30家格式统计 ===")
print(f"单字符串(V4正确格式): {stats['single_str']}")
print(f"三版dict(旧格式,需重写): {stats['dict']}")
print(f"其他: {stats['other']}")
print(f"空/无recommend: {stats['empty']}")
print(f"字数60-240达标: {stats['rec_len_ok']}/{stats['has_recommend']}")
print(f"\n问题清单:")
for i in issues:
    print(f"  - {i}")

# 看一个通过的单条样例
for f in sample:
    d = json.load(open(f,'r',encoding='utf-8'))
    r = d.get('recommend')
    if isinstance(r,str) and 60<=len(r)<=240:
        print(f"\n=== 样例(合格单条) ===")
        print(f"serial: {d.get('serial')}")
        print(f"recommend ({len(r)}字): {r[:200]}")
        break
