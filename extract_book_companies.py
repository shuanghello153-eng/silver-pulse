"""
从《The AgeTech Revolution》216页全书中提取被重点描述的企业信息。
策略：
1. 提取全文，按页扫描所有大写开头的专有名词（候选企业名）
2. 统计每个候选名的出现频次
3. 对频次>=3的企业，提取其首次出现页和最后一次出现页之间的上下文
4. 从上下文中提取业务描述、商业模式等信息
"""

import pdfplumber
import json
import re
from collections import defaultdict, Counter

BOOK_PDF = r'G:\360MoveData\Users\shuan\Desktop\飞书-选题库-结构化整理\The AgeTech Revolution - Keren Etkin PDF.pdf'
OUTPUT = r'G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\book_deep_info.json'

# 已知的企业名列表（从Market Map提取的 + 常见AgeTech企业）
# 用于精确匹配而非模糊推断
KNOWN_COMPANIES = [
    # 从Market Map提取的企业名中选取高频/重要的
    "ElliQ", "Papa", "Intuition Robotics", "UpsideHom", "Apple", "AARP",
    "Elder", "Honor", "Home Instead", "Brightstar Care", "ComForCare",
    "Homewell", "Caresync", "CareLinx", "CareZone", "CarePredict",
    "CareMerge", "CarePilot", "CareVoyant", "CareCloud", "CareAware",
    "A Place For Mom", "APlaceForMom", "Caring.com", "Seniorly",
    "Silvernest", "Nesterly", "Room2Care", "Sharehaus", "Upside",
    "K4Connect", "Kisi", "Alarm.com", "SimpliSafe", "August Home",
    "Amazon Alexa", "Google Home", "Alexa", "Google Assistant",
    "Lively", "GreatCall", "Lively Mobile", "Snapfon", "Jitterbug",
    "Techboomers", "GetSetup", "OATS", "Senior Planet", "CyberSeniors",
    "Aging2.0", "Canopy", "Lifeline", "Life Alert", "Medical Guardian",
    "Bay Alarm Medical", "Rescue Alert", "Vive Health", "Drive Medical",
    "Hoveround", "Pride Mobility", "Golden Technologies", "Nova",
    "Bloom", "BrainCheck", "NeuroTrax", "Cognecity", "MyBrain",
    "Sage", "Sage Eldercare", "Sage Home Care",
    "Waldo", "Waldo Vision", "Vayyar", "Sensio", "Sensi",
    "Fujitsu", "Toshiba", "Panasonic", "Sharp", "NEC",
    "Paro", "Joy For All", "Hasbro", "Tombot", "Groove X",
    "MiRo", "Aeolus", "Luvozo", "Samu", "Stevie",
    "OhmniLabs", "Ohmni", "Diligent Robotics", "Moxi",
    "Bear Robotics", "Servi", "Pudu", "SoftBank",
    "Pepper", "Nao", "Robear", "Riba", "Matilda",
    "Zora", "Nao", "Teleadoc", "Teladoc", "Amwell",
    "Doctor On Demand", "MDLive", "PlushCare", "Lemonaid",
    "Hims", "Hers", "Ro", "Roman", "Keeps",
    "Headspace", "Calm", "Happify", "Mindstrong", "Talkspace",
    "BetterHelp", "Ginger", "Lyra", "Spring Health",
    "Lumosity", "Peak", "Elevate", "Fit Brains", "CogniFit",
    "BrainHQ", "Posit Science", "Dakim", "MyBrainTrainer",
    "Nest", "Nest Labs", "Ring", "Arlo", "Wyze",
    "Ecobee", "Honeywell Home", "Tado", "Emerson",
    "Philips", "Philips Lifeline", "Philips Healthcare",
    "Best Buy", "Great Call", "GreatCall", "Best Buy Health",
    "Livongo", "Omada", "Virta", "Noom", "MySugr",
    "Dexcom", "Abbott", "Libre", "Freestyle Libre",
    "Insulet", "Omnipod", "Tandem", "Medtronic",
    "Butterfly", "Butterfly Network", "Eko", "Eko Health",
    "Steth IO", "Clarius", "Heal", "Dispatch Health",
    "Home Hospital", "Medically Home", "Contessa",
    "DispatchHealth", "Heal", "Landing", "Friendship Ventures",
    "Silvergate", "SilverRide", "GoGo Grandparent", "Lyft",
    "Uber", "Uber Health", "Lyft Healthcare", "Via",
    "GoGo", "Envoy", "Joyride", "Circulation",
    "Scoop", "SilverRide", "ITN", "ITNAmerica",
    "Village to Village", "NORC", "Beacon Hill Village",
    "Capitol Hill Village", "Avalon", "Atria", "Brookdale",
    "Sunrise", "Senior Lifestyle", "Genesis", "Kindred",
    "Ensign", "Five Star", "New Senior", "Welltower",
    "Ventas", "Healthpeak", "HCP", "LTC Properties",
    "National Health Investors", "NHI", "Omega",
    "Civitas", "Civitas Capital", "Discovery", "Discovery Senior Living",
    "Solera", "Solera Senior Living", "Anthology", "Anthology Senior Living",
    "Kisco", "The Arbor Company", "Integral Senior Living",
    "Sagora", "Senior Lifestyle", "Civitas",
    "Memory Care", "Dementia Care", "Alzheimer's",
    "Aphasia", "Wernicke", "Broca",
    "Best Companies", "AARP", "AARP Foundation",
    "AARP Services", "AARP Innovation Lab", "AARP Tech",
    "Aetna", "UnitedHealth", "Humana", "Cigna", "Anthem",
    "CVS", "Walgreens", "Rite Aid", "Walmart",
    "CVS Health", "Optum", "UnitedHealth Group",
    "Blue Cross", "Blue Shield", "Kaiser",
    "Medicare", "Medicaid", "Social Security",
    "Veterans Affairs", "VA", "NIH", "NIA",
    "National Institute on Aging",
    "FDA", "FTC", "CMS",
    "WHO", "United Nations", "OECD",
]

def extract_all_text(pdf_path):
    """Extract text from all pages, return dict {page_num: text}"""
    pages = {}
    pdf = pdfplumber.open(pdf_path)
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            pages[i + 1] = text  # 1-indexed
    pdf.close()
    return pages


def find_company_mentions(pages_text):
    """
    Find all mentions of known companies in the text.
    Returns dict: {company_name: [(page_num, context_snippet), ...]}
    """
    mentions = defaultdict(list)
    
    for company in KNOWN_COMPANIES:
        # Use word boundary matching, case-sensitive for proper nouns
        # But also try case-insensitive for flexibility
        pattern = re.compile(r'\b' + re.escape(company) + r'\b', re.IGNORECASE)
        
        for page_num, text in pages_text.items():
            matches = list(pattern.finditer(text))
            if matches:
                for match in matches:
                    start = max(0, match.start() - 200)
                    end = min(len(text), match.end() + 200)
                    snippet = text[start:end].replace('\n', ' ')
                    mentions[company].append((page_num, snippet))
    
    return mentions


def extract_company_info(company, mentions):
    """
    Extract structured info from the mention contexts.
    """
    if not mentions:
        return None
    
    pages = [m[0] for m in mentions]
    contexts = [m[1] for m in mentions]
    
    # Combine all contexts for analysis
    full_context = ' '.join(contexts)
    
    # Try to extract business description from first few mentions
    # Look for patterns like "X is a..." or "X provides..." or "X helps..."
    desc_patterns = [
        rf'\b{re.escape(company)}\b\s+(?:is|was|are)\s+(?:a |an |the )?(.+?)(?:\.|,|;)',
        rf'\b{re.escape(company)}\b\s+(?:provides|offers|delivers|helps|enables|allows|creates|develops|builds|makes)\s+(.+?)(?:\.|,|;)',
        rf'\b{re.escape(company)}\b\s+(?:that|which)\s+(.+?)(?:\.|,|;)',
    ]
    
    description = ''
    for pattern in desc_patterns:
        match = re.search(pattern, full_context, re.IGNORECASE)
        if match:
            desc_candidate = match.group(1).strip()
            if len(desc_candidate) > 40:  # Only use if substantial enough
                description = desc_candidate
                break

    # Fallback: look for "X, a [company/organization/startup/platform/service] that/which"
    if not description:
        fallback_pattern = rf'\b{re.escape(company)}\b[^.]*?\b(?:company|organization|startup|platform|service|app|device|robot|startup|nonprofit|initiative)\b[^.]*'
        match = re.search(fallback_pattern, full_context, re.IGNORECASE)
        if match:
            desc_candidate = match.group(0).strip()
            if len(desc_candidate) > 40:
                description = desc_candidate[:500]

    # Another fallback: look for "created/founded/launched X" with mission/purpose
    if not description:
        mission_pattern = rf'(?:created|founded|launched|started)\s+{re.escape(company)}[^.]*?(?:mission|purpose|help|connect|provide|enable|allow)[^.]*'
        match = re.search(mission_pattern, full_context, re.IGNORECASE)
        if match:
            description = match.group(0).strip()[:500]
    
    # Extract potential funding info
    funding_patterns = [
        r'(?:raised|secured|received)\s+\$?([\d,.]+)\s*(?:million|billion|M|B)',
        r'(?:Series [A-F])\s+(?:funding|round|investment)',
        r'(?:valued at|valuation of)\s+\$?([\d,.]+)\s*(?:million|billion)',
        r'(?:acquired|acquisition|merger|merged)',
    ]
    
    funding = ''
    for pattern in funding_patterns:
        match = re.search(pattern, full_context, re.IGNORECASE)
        if match:
            funding = match.group(0)
            break
    
    # Extract founder info
    founder_pattern = rf'(?:founded by|created by|started by|launched by)\s+(.+?)(?:\.|,|;|in \d)'
    founder_match = re.search(founder_pattern, full_context, re.IGNORECASE)
    founder = founder_match.group(1).strip() if founder_match else ''
    
    # Extract founding year
    year_pattern = rf'(?:founded|launched|started|established|created)\s+(?:in\s+)?(\d{{4}})'
    year_match = re.search(year_pattern, full_context, re.IGNORECASE)
    founding_year = year_match.group(1) if year_match else ''
    
    # Extract country/location
    location_patterns = [
        r'(?:based in|headquartered in|HQ in|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:in|from)\s+(?:the\s+)?(US|USA|UK|Israel|Japan|China|Germany|France|Canada|Australia|Singapore|India|Korea|Netherlands|Sweden|Finland|Norway|Denmark)',
    ]
    location = ''
    for pattern in location_patterns:
        match = re.search(pattern, full_context, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            break
    
    return {
        'name': company,
        'mention_count': len(mentions),
        'first_page': min(pages),
        'last_page': max(pages),
        'description': description[:500] if description else '',
        'funding': funding,
        'founder': founder,
        'founding_year': founding_year,
        'location': location,
        'key_contexts': contexts[:3],  # Top 3 most informative contexts
    }


def main():
    print("Extracting text from book PDF...")
    pages_text = extract_all_text(BOOK_PDF)
    print(f"Extracted text from {len(pages_text)} pages")
    
    print("\nSearching for company mentions...")
    mentions = find_company_mentions(pages_text)
    
    # Non-company entities to exclude
    NON_COMPANIES = {'WHO', 'United Nations', 'OECD', 'Medicare', 'Medicaid',
                     'Social Security', 'Veterans Affairs', 'VA', 'NIH', 'NIA',
                     'National Institute on Aging', 'FDA', 'FTC', 'CMS',
                     'Blue Cross', 'Blue Shield', 'Kaiser'}
    
    # Filter out non-companies
    frequent_companies = {k: v for k, v in mentions.items()
                         if len(v) >= 3 and k not in NON_COMPANIES}
    print(f"Found {len(frequent_companies)} companies mentioned >= 3 times")
    
    # Extract structured info for each
    results = []
    for company, company_mentions in sorted(frequent_companies.items(), key=lambda x: -len(x[1])):
        info = extract_company_info(company, company_mentions)
        if info:
            results.append(info)
            print(f"  {company}: {info['mention_count']} mentions (p.{info['first_page']}-{info['last_page']})")
            if info['description']:
                print(f"    -> {info['description'][:100]}...")
    
    print(f"\nTotal companies with deep info: {len(results)}")
    
    # Save
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved to {OUTPUT}")
    
    return results


if __name__ == '__main__':
    main()
