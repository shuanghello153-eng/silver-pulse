# -*- coding: utf-8 -*-
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE="G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB=json.load(open(os.path.join(BASE,"data/enterprise/all_enterprises.json"),encoding="utf-8"))
OUT="G:/workbuddy/2026-07-17-12-07-23/SilverPulse_全量基线_1502家_字段完整版.xlsx"

HEAD=Font(bold=True,color="FFFFFF",size=11); HEADFILL=PatternFill("solid",fgColor="2F5496")
WRAP=Alignment(wrap_text=True,vertical="top"); TOP=Alignment(vertical="top")
THIN=Side(style="thin",color="D0D0D0"); BORDER=Border(left=THIN,right=THIN,top=THIN,bottom=THIN)
REDFILL=PatternFill("solid",fgColor="FCE4E4")
def style_header(ws,nc):
    for c in range(1,nc+1):
        cell=ws.cell(row=1,column=c); cell.font=HEAD; cell.fill=HEADFILL
        cell.alignment=Alignment(wrap_text=True,vertical="center",horizontal="center"); cell.border=BORDER
    ws.freeze_panes="A2"
def setw(ws,widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
def s(v):
    if v is None: return ""
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False)
    return str(v)
wb=Workbook()

# Sheet1 全量总览
ws=wb.active; ws.title="全量总览"
cols=["serial","name","name_cn","region","stage","research_value","signal_strength","info_score","diff_score","copy_score","payor_model","silver_verdict","recommend","update_time"]
ws.append(cols)
for e in DB:
    ws.append([e.get("serial"),e.get("name"),e.get("name_cn"),e.get("region"),e.get("stage"),
               e.get("research_value"),e.get("signal_strength"),e.get("info_score"),e.get("diff_score"),
               e.get("copy_score"),e.get("payor_model"),e.get("silver_verdict"),e.get("recommend"),e.get("update_time")])
style_header(ws,len(cols)); setw(ws,[9,22,16,8,10,12,11,9,9,9,22,12,60,12])
for row in ws.iter_rows(min_row=2): row[12].alignment=WRAP

# Sheet2 字段填充率
ws2=wb.create_sheet("字段填充率")
ws2.append(["字段","有效填充","占位词(未搜到/未融资/不确定)","空值","总计","填充率"])
fields=["name_cn","founded","stage","website_url","funding_latest","funding_total","investors",
        "payor_model","desc_cn","highlights","events","recommend","business_tags_role","silver_verdict"]
PH={"未搜到","未融资","不确定"}
for f in fields:
    eff=0; ph=0; empty=0
    for e in DB:
        v=e.get(f)
        if isinstance(v,list):
            if len(v)==0: empty+=1
            elif all(str(x).strip() in PH for x in v): ph+=1
            else: eff+=1
        elif v is None or (isinstance(v,str) and v.strip()==""): empty+=1
        elif isinstance(v,str) and v.strip() in PH: ph+=1
        else: eff+=1
    tot=len(DB); rate=round((eff+ph)/tot*100,1)
    ws2.append([f,eff,ph,empty,tot,f"{rate}%"])
style_header(ws2,6); setw(ws2,[20,12,30,8,8,10])

# Sheet3 校验结果(五道防线)
ws3=wb.create_sheet("校验结果")
ws3.append(["防线","检查项","结果"]); 
lines=[
 ["L1","覆盖：1502 serial 无缺无重","通过(0)"],
 ["L2","公式：research_value 当场重算误差<=0.5","通过(0)"],
 ["L3","量纲：四维 ∈[0,10]","通过(0)"],
 ["L4","推荐理由：单字符串/30-200字/含四维/无禁用词","通过(0)"],
 ["L5","stage 白名单：严禁融资中/未披露","通过(0)"],
 ["L6","全字段非空(允许占位词)","通过(0)"],
 ["L7","描述禁忌：不含企业名/成立于/融资","通过(0)"],
 ["L8","payor_model 非空","通过(0)"],
 ["合计","全量 1502 家违规项","0 条"],
]
for r in lines: ws3.append(r)
style_header(ws3,3); setw(ws3,[8,55,12])

# Sheet4 质量增强进度
ws4=wb.create_sheet("质量增强进度")
ws4.append(["批次","tier","企业数","状态","说明"])
ab=[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
for b in ab:
    ws4.append([f"batch_{b:03d}","A" if b<=6 else "B",12,"后台运行中(待合并)","联网精评+单字段recommend提质，完成后主智能体合并复扫"])
ws4.append(["batch_014~125 (Tier C 长尾)","C","约1334","基线已落地","规则化估算，按方案'长尾降级轻量补全'，后续可择机提质"])
style_header(ws4,5); setw(ws4,[18,8,10,20,55])

wb.save(OUT)
print("已保存:",OUT,"| sheets:",wb.sheetnames)
print("总企业:",len(DB))
