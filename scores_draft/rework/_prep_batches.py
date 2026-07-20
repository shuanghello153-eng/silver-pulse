import json, os
q=json.load(open("_rework_queue.json",encoding="utf-8"))
os.makedirs("_batches",exist_ok=True)
CH=12
for i in range(0,len(q),CH):
    chunk=q[i:i+CH]
    fn=f"_batches/batch_{i//CH+1:03d}.json"
    json.dump(chunk, open(fn,"w",encoding="utf-8"), ensure_ascii=False)
print(f"队列共 {len(q)} 家 -> {len(q)//CH + (1 if len(q)%CH else 0)} 批 (每批{CH})")
print("首批 batch_001:", q[:12])
