import json, os, glob
from pathlib import Path

HERE = Path('G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework').resolve()
DB = Path('G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json').resolve()

db = json.load(open(DB, 'r', encoding='utf-8'))
all_serials = set()
for e in db:
    s = e.get('serial') or e.get('id') or e.get('序号')
    if s:
        all_serials.add(s)
print(f"DB 企业总数: {len(db)} | 唯一序列号: {len(all_serials)}")

draft_dir = HERE / 'drafts_v4'
draft_serials = set()
for f in glob.glob(str(draft_dir / 'draft_*.json')):
    name = os.path.basename(f).replace('draft_','').replace('.json','')
    draft_serials.add(name)
print(f"drafts_v4 草稿文件数: {len(glob.glob(str(draft_dir/'draft_*.json')))}")
print(f"草稿唯一序列号: {len(draft_serials)}")

covered = all_serials & draft_serials
missing = all_serials - draft_serials
print(f"\n=== 覆盖情况 ===")
print(f"已覆盖: {len(covered)} ({len(covered)*100/len(all_serials):.1f}%)")
print(f"未覆盖: {len(missing)} ({len(missing)*100/len(all_serials):.1f}%)")

batch_dir = HERE / 'batches_full'
batch_files = sorted(glob.glob(str(batch_dir / 'batch_src_*.json')))
full_batches, partial_batches, empty_batches = [], [], []
for bf in batch_files:
    bno = os.path.basename(bf).replace('batch_src_','').replace('.json','')
    data = json.load(open(bf,'r',encoding='utf-8'))
    if isinstance(data, dict) and 'enterprises' in data:
        ents = data['enterprises']
    elif isinstance(data, list):
        ents = data
    else:
        ents = data.get('items', []) if isinstance(data, dict) else []
    serials_in_batch = [e.get('serial') or e.get('id') or e.get('序号') for e in ents if e.get('serial') or e.get('id') or e.get('序号')]
    if not serials_in_batch:
        continue
    cov = [s for s in serials_in_batch if s in draft_serials]
    mis = [s for s in serials_in_batch if s not in draft_serials]
    r = len(cov)*100/len(serials_in_batch)
    if r == 100:
        full_batches.append(bno)
    elif r == 0:
        empty_batches.append((bno, len(serials_in_batch)))
    else:
        partial_batches.append((bno, len(cov), len(serials_in_batch), int(r)))

print(f"\n=== 批次缺口 (76批) ===")
print(f"完全覆盖(100%): {len(full_batches)} 批")
print(f"部分覆盖: {len(partial_batches)} 批")
for b,c,t,r in partial_batches:
    print(f"  批{b}: {c}/{t} ({r}%)")
print(f"零覆盖: {len(empty_batches)} 批")
for b,n in empty_batches:
    print(f"  批{b}: {n}家")
