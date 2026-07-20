# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as c

# 取库里一家真实企业当上下文
DB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data/enterprise/all_enterprises.json"))
d = json.load(open(DB, encoding="utf-8"))
e = next(x for x in d if str(x.get("serial")) == "#0565")
ctx = dict(e)

print("=== 好的样例（应 PASS）===")
good = dict(ctx)
good["recommend"] = ("被Optum收购的老年连锁诊所（收购额见投融资字段）。核心打法：用标准化预防护理+社区诊所做老年获客入口，"
                     "高医患比和社交化诊所有效黏住慢病老人。国内险企可借鉴其'诊所即流量入口'模式，但按人头付费的医保结构难直接照搬。")
print(c.validate(good))

print("=== 坏样例1：重复企业名 + 绝对化国内空白 + 技术黑话 ===")
bad1 = dict(ctx)
bad1["recommend"] = ("Oak Street Health 是国内空白的市场，靠并购补管线拿到CNS给药技术，"
                     "差异在血脑屏障突破，国内可复制。")
print(c.validate(bad1))

print("=== 坏样例2：与 desc_cn 整句雷同 ===")
bad2 = dict(ctx)
bad2["recommend"] = (ctx.get("desc_cn", "")[:25] + "信号与信息双高，模式可借鉴国内。") if ctx.get("desc_cn") else "测试雷同"
print("desc_cn前25:", ctx.get("desc_cn", "")[:25])
print(c.validate(bad2))

print("=== 坏样例3：泛泛而谈，无数字无tag ===")
bad3 = dict(ctx)
bad3["recommend"] = "这是一家值得关注的银发企业，差异化和可复制性都不错，国内可借鉴其思路，信息量也还可以。"
print(c.validate(bad3))
