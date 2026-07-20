import json
dirty=json.load(open("_dirty_R10.json",encoding="utf-8"))["dirty_serials"]
gap=json.load(open("_gap_maindb.json",encoding="utf-8"))
allset=list(dict.fromkeys(dirty+gap))  # 保序去重
print(f"脏数据: {len(dirty)} | 缺口(dict/空): {len(gap)} | 合并去重: {len(allset)}")
json.dump(allset, open("_rework_queue.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("已存 _rework_queue.json")
