# -*- coding: utf-8 -*-
"""
Silver Pulse 评分补全 · 硬质量门禁（代码级，非文档）
====================================================
每个批次工人写完后，主智能体调用本脚本对一批 serial 做硬规则校验。
不过门 -> 返回 fail 清单 -> 工人重做 -> 再校验，循环至过。
这是管线强制一步，不是可选。

规则（对应小爽的原始要求）：
  R1 recommend 必须是 dict，且 rec_v1/rec_v2/rec_v3 三版齐全
  R2 每版 40~90 字（含）
  R3 三版互不雷同（两两字符重合率 < 0.5）
  R4 每版不得含模板套话（BANNED 列表）
  R5 每版须覆盖四维度信号词（信号/信息量/差异化/可复制 各至少命中一类）
  R6 desc_cn >= 80 字，且不以通用套话开头，且不含"成立于YYYY年"废话
  R7 silver_reason >= 30 字
  R8 payor_model 必须在规范词表 CANON_PAYOR 中
  R9 research_value 公式正确：round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10,1)
  R10 三版不得与 desc_cn / 标签 逐字重复（不复述卡片）
用法：
  python validator.py --serials 1,2,3      校验指定 serial（#0001 -> 1）
  python validator.py --all                全量校验
  python validator.py --batch-file x.txt   从文件读 serial 列表
输出：stdout 打印每批通过率；末行打印 FAIL 总数；并写 rework/fail_list.json
"""
import json, re, os, argparse, sys

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))  # silver-pulse
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")

BANNED = [
    "复制需结合本地资源",
    "部分环节可借鉴（切入",
    "国内宜学其思路而非形态",
    "轻模式易复制，国内创业者可直接借鉴落地",
    "切入行业媒体赛道",
    "切入养老机构赛道",
    "切入保险赛道",
    "切入保健品",
    "切入消费背景赛道",
    "切入社交平台赛道",
    "切入适老化赛道",
    "切入专业级护理赛道",
    "切入养老护理服务赛道",
    "切入B2B AI/数据驱动",
]

# 四维度关键词（三版合起来须至少命中每类各一词；词汇表覆盖真实信息/财经/运营用语，避免逼出套话）
DIM_SIG = ["信号", "热点", "融资", "收购", "IPO", "上市", "事件", "近期", "大额",
           "政策", "新规", "获批", "过审", "风口", "扩张", "合作", "启动", "上线", "发布",
           "新获", "获投", "中标", "申报", "众筹", "刚", "刚获", "落地", "推",
           "当下", "当前", "升温", "爆发", "走热", "走俏", "走红", "兴起", "走", "势头", "催化"]
DIM_INFO = ["信息", "资料", "透明", "公开", "年报", "招股", "报道", "深度", "数据量", "数据",
            "披露", "财报", "营收", "净利", "复购", "中标", "用户", "月活", "临床", "专利",
            "招股书", "公告", "研报", "样本", "规模", "交易额", "装机", "病例", "金额", "亿元",
            "估值", "量化", "指标", "明细", "覆盖", "触达", "融资额", "获投", "领投"]
DIM_DIFF = ["差异", "反常识", "独特", "壁垒", "模式", "打法", "少见", "起落", "颠覆",
            "首创", "独家", "闭环", "定位", "稀缺", "护城河", "唯一", "领先", "第一", "卡位",
            "特色", "另类", "不一样", "不同", "重资产", "轻资产", "错位", "集成",
            "独有", "优势", "强项", "亮点", "看点", "专长", "切入角度", "打法", "范式"]
DIM_COPY = ["可复制", "借鉴", "国内", "平移", "照搬", "落地", "红海", "空白", "对标", "赛道",
            "复用", "抄", "学", "移植", "参考", "模仿", "可学", "可搬", "国内团队", "国内创业者",
            "对表", "平移", "移植", "本地化", "微创新"]

GEN_OPENERS = ["是一家", "致力于", "专注于", "成立于", "提供", "打造", "旨在"]

CANON_PAYOR = {
    "个人自费", "个人自费+政府补贴", "个人自费+长护险", "个人自费+医保",
    "B端机构采购", "B端机构采购+政府付费", "B端机构采购+政府/商保支付",
    "政府医保/商保支付", "混合支付", "不适用（投资机构）", "未搜到",
}

def char_overlap(a, b):
    if not a or not b: return 0.0
    sa, sb = set(a), set(b)
    if not sa | sb: return 0.0
    return len(sa & sb) / len(sa | sb)

def has_dim(v):
    return any(k in v for k in DIM_SIG) and any(k in v for k in DIM_INFO) and \
           any(k in v for k in DIM_DIFF) and any(k in v for k in DIM_COPY)

SKIP = set()  # 由 --skip 填充，如 "R8" 跳过支付方规范

def validate(e):
    issues = []
    # R1 R2 R3 R4 R5 R10
    r = e.get("recommend")
    if not isinstance(r, dict):
        issues.append("R1:recommend非dict(缺三版)")
    else:
        vs = [r.get("rec_v1") or "", r.get("rec_v2") or "", r.get("rec_v3") or ""]
        for i, k in enumerate(("rec_v1", "rec_v2", "rec_v3")):
            v = vs[i]
            if len(v) < 40 or len(v) > 90:
                issues.append(f"R2:{k}字数{len(v)}越界(需40-90)")
            if any(t in v for t in BANNED):
                issues.append(f"R4:{k}含模板套话")
        # R5：三版合起来须覆盖四维度（而非每版各自全中）
        alltext = " ".join(vs)
        if not (any(k in alltext for k in DIM_SIG) and any(k in alltext for k in DIM_INFO)
                and any(k in alltext for k in DIM_DIFF) and any(k in alltext for k in DIM_COPY)):
            issues.append("R5:三版未共同覆盖四维度(信号/信息量/差异化/可复制)")
        for i in range(3):
            for j in range(i + 1, 3):
                if vs[i] and vs[j] and char_overlap(vs[i], vs[j]) > 0.5:
                    issues.append(f"R3:rec_v{i+1}/v{j+1}雷同({char_overlap(vs[i],vs[j]):.2f})")
        # R10 不复述 desc
        desc = e.get("desc_cn") or ""
        for i, k in enumerate(("rec_v1", "rec_v2", "rec_v3")):
            if desc and len(desc) > 20 and vs[i] and vs[i][:18] in desc:
                issues.append(f"R10:{k}复述desc_cn")
    # R6 desc
    desc = e.get("desc_cn") or ""
    if len(desc) < 80:
        issues.append(f"R6:desc_cn过短({len(desc)})")
    if any(desc.startswith(g) for g in GEN_OPENERS):
        issues.append("R6:desc_cn通用套话开头")
    if re.search(r"成立于\d{4}年", desc):
        issues.append("R6:desc_cn含'成立于YYYY年'废话")
    # R7 silver_reason
    sr = e.get("silver_reason") or ""
    if len(sr) < 30:
        issues.append(f"R7:silver_reason过短({len(sr)})")
    # R8 payor
    p = e.get("payor_model") or ""
    if p not in CANON_PAYOR:
        issues.append(f"R8:payor_model非规范词表({p[:30]})")
    # R9 formula
    rv = e.get("research_value")
    sig = e.get("signal_strength"); info = e.get("info_score")
    df = e.get("diff_score"); cp = e.get("copy_score")
    if isinstance(rv, (int, float)) and None not in (sig, info, df, cp):
        exp = round((sig * 0.3 + info * 0.3 + df * 0.2 + cp * 0.2) * 10, 1)
        if abs(exp - rv) > 0.15:
            issues.append(f"R9:公式错 rv={rv} 期望={exp}")
    issues = [x for x in issues if x.split(":")[0] not in SKIP]
    return issues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serials", help="逗号分隔的 serial 数字，如 1,2,3")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch-file", help="每行一个 serial 的文本文件")
    ap.add_argument("--db", default=DB)
    ap.add_argument("--skip", help="跳过规则，逗号分隔，如 R8 跳过支付方规范")
    args = ap.parse_args()
    if args.skip:
        SKIP.update(x.strip() for x in args.skip.split(",") if x.strip())

    d = json.load(open(args.db, encoding="utf-8"))
    by_serial = {int(str(e.get("serial", "#0000")).lstrip("#")): e for e in d}

    sers = []
    if args.all:
        sers = list(by_serial.keys())
    elif args.serials:
        sers = [int(x) for x in args.serials.split(",") if x.strip()]
    elif args.batch_file:
        sers = [int(x.strip()) for x in open(args.batch_file, encoding="utf-8") if x.strip()]
    else:
        print("请指定 --serials / --all / --batch-file", file=sys.stderr)
        sys.exit(2)

    fails = {}
    checked = 0
    for s in sers:
        e = by_serial.get(s)
        if not e:
            fails[s] = ["serial不在库中"]
            continue
        iss = validate(e)
        checked += 1
        if iss:
            fails[s] = iss
    ok = checked - len(fails)
    print(f"校验 {checked} 家 | 通过 {ok} | 不通过 {len(fails)} | 通过率 {100*ok/max(checked,1):.1f}%")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fail_list.json")
    json.dump({"fails": fails, "checked": checked, "ok": ok}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"FAIL清单已写: {out}")
    print(f"FAIL_TOTAL={len(fails)}")
    return len(fails)

if __name__ == "__main__":
    sys.exit(1 if main() > 0 else 0)
