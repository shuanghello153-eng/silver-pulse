"""
Add new articles found via WebSearch to scored_latest.json.
These are articles that the RSS collector missed or that appeared after the last collection.
"""
import json
import os

SCORED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "scored_latest.json")

NEW_ARTICLES = [
    {
        "title": "Callie Care Raises $500K Pre-Seed to Tackle America's Senior Care Gap with Phone-First AI",
        "summary": "Callie Care, a Delaware-based AgeTech startup building a proactive phone-first voice AI that calls seniors daily to fight isolation and manage everyday needs, has raised $500,000 in pre-seed funding from angel investors alongside non-dilutive support from InterSystems Ventures. The funding will be used to scale user acquisition and build cognitive monitoring infrastructure.",
        "url": "https://aijourn.com/callie-care-raises-500k-pre-seed-to-tackle-americas-senior-care-gap-with-phone-first-ai/",
        "source": "The AI Journal",
        "date": "2026-07-06",
        "final_score": 7.5,
        "category": "high",
        "tags": ["智慧养老", "融资"],
        "recommendation": "电话优先的AI语音助手为美国老年人提供每日主动关怀呼叫，解决孤独和日常需求管理。对中国市场的参照：中国空巢老人问题同样严峻，语音AI（尤其是方言适配）可能是比App更自然的适老化交互方式，值得国内养老科技创业者关注。",
        "signal_score": 6.0,
    },
    {
        "title": "如身机器人完成亿元Pre-A轮融资，推动养老机器人规模化落地",
        "summary": "上海如身机器人科技有限公司宣布完成亿元Pre-A轮融资，由清松资本、润泽科技及平湖泽新共同投资。资金将用于加速具身智能在养老机构与居家场景中的落地部署。如身机器人从真实养老场景切入，通过通用具身机器人在真实环境中持续运行和学习。",
        "url": "https://finance.sina.com.cn/jjxw/2026-07-03/doc-inifntfe2365970.shtml",
        "source": "投资界",
        "date": "2026-07-03",
        "final_score": 8.5,
        "category": "high",
        "tags": ["养老用品", "融资"],
        "recommendation": "亿元级Pre-A轮融资在当前资本环境下非常罕见，清松资本（医疗基金）+润泽科技（算力上市公司）的投资组合说明具身智能+养老赛道的交叉点正在获得资本认可。如身机器人选择从养老机构B端切入而非C端，降低了落地难度，这个策略值得国内同类企业借鉴。",
        "signal_score": 8.0,
    },
    {
        "title": "烟台发布《养老产业高质量发展三年行动方案（2026-2028年）》",
        "summary": "烟台市政府发布养老产业三年行动方案，目标从'一床难求'到'一键享老'。方案涵盖养老服务体系建设、养老产业发展、医养结合等多个维度，推动养老产业高质量发展。",
        "url": "https://finance.sina.com.cn/wm/2026-07-03/doc-inifpkau5657769.shtml",
        "source": "新浪财经",
        "date": "2026-07-03",
        "final_score": 6.0,
        "category": "watch",
        "tags": ["养老服务", "政策法规"],
        "recommendation": "地方性养老产业政策持续加码，烟台方案从'一床难求'到'一键享老'的表述体现了从机构养老向智慧养老转型的政策导向。对选题的参照价值在于：多地出台类似方案意味着智慧养老SaaS、适老化改造、养老机器人等领域将迎来政策红利期。",
        "signal_score": 3.0,
    },
    {
        "title": "2026山西银发经济博览会将于7月17-19日在太原举办",
        "summary": "2026山西银发经济博览会以'银发康养 晋享未来'为主题，由山西省银发经济促进会、山西省老龄产业协会联合主办。展会总面积达3万平方米，规划9大特色展区，是中部地区规模领先的银发经济专业展会。",
        "url": "http://finance.sina.com.cn/wm/2026-06-17/doc-inictnup3763175.shtml",
        "source": "新浪财经",
        "date": "2026-06-17",
        "final_score": 4.0,
        "category": "archive",
        "tags": ["行业服务", "行业活动"],
        "recommendation": "区域性银发经济展会持续扩容，反映中部省份对银发经济的重视程度提升。但作为选题素材，价值较低，更多是行业动态参考。",
        "signal_score": 1.0,
    },
]

def main():
    # Load existing
    with open(SCORED_FILE, "r", encoding="utf-8") as f:
        existing = json.load(f)

    print(f"Existing articles: {len(existing)}")

    # Get existing URLs to avoid duplicates
    existing_urls = {a.get("url", "") for a in existing}

    # Add new articles
    added = 0
    for art in NEW_ARTICLES:
        if art["url"] not in existing_urls:
            existing.append(art)
            existing_urls.add(art["url"])
            added += 1
            print(f"  Added: [{art['category']}] {art['title'][:60]}")
        else:
            print(f"  Skipped (duplicate): {art['title'][:60]}")

    # Sort by date descending
    existing.sort(key=lambda a: a.get("date", ""), reverse=True)

    # Save
    with open(SCORED_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {added} new articles. Total: {len(existing)}")

    # Stats
    high = sum(1 for a in existing if a.get("category") == "high")
    watch = sum(1 for a in existing if a.get("category") == "watch")
    print(f"High value: {high}, Watch: {watch}")

if __name__ == "__main__":
    main()
