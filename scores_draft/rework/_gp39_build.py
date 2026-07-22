# -*- coding: utf-8 -*-
"""general-purpose-39: batch_39 的 20 家 V5 编辑判断层推荐理由 + info/diff/copy 整数打分。
_is_v5_already=True -> 保留 current_recommend + 四舍五入补分
_is_v5_already=False -> 重写推荐 + 打分
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "drafts_v5")
SRC = os.path.join(HERE, "batches_score", "batch_39.json")
CHECK = os.path.join(HERE, "check_single.py")

batch = json.load(open(SRC, encoding="utf-8"))

# 8 家需重写
REWRITE = {
    "#1200": ("用消费级脑电帽读取神经信号、驱动偏瘫老人做肢体训练，比植入式方案门槛低、易进社区康复站，把高端脑机从医院搬到家门口的做法素材可挖（临床病例、设备成本都够拆）。差异在电极消费化、训练可视化；国内司羿智能、强脑科技做康复但偏器械，可学其'轻设备+社区站'思路，但信号精度受消费级硬件限制。", 6, 7, 6),
    "#1207": ("走侵入式高带宽路线、用柔性电极做神经疾病治疗与监测，比非植入方案信号更稳、专利壁垒高，这种'体内长期记录'的临床路径素材可挖（电极寿命、适配病症都够拆）。差异在柔性电极的微创与安全设计；国内脑虎科技同攻植入式但工艺不同，可学其'高端神经康复+长期监测'组合思路，但植入式审批与成本门槛极高。", 6, 7, 6),
    "#1220": ("用摄像头实时增强画面、让法定盲也能识别人脸与读字，把'电子视觉'做成可日常佩戴的眼镜而非手持放大镜，这种消费级低视力硬件路径素材可挖（佩戴舒适度、用户适配都够拆）。差异在电子增强替代光学放大；国内视氪科技、亮亮视野做低视力但偏AR，可学其'电子眼镜即服务'软硬件一体思路，但价格与验配仍是普及门槛。", 6, 7, 6),
    "#1225": ("医用级外骨骼帮脊髓损伤老人重建步态、拿下FDA与CE认证，把康复从平地训练做到真实行走，这种取证型康复硬件路径素材可挖（临床数据、医保覆盖都够拆）。差异在医用级步态重建而非健身助行；国内傅利叶智能、大艾机器人做康复外骨骼但偏训练，可学其'取证+医院渠道'打法，但医用设备审批与售价门槛高。", 7, 7, 5),
    "#1226": ("临床康复外骨骼进医院康复科、做卒中与脊髓损伤步态训练，把设备绑定到刚需康复流程而非健身房，这种科室级康复硬件路径素材可挖（科室渗透、疗程定价都够拆）。差异在临床刚需绑定与循证背书；国内大艾机器人、傅利叶智能同样做康复外骨骼，可学其'科室渠道+循证证据'打法，但进口设备价格与本地化服务是落地难点。", 7, 6, 5),
    "#1227": ("用游戏化训练做认知障碍早期干预、在英德已积累用户，把'脑健康'做成日常可坚持的轻量练习，这种早期筛查+训练一体路径素材可挖（留存曲线、训练模块都够拆）。差异在游戏化降低使用门槛、早筛早练；国内六六脑、脑动做认知训练但偏机构，可学其'消费级订阅+早筛'思路，但国内用户对付费脑训练接受度仍低。", 6, 6, 6),
    "#1228": ("神经康复APP按病历给个性化训练、覆盖中风与脑伤居家练习，把康复处方从医院延伸到家里，这种处方级神经康复路径素材可挖（病例库、训练有效性都够拆）。差异在处方级个性化与居家延续；国内六六脑做认知训练、卓道医疗做康复器械，可学其'医院开方+居家练'衔接思路，但国内处方流转与支付尚未打通。", 6, 7, 5),
    "#1232": ("循证脑训练平台背靠多项临床研究、做订阅制认知增强，把训练效果用论文背书变成可销售信任，这种研究驱动型脑训练路径素材可挖（研究设计、订阅留存都够拆）。差异在研究背书增信任、订阅可续；国内六六脑也做脑训练但缺循证积累，可学其'研究即营销'思路，但国内用户对循证付费意愿仍待培养。", 6, 7, 5),
}

results = []
for e in batch:
    s = e["serial"]
    if e.get("_is_v5_already"):
        rec = e["current_recommend"]
        info = int(round(float(e["current_info"])))
        diff = int(round(float(e["current_diff"])))
        copy = int(round(float(e["current_copy"])))
        mode = "KEEP"
    else:
        rec, info, diff, copy = REWRITE[s]
        mode = "REWRITE"
    doc = {"serial": s, "recommend": rec, "info": info, "diff": diff, "copy": copy}
    fp = os.path.join(OUT, f"draft_{s}.json")
    json.dump(doc, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    p = subprocess.run([sys.executable, CHECK, fp], capture_output=True, text=True)
    out = p.stdout.strip()
    results.append((s, mode, info, diff, copy, len(rec), out))

print(f"{'serial':7} {'mode':8} i/d/c  len  gate")
for s, mode, i, d, c, ln, gate in results:
    print(f"{s:7} {mode:8} {i}/{d}/{c}  {ln:3}  {gate}")

fails = [r for r in results if not r[6].startswith("PASS")]
print(f"\nTOTAL={len(results)} PASS={len(results)-len(fails)} FAIL={len(fails)}")
for r in fails:
    print("  FAIL", r)
