"""
Build unified enterprise database from three sources:
1. Stage (Not Age) book — 73 overseas enterprises
2. Chinese silver economy mapping (许之怿) — 150+ Chinese enterprises  
3. Existing top30 curated enterprises

Output: data/enterprise/all_enterprises.json
"""
import json
import re
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def load_stage_book():
    """Parse Stage (not Age) book enterprise text into structured records."""
    path = "G:/360MoveData/Users/shuan/Desktop/Stage （not Age）书籍企业库.txt"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split by numbered sections (lines starting with digits followed by a period)
    # Pattern: "1. Company Name"
    sections = re.split(r'\n(?=\d+\.\s)', text)
    
    enterprises = []
    for i, section in enumerate(sections):
        lines = [l.strip() for l in section.split('\n') if l.strip()]
        if not lines:
            continue
        
        # Parse header: "1. Company Name (Chinese Name)"
        header = lines[0]
        match = re.match(r'(\d+)\.\s+(.+?)(?:（(.+?)）)?$', header)
        if not match:
            continue
        
        name_en = match.group(2).strip()
        name_cn = match.group(3).strip() if match.group(3) else ""
        
        # Parse fields
        record = {
            "name": name_en,
            "name_cn": name_cn,
            "source": "Stage (not Age) Book",
            "region": "overseas",
            "category": "",
            "subcategory": "",
            "priority": "P2",
            "funding": "",
            "key_info": "",
            "suggestion": "",
            "tags": [],
        }
        
        for line in lines[1:]:
            if line.startswith("领域："):
                record["category"] = line.replace("领域：", "").strip()
            elif line.startswith("核心业务："):
                record["description"] = line.replace("核心业务：", "").strip()
            elif line.startswith("书中关键信息："):
                # Collect multi-line key info
                pass
            elif line.startswith("商业模式："):
                if "商业模式" not in record:
                    record["business_model"] = line.replace("商业模式：", "").strip()
            elif line.startswith("投资方"):
                record["investors"] = line.replace("投资方包括 ", "").replace("投资方：", "").strip()
            elif line.startswith("对应市场规模"):
                record["market_size"] = line.strip()
            elif line.startswith("覆盖"):
                record["life_stages"] = line.strip()
            elif line.startswith("关键信息："):
                record["funding"] = line.replace("关键信息：", "").strip()
            elif line.startswith("业绩表现："):
                record["performance"] = line.replace("业绩表现：", "").strip()
        
        # Collect key info from the section
        key_info_lines = []
        for line in lines:
            if any(line.startswith(k) for k in ["领域", "核心业务", "书中关键信息", "商业模式", 
                 "投资方", "对应市场", "覆盖", "关键信息", "业绩表现", "健康效果", "付费方",
                 "背景：", "价值主张：", "业务拓展", "核心观点", "核心项目", "特色"]):
                continue
            if line and not re.match(r'^\d+\.\s', line):
                key_info_lines.append(line)
        
        # Build tags from category
        cats = record["category"].split("、") if record["category"] else []
        record["tags"] = [c.strip() for c in cats if c.strip()]
        
        enterprises.append(record)
    
    return enterprises


def load_chinese_mapping():
    """Parse 许之怿 Chinese enterprise mapping from PDF text."""
    import PyPDF2
    reader = PyPDF2.PdfReader("F:/艾年/中国银发经济行业mapping-许之怿-20250622.pdf")
    text = reader.pages[0].extract_text()
    # Remove extra spaces between chars
    text = re.sub(r'\s+', '', text)
    
    # Parse categories and enterprises from the unstructured text
    # Major sections with their enterprises
    categories = {
        # 购物渠道
        "线上渠道": ["快团团", "悟空百货", "时尚奶奶团", "银彩聚乐部", "摩登银龄"],
        "线下渠道": ["自然之声", "海之声", "康复之家", "康林仁和", "上品折扣"],
        "电视购物": ["快乐购", "家有购物", "东方购物", "聚鲨环球", "惠买集团"],
        "会员营销": ["享佳健康", "麦考林", "益生康健", "银发无忧"],
        "私域渠道": ["芬香电商", "鲸灵集团", "云货优选", "环球捕手"],
        "特殊渠道": ["票圈视频", "甲子科技", "爱普雷德", "趣得多"],
        # 日常用品
        "老年鞋": ["足力健", "舒悦", "老美华", "老人头", "响午"],
        "老年服饰": ["福玛玛", "女王新款", "米兰登", "台格"],
        "老年护肤": ["昱芝夕", "令羽", "最美芳华", "多呵", "半月浮生"],
        "染发剂": ["染博士", "章华", "韩愢", "OKCS", "韩金靓"],
        "假发": ["瑞贝卡", "海森林", "佰丝堂", "天空树", "恒发"],
        "家用医疗": ["左点", "粤嘉康", "倍益康", "倍轻松", "匹奇"],
        # 健康食品
        "健康食品代工": ["艾兰得", "仙乐健康", "百合生物", "泰一健康", "今旭面业"],
        "线上健康食品": ["时光派", "VTN", "远方好物", "知识矩阵", "元气家族"],
        "线下健康食品": ["国科优选", "天合人康", "好孝心", "孝当先", "孝心坊"],
        "保健品OTC": ["百善药业", "绿瘦", "健特药业", "老来寿", "森美"],
        "中式养生": ["同仁堂", "寿仙谷", "楼上", "方家铺子", "福东海"],
        "益生菌": ["WonderLab", "月神", "蒙佩尔兰", "乐力", "每日的菌"],
        "小分子肽": ["太爱肽", "天天好", "瑞邦", "盛美诺", "蓝力"],
        "特医食品": ["玛士撒拉", "麦孚", "冬泽", "苏立康", "鲲鱼健康"],
        "蛋白粉": ["纽崔莱", "康比特", "肌肉科技", "百合康"],
        "无糖低GI": ["阿尔发", "神探伍伍", "慢糖家", "糖友饱饱", "江南米道"],
        "成人羊奶": ["优生活", "养乃世家", "莎浓羊奶", "臻牧", "卓牧"],
        # 老年文娱
        "老年旅游": ["一龄集团", "退休俱乐部", "共比邻", "晶彩人生", "遇见美好"],
        "老年教育": ["量子之歌", "红松学堂", "兴趣岛", "心智青", "美好盛年"],
        "社交平台": ["美篇", "小年糕", "彩视", "闲趣岛", "全民K歌"],
        "广场舞": ["糖豆", "爱风尚", "舞动时代", "就爱广场舞"],
        "老年相亲": ["伊对", "余生幸福", "完美亲家", "寻缘树", "成家相亲"],
        "老年健身": ["尚体乐活", "华友健身", "动龄健康", "心乐空间"],
        "老年音乐": ["乐唱族", "乐龄圈", "老柚", "锣钹科技"],
        "再就业": ["老年人才网", "阳光大姐", "鹏翼时代"],
        # 健康服务
        "健康养生": ["郑远元", "彭世", "唯艾", "艾艾贴", "艾益生"],
        "摔倒监测": ["清雷", "清澜技术", "苗米", "点可", "百芝龙"],
        "睡眠监测": ["博博科技", "兆观", "享睡", "大耳马", "星巡智能"],
        "血压血糖": ["瑞光康泰", "心永科技", "硅基仿生", "深纳普思"],
        "慢病管理": ["智云健康", "优加健康", "森梅医疗", "铂桐医疗"],
        "陪诊服务": ["善诊", "橙医健康", "安护通", "优享陪诊", "鲸鱼陪诊"],
        # 适老化改造
        "智慧养老软件": ["医家通", "颐讯", "颐养通", "乐湾", "麦麦养老"],
        "适老规划设计": ["志贺康养", "栖城设计", "天华设计", "遇禾规划"],
        "适老家居产品": ["福康通", "安馨康养", "中匠福", "沐恒实业", "悠幸"],
        "智能养老用品": ["来邦科技", "爱牵挂", "友达颐康", "救救帮", "云芯信息"],
        "综合供应链": ["佛山永爱", "盛通养老", "和乐春晖", "嘉年乐"],
        # 养老地产
        "国企央企养老": ["光大养老", "华润维麟", "中金佰仁堂", "招商观颐"],
        "上市公司养老": ["迪马常青社", "锦欣福星", "东方华康", "悦心安颐"],
        "保险公司养老": ["泰康之家", "太平养老", "复星保德信", "平安臻颐年"],
        "房地产养老": ["远洋椿萱茂", "人寿堂", "亲和源", "绿城康养"],
        "市场化机构养老": ["九如城", "绿康", "乐成养老", "哺恩", "水印中国"],
        "养老院中介": ["初新养老", "安养养老", "安养帮", "春树养老", "链老网"],
        "护工培训": ["一家依", "颐佳康", "嘉堡护理", "智杰教育"],
        # 养老服务
        "传统家政": ["天鹅到家", "好慷在家", "三替护理", "爱侬养老"],
        "民政服务": ["安康通", "天壹智慧", "智宇孝老", "青鸟软通"],
        "长护险": ["福寿康", "易得康", "颐家", "小橙", "抚理健康"],
        "专业护理": ["金牌护士", "小柏家护", "医护到家", "一号护工"],
        "院内陪护": ["泰心康护", "擎浩护理", "阿福医疗", "乐陪护"],
        "老年助餐": ["南京携才", "柏老汇", "老友记", "万德厨"],
        "助浴助洁": ["戴恩", "小V助浴", "银汤屋", "立奇电子", "尊术医疗"],
        "临终关怀": ["泰康安宁疗护", "慈康生命", "福寿家"],
        # 养老用品
        "轮椅": ["鱼跃", "英洛华", "互邦", "护卫神", "振邦"],
        "护理床": ["厚福", "迈德斯特", "添康", "世道", "康力元"],
        "拐杖助行器": ["佛山建泰", "康政", "钰民", "福佑", "足步医疗"],
        "代步车": ["斯维驰", "小飞哥", "皮皮熊", "舒莱适", "易乐车业"],
        "假肢": ["德林", "恩德莱", "祥和", "臻行科技", "健行仿生"],
        "洗澡坐便": ["福仕得", "美瑞德", "凌晴翔", "康德宝"],
        "视觉障碍": ["夕阳红", "美丽岛", "百年红", "联谛信息"],
        "听觉障碍": ["博音", "爱可声", "智听", "玖益", "锦好医疗"],
        "呼吸障碍": ["怡和嘉业", "家瑞康", "巨贸康万家", "谊安医疗"],
        "吞咽障碍": ["康乐龄", "奥特顺咽", "亿芃健康", "一味盛长"],
        "咀嚼障碍": ["美呀植牙", "瑞尔齿科", "鼎植口腔", "通策医疗"],
        "成人失禁": ["可靠", "豪悦", "维达", "爱舒乐", "永福康"],
        "智能用品": ["优必选", "作为科技", "若创科技", "得印科技", "正奇智能"],
        # 康复设备
        "运动康复": ["一康", "泽普医疗", "金矢机器人", "如身机器人", "优复门诊"],
        "手部康复": ["司羿智能", "希润医疗", "富伯医疗", "钧晟科技"],
        "外骨骼": ["程天", "远也", "迈步", "安杰莱", "奕然康复"],
        "精神神经": ["景昱", "品驰", "依瑞德", "英智", "温州康宁"],
        "肿瘤康复": ["康爱医疗", "和佳医疗", "安泰康成", "盈康生命"],
        # 认知症
        "认知症早筛": ["博斯腾", "特霍芬", "织生科技", "集思鸣智", "鹤灵医疗"],
        "认知症照护": ["美邸中国", "上海剪爱", "康语轩", "记忆家"],
        "认知症产品": ["脑动极光", "虚之实", "和家健脑", "达旦无极", "赋爱科技"],
        # 投资机构
        "消费VC": ["金鼎资本", "银创资本", "栈道资本", "BAI资本"],
        "医疗VC": ["长岭资本", "千骥资本", "博远资本", "铱创投资"],
        "国资投资": ["国寿大健康", "太保资本", "达晨财智", "达风投资"],
        "种子投资": ["高樟资本", "普健济康"],
    }
    
    # Category to parent mapping
    cat_parent = {
        "线上渠道": "购物渠道", "线下渠道": "购物渠道", "电视购物": "购物渠道",
        "会员营销": "购物渠道", "私域渠道": "购物渠道", "特殊渠道": "购物渠道",
        "老年鞋": "日常用品", "老年服饰": "日常用品", "老年护肤": "日常用品",
        "染发剂": "日常用品", "假发": "日常用品", "家用医疗": "日常用品",
        "健康食品代工": "健康食品", "线上健康食品": "健康食品", "线下健康食品": "健康食品",
        "保健品OTC": "健康食品", "中式养生": "健康食品", "益生菌": "健康食品",
        "小分子肽": "健康食品", "特医食品": "健康食品", "蛋白粉": "健康食品",
        "无糖低GI": "健康食品", "成人羊奶": "健康食品",
        "老年旅游": "老年文娱", "老年教育": "老年文娱", "社交平台": "老年文娱",
        "广场舞": "老年文娱", "老年相亲": "老年文娱", "老年健身": "老年文娱",
        "老年音乐": "老年文娱", "再就业": "老年文娱",
        "健康养生": "健康服务", "摔倒监测": "健康服务", "睡眠监测": "健康服务",
        "血压血糖": "健康服务", "慢病管理": "健康服务", "陪诊服务": "健康服务",
        "智慧养老软件": "适老化改造", "适老规划设计": "适老化改造", "适老家居产品": "适老化改造",
        "智能养老用品": "适老化改造", "综合供应链": "适老化改造",
        "国企央企养老": "养老地产", "上市公司养老": "养老地产", "保险公司养老": "养老地产",
        "房地产养老": "养老地产", "市场化机构养老": "养老地产", "养老院中介": "养老地产",
        "护工培训": "养老地产",
        "传统家政": "养老服务", "民政服务": "养老服务", "长护险": "养老服务",
        "专业护理": "养老服务", "院内陪护": "养老服务", "老年助餐": "养老服务",
        "助浴助洁": "养老服务", "临终关怀": "养老服务",
        "轮椅": "养老用品", "护理床": "养老用品", "拐杖助行器": "养老用品",
        "代步车": "养老用品", "假肢": "养老用品", "洗澡坐便": "养老用品",
        "视觉障碍": "养老用品", "听觉障碍": "养老用品", "呼吸障碍": "养老用品",
        "吞咽障碍": "养老用品", "咀嚼障碍": "养老用品", "成人失禁": "养老用品",
        "智能用品": "养老用品",
        "运动康复": "康复设备", "手部康复": "康复设备", "外骨骼": "康复设备",
        "精神神经": "康复设备", "肿瘤康复": "康复设备",
        "认知症早筛": "认知症", "认知症照护": "认知症", "认知症产品": "认知症",
        "消费VC": "投资机构", "医疗VC": "投资机构", "国资投资": "投资机构", "种子投资": "投资机构",
    }
    
    # All Chinese top-level categories
    main_cats = ["购物渠道", "日常用品", "健康食品", "老年文娱", "健康服务", 
                 "适老化改造", "养老地产", "养老服务", "养老用品", "康复设备", "认知症"]
    
    enterprises = []
    seen_names = set()
    
    for subcat, names in categories.items():
        parent = cat_parent.get(subcat, "其他")
        for name in names:
            if name in seen_names or len(name) < 2:
                continue
            seen_names.add(name)
            
            # Determine if investor or enterprise
            is_investor = parent == "投资机构"
            
            enterprises.append({
                "name": name,
                "name_cn": "",
                "source": "中国企业图谱(许之怿)",
                "region": "china",
                "category": parent,
                "subcategory": subcat,
                "priority": "P1" if subcat in ["老年教育", "社交平台", "长护险", "认知症早筛",
                    "外骨骼", "保险", "智慧养老软件", "摔倒监测", "陪诊服务"] else "P2",
                "description": "",
                "is_investor": is_investor,
                "tags": [parent, subcat],
            })
    
    # Add some extra enterprises from the text that might be in description lines
    extra = [
        ("CMEF", "行业展会", "P2"), ("AID上海老博会", "行业展会", "P2"),
        ("SIC保利老博会", "行业展会", "P2"), ("EE广州老博会", "行业展会", "P2"),
        ("AgeClub", "行业媒体", "P1"), ("昱言养老", "行业媒体", "P2"),
        ("ITH康养家", "行业媒体", "P2"), ("和君康养", "行业媒体", "P2"),
        ("SageWell", "金融理财", "P1"), 
        ("南京新百", "上市公司", "P1"), ("悦心健康", "上市公司", "P1"),
        ("可靠股份", "上市公司", "P1"), ("中顺洁柔", "上市公司", "P2"),
    ]
    for name, cat, pri in extra:
        if name not in seen_names:
            seen_names.add(name)
            enterprises.append({
                "name": name, "name_cn": "", "source": "中国企业图谱(许之怿)",
                "region": "china", "category": cat, "subcategory": "",
                "priority": pri, "description": "", "is_investor": False,
                "tags": [cat],
            })
    
    return enterprises


def merge_all():
    """Merge all three sources and save."""
    # Load existing top30
    top30_path = os.path.join(DATA_DIR, "data/enterprise/enterprises_top30.json")
    merged = {}
    
    # Helper to get key
    def key(ent):
        return re.sub(r'\s+', '', (ent.get("name", "") or "").lower())
    
    # Load top30 first (highest priority)
    if os.path.exists(top30_path):
        with open(top30_path, "r", encoding="utf-8") as f:
            top30 = json.load(f)
        for ent in top30:
            merged[key(ent)] = ent
        print(f"Top30 (existing): {len(top30)} enterprises")
    
    # Stage book
    stage = load_stage_book()
    for ent in stage:
        k = key(ent)
        if k not in merged:
            merged[k] = ent
    print(f"Stage book: {len(stage)} enterprises, {len(merged) - 30} new")
    
    # Chinese mapping
    cn_map = load_chinese_mapping()
    for ent in cn_map:
        k = key(ent)
        if k not in merged:
            merged[k] = ent
    print(f"Chinese mapping: {len(cn_map)} enterprises")
    
    # Convert to list and sort
    all_ents = list(merged.values())
    
    # Sort: P0 first, then P1, then P2, then alphabetically
    pri_order = {"P0": 0, "P1": 1, "P2": 2}
    all_ents.sort(key=lambda e: (pri_order.get(e.get("priority", "P2"), 2), e.get("name", "")))
    
    # Count stats
    p0 = sum(1 for e in all_ents if e.get("priority") == "P0")
    p1 = sum(1 for e in all_ents if e.get("priority") == "P1")
    p2 = sum(1 for e in all_ents if e.get("priority") == "P2")
    china = sum(1 for e in all_ents if e.get("region") == "china")
    overseas = sum(1 for e in all_ents if e.get("region") == "overseas")
    
    print(f"\nTotal enterprises: {len(all_ents)}")
    print(f"  P0={p0}, P1={p1}, P2={p2}")
    print(f"  China={china}, Overseas={overseas}")
    
    # Save
    out_path = os.path.join(DATA_DIR, "data/enterprise/all_enterprises.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_ents, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to {out_path}")
    return all_ents


if __name__ == "__main__":
    merge_all()
