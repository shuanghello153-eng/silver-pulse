import json
fp="scores_draft/run_v2/out/batch_007_out.json"
d=json.load(open(fp,encoding="utf-8"))
new="信号中等、信息披露较充分（模式与定价公开可查），差异化极强：'去网络+透明定价+会员按节省分润'颠覆传统HMO/PPO；可复制性低，因国内商保以社保补充与基础医疗险为主、雇主直付福利不成熟——其'透明定价+分润'机制值得国内健康险产品借鉴。"
for e in d["enterprises"]:
    if e["serial"]=="#0853":
        e["recommend"]=new; print("fixed #0853 len",len(new))
json.dump(d,open(fp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
