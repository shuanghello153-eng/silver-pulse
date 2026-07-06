import json

# Load existing scored data
with open('data/scored_latest.json', 'r') as f:
    scored = json.load(f)

max_id = max(item.get('id', 0) for item in scored) if scored else 0

# New scored entries - unique high-value articles
new_entries = [
    {
        "title": "@在粤养老的香港长者！粤港养老通正式上线 津贴直达内地账户",
        "summary": "@在粤养老的香港长者！粤港养老通正式上线 津贴直达内地账户 广州日报新花城",
        "url": "https://news.google.com/rss/articles/CBMiigFBVV95cUxPeTN4Zm55Z29nN2dWNkNyeDVYd1oxdjF0TlN3aVA3Q3hBWkhPTV9ZMDR3YXFNWG9rQ0l5SzlOcEpJN1JnWmU2MkhDekRmSXI2bTRQQ0o1cGRlc041amk1cWJVY2pQeFN6REQ1M3dHR3FjcGJ2bU1lUjluekQ5ZlhOYWhreXNMbVMydHc?oc=5",
        "source": "广州日报新花城",
        "date": "2026-07-06",
        "final_score": 8.0,
        "category": "high",
        "tags": ["政策法规", "跨境养老", "支付通道"],
        "recommendation": "粤港养老通让香港长者津贴直达内地账户，跨境养老支付问题获得实质性突破。对中国市场参照：大湾区跨境养老是先行试验区，支付通道打通意味着香港长者在深圳/广州等地的消费能力将释放——养老服务供应商（陪诊、上门护理、社区食堂）将迎来增量客户。可做跨境养老支付元年选题。",
        "viral": False,
        "view": "curated",
        "region": "domestic",
        "id": max_id + 1
    },
    {
        "title": "GAO: Medicaid, Medicare Spent at Least $12B on Assisted Living But Affordability and Access Gaps Persist",
        "summary": "GAO首次披露联邦政府在辅助生活上的Medicaid/Medicare支出至少120亿美元，但可及性和可负担性差距仍然巨大。覆盖范围限制和地理差异导致老年人群获得服务不平等。",
        "url": "https://seniorhousingnews.com/2026/07/06/gao-medicaid-medicare-spent-at-least-12b-on-assisted-living-but-affordability-and-access-gaps-persist/",
        "source": "Senior Housing News",
        "date": "2026-07-06",
        "final_score": 7.5,
        "category": "high",
        "tags": ["政策法规", "辅助生活"],
        "recommendation": "GAO首次披露联邦政府在辅助生活上支出超120亿美元，但覆盖缺口巨大。对中国参照：120亿美元的隐性补贴揭示了辅助生活如何嵌入美国医保体系——不是单独的养老险，而是在现有Medicaid/Medicare框架内渗透。中国长护险在机构养老的支付设计上可参考这种嵌入式而非独立式的思路。",
        "viral": False,
        "view": "curated",
        "region": "overseas",
        "id": max_id + 2
    },
    {
        "title": "PPL Reaches Proposed $162M Settlement With NY CDPAP Caregivers",
        "summary": "PPL与纽约CDPAP护理员达成1.62亿美元和解协议，涉及工资盗窃问题。CDPAP（消费者主导个人援助计划）允许消费者自主选择护理员而非机构派单。",
        "url": "https://news.google.com/rss/articles/CBMikgFBVV95cUxQeHctcVh4enZfX3lrUkpCMDJxa29hQmI0cmY1emp6T3U0WFhjZFRxX191UG8tb0NGNjlhdUlHZE9yQTZ6ZGlZLU1lUTdEbkYyNUstenNSTFMxdkpfajZQYkQySmtLd2lKRWZfaG1zc0E3ZzRSWnVSZ1FzUVUtV29GY2NsMV9abkFIQ19nWWN1VTZuQQ?oc=5",
        "source": "Home Health Care News",
        "date": "2026-07-06",
        "final_score": 6.5,
        "category": "watch",
        "tags": ["居家养老", "护理人力", "政策法规"],
        "recommendation": "1.62亿美元和解——纽约CDPAP护理员工资盗窃案的集体和解金额惊人。对中国参照：中国养老护理员同样面临低薪和权益保障不足，但缺乏集体诉讼机制。CDPAP模式本身值得研究——让消费者自主选择护理员而非机构派单，中国居家养老雇佣制vs平台制的争议可借鉴。",
        "viral": False,
        "view": "curated",
        "region": "overseas",
        "id": max_id + 3
    },
    {
        "title": "How Benchmark, Onelife and McMillan Pazdan Smith Keep Old Buildings Alive With an Eye on Costs",
        "summary": "美国养老社区运营商Benchmark、Onelife和McMillan Pazdan Smith在旧楼改造中平衡效率提升与成本控制。改造重点不是外观翻新，而是让旧建筑更适合员工工作流程，从而降低长期运营成本。",
        "url": "https://seniorhousingnews.com/2026/07/06/how-benchmark-onelife-and-mcmillan-pazdan-smith-keep-old-buildings-alive-with-an-eye-on-costs/",
        "source": "Senior Housing News",
        "date": "2026-07-06",
        "final_score": 6.0,
        "category": "watch",
        "tags": ["养老地产", "运营效率"],
        "recommendation": "美国养老社区存量改造案例：改造重点不是外观翻新而是员工效率——让旧建筑适合护理工作流程。对中国参照：国内大量存量养老机构面临老旧设施拖垮运营问题，但改造思路普遍停留在翻新装修而非流程优化。美国经验提示：养老建筑的改造核心是让员工少跑路，而非让老人看新墙。",
        "viral": False,
        "view": "curated",
        "region": "overseas",
        "id": max_id + 4
    },
    {
        "title": "养老服务师职业资格明确",
        "summary": "工人日报报道养老服务师职业资格首次明确，标志着中国养老护理员从劳务向职业的制度化转型。",
        "url": "https://news.google.com/rss/articles/CBMibEFVX3lxTFBsS1hIYmdYUS0wODc4MXZvNGVxbERHMEkyNzhKYnljMGk0UWtqTFd3S0ZKQ2YyV0RiX3V3Rlc2WVBOMmYtSlhITlQyRUlVNTJleW1paUgyN2plV1hSTTd6OUUxMmNrc0Z2UW4zeg?oc=5",
        "source": "中工网",
        "date": "2026-07-04",
        "final_score": 6.5,
        "category": "watch",
        "tags": ["护理人力", "政策法规"],
        "recommendation": "养老服务师职业资格首次明确，标志着中国养老护理员从劳务向职业的制度化转型。对创业者参照：职业资格认证意味着准入门槛提升，同时也为优质护理员的薪酬议价提供了制度支撑。可与上海陪诊服务标准化政策（8.4分条目）对照——两者共同指向2026年是中国养老服务业标准化元年。",
        "viral": False,
        "view": "curated",
        "region": "domestic",
        "id": max_id + 5
    },
    {
        "title": "银发经济浪潮下，东软睿新的数智答卷与民生温度",
        "summary": "东软睿新定位银发经济数智化解决方案提供商，代表大厂系银发科技玩家的入场信号。",
        "url": "https://news.google.com/rss/articles/CBMibEFVX3lxTE52cW9YUk5ibTFyRDdyZVJzODNQZTF5ZEF3N2lWdzQyYXR5cERYRk1WRXUtUWlqQk9vV1VqME50ZU9vQW5aN1k0ZC1wOVBTcEFvRGNJcEs5dHhTQUc1NHc5YTZwWnM1OGhKa0c0SA?oc=5",
        "source": "中华网",
        "date": "2026-07-03",
        "final_score": 6.0,
        "category": "watch",
        "tags": ["智慧养老", "大厂入场"],
        "recommendation": "东软睿新定位银发数智化解决方案，代表大厂系银发科技玩家入场。对创业者参照：大厂入局意味着赛道天花板在升高，但也要警惕大厂做银发通常重技术轻场景的通病——东软的核心能力在医疗信息化，但银发场景的最后一公里不在系统里，在现场。",
        "viral": False,
        "view": "curated",
        "region": "domestic",
        "id": max_id + 6
    },
    {
        "title": "CMS proposes expanded authority to revoke Medicare privileges",
        "summary": "CMS提议扩大吊销Medicare资格的权限，反欺诈力度加大。追溯性吊销执照、扩展吊销理由等新规。",
        "url": "https://news.google.com/rss/articles/CBMivwFBVV95cUxNeGlQZmpuUmlIUFNYRUl5cTZFRXBGWFlKYTB4Y19TSkZsS1MzektleV1NQcEJwQTJpT2sxMFlWN1dnb2twOWZXWFFBdENLWWxOcDlkTncwbnB4QjVPYkNTY0VsTWtZY0lIdGU3Qk9XbFhlRldIbnFhREhkVUNwcWxEQjRFaUFlY0RtY0hzcV85NWw4NmdOcGZPcDBNVnpfeG9CTjVaVHFvNlIwbExWM0xxeTJHVTJKU0dINEJBa19xVQ?oc=5",
        "source": "TechTarget",
        "date": "2026-07-06",
        "final_score": 5.5,
        "category": "watch",
        "tags": ["政策法规", "居家养老"],
        "recommendation": "CMS扩大吊销Medicare资格权限，与此前2.4%支付增加政策配套——给钱+管钱双轨推进。中国长护险反欺诈机制建设滞后，美国经验提示：支付体系不能只设计怎么给，还要设计怎么查。",
        "viral": False,
        "view": "curated",
        "region": "overseas",
        "id": max_id + 7
    },
    {
        "title": "闲置楼宇变身康养热土 韶关乐昌聚力打造银发经济新标杆",
        "summary": "韶关乐昌闲置楼宇改造为康养设施，探索中国养老地产轻资产路径。",
        "url": "https://news.google.com/rss/articles/CBMiigFBVV95cUxOM3BtaDRJbjJ2QUluaVJ2R3ZHMU9UcnRpeURVYm9hY0hiNDZYcEdHdlNqaU5ybjFVMkpGM3hmdGxFQ0tuV1M2UHpfVWJ2Y2Zhd0NlNUxSblpYdG9CSWNxTXNKZ095cjFSWWRMR25jNEYwQldSNDJvUl81YnMxbVZ1bUVVLWx2Q1UwSnc?oc=5",
        "source": "广州日报新花城",
        "date": "2026-07-03",
        "final_score": 5.0,
        "category": "archive",
        "tags": ["养老地产"],
        "recommendation": "闲置楼宇改造为康养设施——轻资产路径探索。韶关乐昌案例偏地方叙事，但闲置资产活化+养老的思路对国内大量空置商业物业有启发。归档备用，积累5-10个类似案例后合并分析。",
        "viral": False,
        "view": "curated",
        "region": "domestic",
        "id": max_id + 8
    }
]

scored.extend(new_entries)

print(f"Total scored articles after append: {len(scored)}")
print(f"New entries added: {len(new_entries)}")
print(f"High value: {sum(1 for e in new_entries if e['category'] == 'high')}")
print(f"Watch: {sum(1 for e in new_entries if e['category'] == 'watch')}")
print(f"Archive: {sum(1 for e in new_entries if e['category'] == 'archive')}")

with open('data/scored_latest.json', 'w') as f:
    json.dump(scored, f, indent=2, ensure_ascii=False)
print("scored_latest.json updated successfully")
