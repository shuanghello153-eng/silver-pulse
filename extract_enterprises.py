#!/usr/bin/env python
"""Extract structured enterprise data from 选题库.docx."""

import zipfile
import xml.etree.ElementTree as ET
import re
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "enterprise")
DOCX_PATH = r"G:/Google 微软下载/选题库.0712 (1).docx"

# ── Helpers ────────────────────────────────────────────────────

def extract_docx_text(path):
    """Extract all text paragraphs from a .docx file."""
    z = zipfile.ZipFile(path)
    xml_content = z.read("word/document.xml")
    tree = ET.fromstring(xml_content)
    paragraphs = []
    for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = []
        for t in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
            if t.text:
                texts.append(t.text)
        if texts:
            paragraphs.append("".join(texts))
    return "\n".join(paragraphs)


def parse_funding_amount(text):
    """Parse funding amount from text like '5500万美元' or '1.25亿美元'."""
    if not text:
        return None, "USD"

    text = text.strip().replace(",", "").replace(",", "")

    # 亿美元
    m = re.search(r"([\d.]+)\s*亿美元", text)
    if m:
        return float(m.group(1)) * 100000000, "USD"

    # 万美元
    m = re.search(r"([\d.]+)\s*万美元", text)
    if m:
        return float(m.group(1)) * 10000, "USD"

    # million dollars
    m = re.search(r"\$?([\d.]+)\s*million", text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1000000, "USD"

    # billion dollars
    m = re.search(r"\$?([\d.]+)\s*billion", text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1000000000, "USD"

    # $X M
    m = re.search(r"\$([\d.]+)\s*M", text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1000000, "USD"

    # $X B
    m = re.search(r"\$([\d.]+)\s*B", text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1000000000, "USD"

    # 万英镑/万欧元/亿韩币/千万人民币 etc.
    m = re.search(r"([\d.]+)\s*万英镑", text)
    if m:
        return float(m.group(1)) * 10000, "GBP"

    m = re.search(r"([\d.]+)\s*万欧元", text)
    if m:
        return float(m.group(1)) * 10000, "EUR"

    m = re.search(r"([\d.]+)\s*亿韩币", text)
    if m:
        return float(m.group(1)) * 100000000, "KRW"

    m = re.search(r"([\d.]+)\s*亿(?:人民币|元)", text)
    if m:
        return float(m.group(1)) * 100000000, "CNY"

    m = re.search(r"([\d.]+)\s*千万(?:人民币|元)", text)
    if m:
        return float(m.group(1)) * 10000000, "CNY"

    m = re.search(r"([\d.]+)\s*万(?:人民币|元)", text)
    if m:
        return float(m.group(1)) * 10000, "CNY"

    # Pure number with $
    m = re.search(r"\$([\d,.]+)", text)
    if m:
        val = float(m.group(1).replace(",", ""))
        return val, "USD"

    # 亿英镑
    m = re.search(r"([\d.]+)\s*亿英镑", text)
    if m:
        return float(m.group(1)) * 100000000, "GBP"

    # 亿欧元
    m = re.search(r"([\d.]+)\s*亿欧元", text)
    if m:
        return float(m.group(1)) * 100000000, "EUR"

    return None, "USD"


def parse_round(text):
    """Parse funding round from text."""
    if not text:
        return None

    text = text.strip()

    rounds = {
        "种子轮": "Seed",
        "Seed": "Seed",
        "种子": "Seed",
        "Pre-A": "Pre-A",
        "A轮": "Series A",
        "A+": "Series A+",
        "B轮": "Series B",
        "B": "Series B",
        "C轮": "Series C",
        "C": "Series C",
        "D轮": "Series D",
        "D": "Series D",
        "E轮": "Series E",
        "E": "Series E",
        "F轮": "Series F",
        "增长轮": "Growth",
        "IPO": "IPO",
        "上市": "IPO",
        "未知轮": "Unknown",
        "未知": "Unknown",
    }

    for cn, en in rounds.items():
        if cn in text:
            return en

    # Check for English round names
    m = re.search(r"Series\s+([A-Z])", text, re.IGNORECASE)
    if m:
        return f"Series {m.group(1).upper()}"

    return None


def parse_priority(text):
    """Parse priority level P0/P1/P2 from text."""
    if not text:
        return None

    m = re.search(r"P(\d)", text)
    if m:
        return f"P{m.group(1)}"

    if "废弃" in text or "不用看" in text or "不考虑" in text:
        return "废弃"

    if "已写" in text or "已写！" in text:
        return "已写"

    return None


# ── Enterprise extraction ───────────────────────────────────────

def extract_enterprises(text):
    """Extract structured enterprise data from the 选题库 text.

    Strategy: Scan line by line, detect enterprise blocks by looking for
    funding patterns and priority markers. Each enterprise block starts
    with the enterprise name and contains associated metadata.
    """

    lines = text.split("\n")
    enterprises = []

    # Category mapping from section headers
    current_category = "未分类"

    # Known category section markers
    category_markers = {
        "居家养老": "居家养老/护理服务",
        "护理服务提供商": "居家护理服务",
        "居家护理服务投融资盘点": "居家护理服务",
        "科技/创新/AI/App": "科技/AI/数字化",
        "更年期": "更年期健康",
        "认知症": "认知症/痴呆症",
        "社交陪伴孤独": "社交陪伴",
        "跌倒预防": "跌倒预防",
        "临终关怀": "临终关怀",
        "慢病管理": "慢病管理",
        "药物管理": "药物管理",
        "护理员支持": "护理员支持",
        "金融理财": "金融理财",
        "租房": "养老住房",
        "就业": "老年就业",
        "心理健康": "心理健康",
        "营养/特医食品": "营养/特医食品",
        "老年食品": "老年食品",
        "ToB科技赋能": "ToB科技赋能",
        "ToB居家护理服务商支持": "ToB护理科技",
        "ToB医疗保健提供商支持": "ToB医疗科技",
        "数字化工具/平台": "数字化工具/平台",
        "B2C内容→产品": "B2C内容→产品",
        "陪伴服务类": "陪伴服务",
        "疾病预测筛查": "疾病预测筛查",
        "健康管理": "健康管理",
        "SDOH": "健康社会决定因素",
        "收入周期管理": "收入周期管理",
        "远程营养": "远程营养",
        "无障碍旅游": "无障碍旅游",
    }

    # Build enterprise records from structured data patterns
    # Pattern 1: Lines that contain funding data (date + amount + round)
    funding_pattern = re.compile(
        r"(202\d\s*年\s*\d?\d\s*月|\d{4}\.\d{2}|\d{4}-\d{2})"
        r".*?"
        r"([\d.]+\s*(?:万|亿)?(?:美元|英镑|欧元|韩币|人民币|元))"
        r".*?"
        r"(种子轮|A轮|A\+|B轮|C轮|D轮|E轮|F轮|增长轮|IPO|上市|Seed|Series\s+[A-Z]|未知轮|未知)?",
        re.IGNORECASE
    )

    # Pattern 2: Enterprise name at start of a block (usually capitalized English name)
    enterprise_name_pattern = re.compile(
        r"^([A-Z][a-zA-Z\s&']+(?:Health|Care|Life|Home|Senior|Living|Innovation|Tech|AI|MD|Rx|app|Platform|Solutions|Services|Inc|LLC|Corp|Group)?"
        r"|[\u4e00-\u9fff]{2,10}(?:科技|健康|养老|护理|康养|食品|医药|陪诊|公寓|社区))",
        re.UNICODE
    )

    # Scan through the text looking for enterprise data
    # We'll do this by processing blocks of related lines
    current_ent = None
    ent_data = {}

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 3:
            continue

        # Check for category section headers
        for marker, category in category_markers.items():
            if marker in line_stripped and len(line_stripped) < 30:
                current_category = category
                break

        # Check for priority marker (P0, P1, P2)
        priority = parse_priority(line_stripped)

        # Check for funding pattern
        funding_match = funding_pattern.search(line_stripped)

        # Check for enterprise name
        name_match = enterprise_name_pattern.match(line_stripped)

        # Try to detect enterprise blocks
        # A new enterprise starts when we see:
        # 1. A line with an enterprise name at the start
        # 2. A line with a priority marker (P0/P1/P2)
        # 3. A line that starts with funding data attached to a known enterprise

        if priority and name_match:
            # This line has both a name and priority - likely start of enterprise block
            name = name_match.group(1).strip()
            if current_ent and ent_data:
                enterprises.append(ent_data)
            current_ent = name
            ent_data = {
                "name": name,
                "category": current_category,
                "priority": priority,
                "raw_text": [],
            }
            ent_data["raw_text"].append(line_stripped)
        elif name_match and len(line_stripped) > 5 and not line_stripped.startswith("点击"):
            name = name_match.group(1).strip()
            # Check if this looks like a standalone enterprise entry
            # (not just a reference within a paragraph)
            if len(line_stripped) < 80 or funding_match or priority:
                if current_ent and ent_data:
                    enterprises.append(ent_data)
                current_ent = name
                ent_data = {
                    "name": name,
                    "category": current_category,
                    "priority": priority,
                    "raw_text": [],
                }
                ent_data["raw_text"].append(line_stripped)
        elif current_ent and ent_data:
            ent_data["raw_text"].append(line_stripped)
            # Extract more data from continuation lines

    # Don't forget the last enterprise
    if current_ent and ent_data:
        enterprises.append(ent_data)

    # Now post-process each enterprise to extract structured fields
    result = []
    for ent in enterprises:
        raw = "\n".join(ent.get("raw_text", []))
        name = ent["name"]

        # Parse funding data
        amount, currency = parse_funding_amount(raw)
        round_val = parse_round(raw)
        priority = ent.get("priority") or parse_priority(raw)

        # Parse date
        date_match = re.search(r"(202\d)\s*年\s*(\d?\d)\s*月", raw)
        if date_match:
            date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}"
        else:
            date_match = re.search(r"(\d{4})\.\d{2}", raw)
            if date_match:
                date = date_match.group(1)
            else:
                date = None

        # Extract business summary (lines that contain "是" or "提供" or "专注于")
        summary_lines = []
        for l in ent.get("raw_text", []):
            if any(kw in l for kw in ["是一家", "是", "提供", "专注于", "致力于", "帮助", "开发", "创造"]):
                # Skip very short lines or lines that are just names
                if len(l) > 15 and name not in l[:10]:
                    summary_lines.append(l)
        summary = summary_lines[0] if summary_lines else None

        # Extract domestic coverage info
        coverage = None
        for l in ent.get("raw_text", []):
            if any(kw in l for kw in ["AgeClub", "微信", "国内", "竞品", "公众号", "文章", "流量", "阅读量", "阿沐"]):
                coverage = l
                break

        # Extract suggestion
        suggestion = None
        for l in ent.get("raw_text", []):
            if any(kw in l for kw in ["可以写", "选题建议", "建议", "值得写", "可以考虑", "已写", "不考虑", "不用看", "暂不考虑"]):
                suggestion = l
                break

        # Build record
        record = {
            "id": f"ent_{len(result) + 1:03d}",
            "name": name,
            "category": ent.get("category", "未分类"),
            "priority": priority,
            "funding": {
                "latest_date": date,
                "latest_amount": amount,
                "latest_amount_display": f"{amount/10000:.0f}万{currency}" if amount else None,
                "latest_round": round_val,
                "currency": currency,
            } if amount or date else None,
            "business_summary": summary,
            "domestic_coverage": coverage,
            "suggestion": suggestion,
            "source": "选题库.docx",
            "raw_text_preview": raw[:200],
        }
        result.append(record)

    # Also scan for enterprises mentioned in the "最新投融资" section
    # These tend to be more structured with clear date/amount/round/priority

    # Pattern for table-like rows: "EnterpriseName YYYY年M月 XM万/亿美元 X轮 P0/P1"
    table_pattern = re.compile(
        r"([A-Z][a-zA-Z\s&'.]+(?:Health|Care|Life|Home|Senior|Living|Innovation|Tech|AI|MD|Rx|App|Solutions|Services|Inc|LLC|Corp|Group|Health)?|[\u4e00-\u9fff]{2,8})"
        r"\s*"
        r"(202\d)\s*年\s*(\d?\d)\s*月\s*"
        r"([\d.]+)\s*(万|亿)?(美元|英镑|欧元|韩币|人民币|元)"
        r"\s*"
        r"(种子轮|A轮|A\+|B轮|C轮|D轮|E轮|F轮|增长轮|IPO|上市|Seed|未知)?"
        r"\s*"
        r"(P\d)?",
    )

    # Deduplicate by name
    seen_names = set()
    deduped = []
    for ent in result:
        name_lower = ent["name"].lower().strip()
        if name_lower not in seen_names:
            seen_names.add(name_lower)
            deduped.append(ent)

    return deduped


# ── Main ────────────────────────────────────────────────────────

def main():
    print("Extracting text from 选题库.docx...")
    text = extract_docx_text(DOCX_PATH)

    print(f"Text length: {len(text)} chars, {len(text.split(chr(10)))} lines")

    print("Extracting enterprise data...")
    enterprises = extract_enterprises(text)

    print(f"Extracted {len(enterprises)} enterprises")

    # Print summary
    from collections import Counter
    cats = Counter(e["category"] for e in enterprises)
    priorities = Counter(e.get("priority") for e in enterprises)

    print("\nCategory distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")

    print("\nPriority distribution:")
    for pri, count in priorities.most_common():
        print(f"  {pri}: {count}")

    # Count enterprises with funding data
    funded = sum(1 for e in enterprises if e.get("funding"))
    print(f"\nEnterprises with funding data: {funded}/{len(enterprises)}")

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, "enterprises_raw.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_path}")

    # Print first 5 for review
    print("\n=== First 5 enterprises ===")
    for e in enterprises[:5]:
        print(json.dumps(e, ensure_ascii=False, indent=1)[:300])
        print("---")


if __name__ == "__main__":
    main()
