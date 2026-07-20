import json, os
BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
d = json.load(open(DB, encoding="utf-8"))
by = {e["serial"]: e for e in d}

# 选高优先级：research_value 降序，优先有 dict3 推荐理由（可复用材料）
def has3(e):
    r = e.get("recommend")
    return isinstance(r, dict) and {"rec_v1", "rec_v2", "rec_v3"} <= set(r.keys())

ranked = sorted(d, key=lambda e: float(e.get("research_value") or 0), reverse=True)
picked = [e for e in ranked if has3(e)][:30]
if len(picked) < 30:
    picked += [e for e in ranked if e not in picked][:30 - len(picked)]

keys = ["serial", "name", "name_cn", "region", "tag_l1", "tag_l2", "stage",
        "funding_latest", "funding_total", "investors", "business_model",
        "business_model_cn", "desc_cn", "recommend", "signal_strength",
        "info_score", "diff_score", "copy_score", "research_value",
        "silver_verdict", "silver_reason", "payor_model"]
out = []
for e in picked:
    out.append({k: e.get(k) for k in keys})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pilot_src.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("picked:", len(out), "| research_value range:", out[0]["research_value"], "->", out[-1]["research_value"])

# 合并校验样例：取 3 个 dict3，把三版拼起来看是否合格
print("\n===== 合并校验样例（rec_v1+v2+v3 直接拼接）=====")
import textwrap
for e in picked[:3]:
    r = e["recommend"]
    print(f"\n### {e['serial']} {e.get('name')} (rv={e.get('research_value')})")
    print("v1:", r.get("rec_v1"))
    print("v2:", r.get("rec_v2"))
    print("v3:", r.get("rec_v3"))
    merged = r.get("rec_v1", "") + r.get("rec_v2", "") + r.get("rec_v3", "")
    print(f">>> 拼接后({len(merged)}字): {merged}")
