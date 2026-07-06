#!/usr/bin/env python3
"""
add_business_model.py — 为所有企业添加 business_model 字段
基于 description, category_l1, category_l2, tags, name 等已有信息自动生成。

商业模式特点推断规则：
- 基于一级分类和二级分类推断主要商业模式
- 基于description中的关键词补充
- 基于已有funding信息推断阶段
- 简短1句话描述
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "enterprise")

# 商业模式映射表：基于一级分类
L1_BIZ_MODEL = {
    "健康服务": "B2B/B2C 健康服务",
    "适老化改造": "B2B/B2C 适老化改造",
    "老年文娱": "B2C 休闲文娱",
    "智慧养老": "B2B/B2G 智慧养老解决方案",
    "养老服务": "B2C/B2B 养老运营服务",
    "老年用品": "B2C 老年消费品",
    "适老金融": "B2C 金融理财服务",
    "养老地产": "B2C/B2B 养老社区运营",
    "老年教育": "B2C 教育培训",
    "养老科技": "B2B 科技产品/服务",
    "老年出行": "B2C 旅游出行服务",
    "人才与就业": "B2B 人才培训/输送",
    "行业服务": "B2B 行业服务/媒体",
}

# 更细分的映射：基于二级分类
L2_BIZ_MODEL = {
    "行业媒体": "B2B 行业媒体/数据服务",
    "金融理财": "B2C 老年金融理财",
    "适老家居产品": "B2C 适老化家居产品",
    "健康养生": "B2C 健康养生服务",
    "社交平台": "B2C 社交娱乐平台",
    "医疗护理": "B2B/B2C 医疗护理服务",
    "康复辅具": "B2C 康复辅具器械",
    "智慧养老平台": "B2B/B2G 智慧养老SaaS平台",
    "养老机构": "B2C 养老机构运营",
    "居家养老": "B2C/B2B 居家养老服务",
    "健康管理": "B2C/B2B 健康管理服务",
    "老年食品": "B2C 老年食品",
    "老年服饰": "B2C 老年服饰",
    "养老社区": "B2C 养老社区开发运营",
    "老年旅游": "B2C 老年旅游服务",
    "教育培训": "B2C 老年教育培训",
    "科技产品": "B2B 科技产品研发",
    "人才培训": "B2B 人才培训输出",
    "护理服务": "B2C/B2B 护理服务",
    "临终关怀": "B2C/B2B 临终关怀服务",
    "老年痴呆": "B2C 认知症专业照护",
    "社区服务": "B2C 社区养老服务",
    "医疗器械": "B2B 医疗器械研发",
    "信息化平台": "B2B 信息化平台服务",
    "远程医疗": "B2B/B2C 远程医疗服务",
    "可穿戴设备": "B2C 智能可穿戴设备",
    "智能家居": "B2B/B2C 智能家居解决方案",
    "机器人": "B2B/B2C 服务机器人",
    "药物研发": "B2B 药物研发",
    "保险服务": "B2C 老年保险服务",
    "宠物陪伴": "B2C 宠物陪伴服务",
    "出行服务": "B2C 老年出行服务",
    "社交娱乐": "B2C 社交娱乐",
    "文化娱乐": "B2C 文化娱乐",
    "心理咨询": "B2C 心理咨询服务",
    "法律咨询": "B2C 法律咨询服务",
    "遗产规划": "B2C 遗产规划服务",
    "反诈防骗": "B2C 反诈防骗服务",
    "消费平台": "B2C 老年消费平台",
}

# 基于description关键词的补充（优先级从高到低）
DESC_KEYWORD_PATTERNS = [
    # 保险/医保优先级最高
    (r"(medicare|medicaid|保险|health plan|健康保险|保险服务)", "B2C/B2B 老年健康保险"),
    (r"(上市|IPO|纳斯达克|NYSE|港交所|A股)", "上市企业"),
    (r"(therapeutic|neuroscience|pharma|biotech|drug|制药|药物)", "B2B 制药/生物科技"),
    (r"(medical device|医疗器械|器械|diagnostic)", "B2B 医疗器械"),
    (r"(SaaS|SaaS平台|软件即服务|platform service|software)", "B2B SaaS/软件平台"),
    (r"(robot|机器人|robotics)", "B2B/B2C 服务机器人"),
    (r"(wearable|可穿戴|智能穿戴|手环|sensor|传感器)", "B2C 智能可穿戴设备"),
    (r"(telehealth|telemedicine|远程医疗|远程健康)", "B2B/B2C 远程医疗"),
    (r"(电商|在线商城|电商平台|marketplace)", "B2C 电商平台"),
    (r"(加盟|连锁|franchise)", "B2C/B2B 加盟连锁"),
    (r"(政府|民政|公办|government)", "B2G 政企合作"),
    (r"(社区|居家|community|home care)", "B2C/B2B 社区/居家服务"),
    (r"(nutri|food|supplement|beverage|食品|营养|保健品)", "B2C 老年健康食品"),
    (r"(media|媒体|资讯|content|news|publication)", "B2B 行业媒体/数据服务"),
    (r"(consult|咨询|顾问|advisory)", "B2B 咨询服务"),
    (r"(education|培训|教育|course|learning)", "B2C 教育/培训"),
    (r"(data|大数据|AI|人工智能|machine learning)", "B2B AI/数据驱动"),
    (r"(fitness|健身|wellness|运动)", "B2C 老年健身/健康"),
    (r"(transportation|出行|travel|旅游|mobility)", "B2C 老年出行服务"),
    (r"(housing|community|养老社区|assisted living|nursing home|senior living|retirement)", "B2C/B2B 养老社区运营"),
    (r"(care|护理|照护|caregiver|nursing)", "B2C/B2B 养老护理服务"),
    (r"(hardware|硬件|设备|device|product)", "B2B/B2C 硬件产品"),
    (r"(operation|运营|运营管理|运营服务|operator)", "B2C/B2B 养老运营服务"),
    (r"(R&D|研发|技术|科技|technology|tech)", "B2B 科技研发"),
]


def infer_business_model(ent):
    """Infer a 1-sentence business_model from existing fields.
    Priority: description keywords > L2 category > L1 category > tags > fallback."""
    l1 = ent.get("category_l1", "")
    l2 = ent.get("category_l2", "")
    desc = ent.get("description", "")
    name = ent.get("name", "")
    tags = ent.get("tags", [])

    # Priority 1: Try keyword patterns from description FIRST
    # This handles cases where L1/L2 is incorrectly categorized (common for overseas companies)
    keyword_match = None
    for pattern, label in DESC_KEYWORD_PATTERNS:
        if re.search(pattern, desc, re.IGNORECASE):
            keyword_match = label
            break

    # Start with L2-based model if available, else L1
    l2_model = L2_BIZ_MODEL.get(l2, "")
    l1_model = L1_BIZ_MODEL.get(l1, "")

    # Determine final model
    if keyword_match:
        # Description keyword takes priority
        model = keyword_match
        # If L1 suggests it's a media company but keyword says otherwise, use keyword
        # Special: if L1 is 行业服务 but desc has insurance/medical/etc, use keyword
    elif l2_model:
        model = l2_model
    elif l1_model:
        model = l1_model
    else:
        model = ""

    # Check for "上市" status and append it
    if re.search(r"(上市|IPO|纳斯达克|NYSE|港交所|A股)", desc, re.IGNORECASE):
        if "上市" not in model:
            model = f"{model}（上市企业）"

    # Fallback: if no model determined, use generic
    if not model:
        # Try tags
        for tag in tags:
            tag_str = tag if isinstance(tag, str) else ""
            tag_lower = tag_str.lower()
            if "saas" in tag_lower or "平台" in tag_str:
                model = "B2B 平台服务"
                break
            elif "硬件" in tag_str or "设备" in tag_str or "产品" in tag_str:
                model = "硬件产品"
                break
            elif "服务" in tag_str:
                model = "服务提供商"
                break
        if not model:
            model = "银发经济企业"

    return model


def main():
    path = os.path.join(DATA_DIR, "all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    total = len(enterprises)
    added = 0
    updated = 0

    for ent in enterprises:
        # Always regenerate (clear existing first)
        ent["business_model"] = infer_business_model(ent)
        added += 1

    # Write back
    with open(path, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"Total enterprises: {total}")
    print(f"Business model added: {added}")
    print(f"Already had model: {updated}")

    # Print sample
    print("\n--- Sample (first 5) ---")
    for ent in enterprises[:5]:
        print(f"  {ent['name']}: {ent.get('business_model', 'N/A')}")

    print("\n--- Sample (last 5) ---")
    for ent in enterprises[-5:]:
        print(f"  {ent['name']}: {ent.get('business_model', 'N/A')}")

    # Stats by L1
    print("\n--- Stats by L1 ---")
    l1_stats = {}
    for ent in enterprises:
        l1 = ent.get("category_l1", "N/A")
        bm = ent.get("business_model", "")
        if l1 not in l1_stats:
            l1_stats[l1] = {}
        if bm not in l1_stats[l1]:
            l1_stats[l1][bm] = 0
        l1_stats[l1][bm] += 1
    for l1, models in sorted(l1_stats.items()):
        print(f"  {l1}:")
        for bm, cnt in sorted(models.items(), key=lambda x: -x[1])[:3]:
            print(f"    {bm}: {cnt}")


if __name__ == "__main__":
    main()
