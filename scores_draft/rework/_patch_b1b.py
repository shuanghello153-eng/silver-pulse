# -*- coding: utf-8 -*-
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts_v5")
def load(s): return json.load(open(os.path.join(D, "draft_"+s+".json"), encoding="utf-8"))
def save(s, d): json.dump(d, open(os.path.join(D, "draft_"+s+".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

d = load("#0349")
d["recommend"] = "这家口腔连锁龙头2023年录得28.47亿元营收、年种植量突破5万颗，近期受集采冲击量增价跌，信号值得跟踪。其90%收入来自浙江、单省密度极高的财报结构公开透明，信息量大。差异在它用'总院+分院'的区域深耕打法，和瑞尔齿科的一线城市高端单店路线错位。国内区域医疗连锁可参考其密度模型。适合写'银发口腔支付力'案例。"
save("#0349", d)
print("patched #0349")
