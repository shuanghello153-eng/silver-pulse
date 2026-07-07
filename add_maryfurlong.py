# -*- coding: utf-8 -*-
"""Add Mary Furlong AgeTech directory companies to enterprise database.
Basic entries (name + description + category + source). Details to be filled later.
"""
import json
import os

DATA_FILE = "data/enterprise/all_enterprises.json"

# (name, category_l1, category_l2, description, website)
COMPANIES = [
    ("Accelera", "康复设备", "可穿戴康复", "先进可穿戴技术，改善本体感觉与神经可塑性，加速关节康复、平衡与步态控制。", "https://www.accelera.health/"),
    ("Amba", "养老服务", "护理自动化", "通过护理自动化减轻团队工作量，提供卓越护理并提升效率。", ""),
    ("Ping", "行业服务", "战略咨询", "对齐公司愿景与利益相关者，涉及战略、销售与产品开发。", ""),
    ("Clairvoyant Networks", "健康服务", "远程监测", "远程监测解决方案（Theora360云平台），利用AI最大化长者与慢性病患者的生活质量。", ""),
    ("GetSetUp", "老年文娱", "在线学习", "通过定制编程帮助长者学习新技能、连接他人、减少社会隔离。", "https://www.getsetup.io/"),
    ("Artifcts", "老年文娱", "遗产记录", "将物品与故事记忆关联，可整理、搜索、分享或私存的遗产记录平台。", "https://artifcts.com/"),
    ("ONSCREEN", "养老用品", "视频通信", "将电视变为视频通信平台，方便与年老亲人连接（$19.99/月）。", "https://onscreeninc.com/"),
    ("Embodied Labs", "健康服务", "VR培训", "开发虚拟现实沉浸式培训，让人从他人视角体会以提供更好护理。", "https://www.embodiedlabs.com/"),
    ("Discover Live", "老年文娱", "虚拟旅行", "自2017年起提供直播与点播虚拟旅行，减少孤独与记忆丧失。", "https://www.discover.live/"),
    ("MyHelloLine", "健康服务", "孤独干预", "孤独干预服务，增加社会连接，在隔离期成为生命线。", ""),
    ("SuperAging News", "行业服务", "营销媒体", "营销服务组织，结合数字出版与电商，触达长寿市场受众。", ""),
    ("JOY FOR ALL", "养老用品", "陪伴机器人", "交互式陪伴猫/狗，为长者带来舒适、陪伴与乐趣。", "https://joyforall.com/"),
    ("Phoenix Hipwear", "康复设备", "防跌倒", "柔软轻量髋关节保护服饰，防跌倒损伤。", ""),
    ("Brava", "健康食品", "智能烹饪", "用光技术烹饪，精准快速搞定三餐。", "https://www.brava.com/"),
]


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_names = {d.get("name", "").lower() for d in data}
    max_serial = max([int(d.get("serial", "#0000").lstrip("#")) for d in data if d.get("serial", "").startswith("#")], default=0)

    added = 0
    for i, (name, l1, l2, desc, web) in enumerate(COMPANIES):
        if name.lower() in existing_names:
            print(f"  Skip (exists): {name}")
            continue
        max_serial += 1
        entry = {
            "serial": f"#0{max_serial:03d}",
            "name": name,
            "region": "海外",
            "category_l1": l1,
            "category_l2": l2,
            "tags": [l2],
            "description": desc,
            "highlights": "",
            "funding_latest": {"amount": "未披露", "display": "未披露"},
            "funding_total": {"amount": "未披露", "display": "累计未披露"},
            "investors": "",
            "founded": "",
            "value_score": None,
            "source": "Mary Furlong企业库",
            "crunchbase_url": f"https://www.crunchbase.com/textsearch?q={name.replace(' ', '+')}",
            "website_url": web,
            "business_model": "",
        }
        data.append(entry)
        added += 1
        print(f"  Added: {name} ({l1}/{l2})")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nTotal enterprises: {len(data)} (added {added})")


if __name__ == "__main__":
    main()
