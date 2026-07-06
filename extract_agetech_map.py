"""
Extract company list from 2025 AgeTech Market Map PDF.
- Extract 332 hyperlinks -> dedup -> ~325 companies
- Infer company names from URL domains
- Infer category by spatial matching between company coordinates and category label coordinates
- Output: data/enterprise/agetech_map_raw.json
"""
import pdfplumber
import json
import re
import os
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "enterprise")
PDF_PATH = "G:/360MoveData/Users/shuan/Desktop/飞书-选题库-结构化整理/2025-AgeTech-Market-Map-Final-Nov（The AgeTech Revolution）.pdf"

# === Category label coordinates (extracted from PDF text) ===
# Format: (label_text, x, y, width, height)
# These define category regions on the map
CATEGORY_REGIONS = [
    # Top section: Health Wellness For Senior Living
    {"label": "RPM", "x": 89, "y": 19, "region": "Health & Wellness For Senior Living", "subcat": "RPM"},
    {"label": "Resident Engagement", "x": 449, "y": 21, "region": "Health & Wellness For Senior Living", "subcat": "Resident Engagement"},
    {"label": "Smart Home", "x": 263, "y": 38, "region": "Health & Wellness For Senior Living", "subcat": "Smart Home"},
    {"label": "Rehabilitation", "x": 71, "y": 51, "region": "Health & Wellness For Senior Living", "subcat": "Rehabilitation"},
    {"label": "PERS", "x": 86, "y": 94, "region": "Health & Wellness For Senior Living", "subcat": "PERS"},
    {"label": "Wearables", "x": 271, "y": 111, "region": "Health & Wellness For Senior Living", "subcat": "Wearables"},
    {"label": "Operations", "x": 468, "y": 119, "region": "Health & Wellness For Senior Living", "subcat": "Operations"},
    {"label": "Medication Management", "x": 43, "y": 127, "region": "Health & Wellness For Senior Living", "subcat": "Medication Management"},

    # Fall Prevention & Detection
    {"label": "Fall Prevention & Detection", "x": 238, "y": 168, "region": "Fall Prevention & Detection", "subcat": "Fall Prevention & Detection"},

    # Retirement 2.0
    {"label": "Retirement 2.0", "x": 59, "y": 179, "region": "Retirement 2.0", "subcat": "Retirement 2.0"},

    # Fitness / Wellness / Monitoring
    {"label": "Fitness Wellness Monitoring", "x": 282, "y": 219, "region": "Fitness Wellness Monitoring", "subcat": "Fitness Wellness Monitoring"},

    # Insurtech
    {"label": "Insurtech", "x": 73, "y": 226, "region": "Insurtech", "subcat": "Insurtech"},

    # Independence section
    {"label": "Everyday assistance", "x": 23, "y": 273, "region": "Independence", "subcat": "Everyday assistance"},
    {"label": "Tech training", "x": 133, "y": 273, "region": "Independence", "subcat": "Tech training"},
    {"label": "Finance", "x": 281, "y": 279, "region": "Independence", "subcat": "Finance"},
    {"label": "Transportation", "x": 401, "y": 275, "region": "Independence", "subcat": "Transportation"},
    {"label": "Assistive Tech", "x": 499, "y": 276, "region": "Independence", "subcat": "Assistive Tech"},

    # Scam & fraud protection
    {"label": "Scam & fraud protection", "x": 243, "y": 328, "region": "Independence", "subcat": "Scam & fraud protection"},

    # Cognitive Care
    {"label": "Cognitive Care", "x": 65, "y": 382, "region": "Cognitive Care", "subcat": "Cognitive Care"},

    # For Caregivers
    {"label": "For Caregivers", "x": 452, "y": 383, "region": "For Caregivers", "subcat": "For Caregivers"},

    # Companionship & Communication
    {"label": "Companionship & Communication", "x": 56, "y": 504, "region": "Companionship & Communication", "subcat": "Companionship & Communication"},

    # For Home Care Providers
    {"label": "Tech-Enabled Home Care", "x": 55, "y": 764, "region": "For Home Care Providers", "subcat": "Tech-Enabled Home Care"},

    # For Healthcare Providers
    {"label": "For Healthcare Providers", "x": 84, "y": 651, "region": "For Healthcare Providers", "subcat": "For Healthcare Providers"},

    # Housing
    {"label": "Housing", "x": 330, "y": 652, "region": "Housing", "subcat": "Housing"},

    # End of Life Planning
    {"label": "End of Life Planning", "x": 448, "y": 651, "region": "End of Life Planning", "subcat": "End of Life Planning"},

    # Legacy / For Adult Day
    {"label": "Legacy For Adult Day", "x": 277, "y": 765, "region": "Legacy / For Adult Day", "subcat": "Legacy / For Adult Day"},
]

# === Map Market Map categories to existing 12-category system ===
CATEGORY_MAPPING = {
    "RPM": "智慧养老/AI/数字疗法",
    "Resident Engagement": "智慧养老/AI/数字疗法",
    "Smart Home": "智慧养老/AI/数字疗法",
    "Rehabilitation": "康复设备",
    "PERS": "智慧养老/AI/数字疗法",
    "Wearables": "智慧养老/AI/数字疗法",
    "Operations": "智慧养老/AI/数字疗法",
    "Medication Management": "健康服务/医疗",
    "Fall Prevention & Detection": "康复设备",
    "Retirement 2.0": "养老地产/居住",
    "Fitness Wellness Monitoring": "健康服务/医疗",
    "Insurtech": "保险科技/金融",
    "Everyday assistance": "养老用品",
    "Tech training": "养老用品",
    "Finance": "保险科技/金融",
    "Transportation": "养老用品",
    "Assistive Tech": "养老用品",
    "Scam & fraud protection": "保险科技/金融",
    "Cognitive Care": "认知症",
    "For Caregivers": "养老服务/护理",
    "Companionship & Communication": "老年文娱/社交",
    "Tech-Enabled Home Care": "养老服务/护理",
    "For Healthcare Providers": "健康服务/医疗",
    "Housing": "养老地产/居住",
    "End of Life Planning": "健康服务/医疗",
    "Legacy / For Adult Day": "老年文娱/社交",
}

# === Known company name corrections (URL domain -> proper name) ===
NAME_CORRECTIONS = {
    "papa": "Papa",
    "joinhonor": "Honor",
    "intuitionrobotics": "Intuition Robotics",
    "carepredict": "CarePredict",
    "naborforce": "Naborforce",
    "medisafe": "Medisafe",
    "lifealert": "Life Alert",
    "gogograndparent": "GoGoGrandparent",
    "grandpad": "GrandPad",
    "rendever": "Rendever",
    "wellthy": "Wellthy",
    "homethrive": "Homethrive",
    "cariloop": "Cariloop",
    "ianacare": "Ianacare",
    "careforth": "Careforth",
    "getduos": "Duos",
    "empathy": "Empathy",
    "braincheck": "BrainCheck",
    "neurotrack": "Neurotrack",
    "silverride": "SilverRide",
    "alayacare": "AlayaCare",
    "birdie": "Birdie",
    "careacademy": "CareAcademy",
    "clearcareonline": "ClearCare",
    "grandcare": "GrandCare",
    "embodiedlabs": "Embodied Labs",
    "homage": "Homage",
    "carelinx": "CareLinx",
    "careship": "Careship",
    "ceracare": "CeraCare",
    "tombot": "Tombot",
    "joyforall": "Joy For All",
    "unipercare": "Uniper Care",
    "k4connect": "K4Connect",
    "cubigo": "Cubigo",
    "aivahealth": "Aiva Health",
    "hellosage": "Hello Sage",
    "inspiren": "Inspiren",
    "augusthealth": "August Health",
    "butlr": "Butlr",
    "sensi": "Sensi",
    "farewill": "Farewill",
    "everplans": "Everplans",
    "freewill": "FreeWill",
    "trustandwill": "Trust & Will",
    "willful": "Willful",
    "mygoodtrust": "GoodTrust",
    "clearestate": "ClearEstate",
    "kodahealthcare": "Koda Health",
    "mywishes": "MyWishes",
    "lifeafterme": "LifeAfterMe",
    "boldin": "Boldin",
    "retirable": "Retirable",
    "truelinkfinancial": "True Link Financial",
    "getcarefull": "Carefull",
    "silvur": "Silvur",
    "savvly": "Savvly",
    "genwise": "GenWise",
    "getsetup": "GetSetUp",
    "eldera": "Eldera",
    "wisdomcircle": "WisdomCircle",
    "seniorsatwork": "SeniorsAtWork",
    "maturious": "Maturious",
    "discover": "Discover Live",
    "wowzitude": "Wowzitude",
    "tango": "Tango",
    "localposh": "LocalPosh",
    "chor-us": "Chorus",
    "vivavalet": "Viva Valet",
    "asksamie": "AskSamie",
    "netassist": "NetAssist",
    "gocaremates": "GoCareMates",
    "seniorthrive": "SeniorThrive",
    "clearcaptions": "ClearCaptions",
    "captioncall": "CaptionCall",
    "listenlively": "Listen Lively",
    "nuheara": "Nuheara",
    "steadiwear": "Steadiwear",
    "silverride": "SilverRide",
    "onwardrides": "Onward Rides",
    "motitech": "Motive",
    "connectamerica": "Connect America",
    "alert-1": "Alert-1",
    "moviwear": "Moviwear",
    "careband": "CareBand",
    "unaliwear": "UnaliWear",
    "theoracare": "TheoraCare",
    "wherible": "Wherible",
    "umps": "UMPS",
    "vitalerter": "Vitalerter",
    "vitaltech": "VitalTech",
    "virtusense": "VirtuSense",
    "sensara": "Sensara",
    "dinacare": "DinaCare",
    "endearhealth": "Endear Health",
    "pearsuite": "PearSuite",
    "healthhive": "HealthHive",
    "ableinnovations": "Able Innovations",
    "exer": "Exer",
    "unlimited-robotics": "Unlimited Robotics",
    "tellapp": "Tell",
    "memorywell": "MemoryWell",
    "seniorly": "Seniorly",
    "nesterly": "Nesterly",
    "kuvu": "Kuvu",
    "joinupside": "JoinUpside",
    "myndyou": "MyndYou",
    "myndimmersive": "MyndImmersive",
    "silverfit": "SilverFit",
    "personcentredsoftware": "Person Centred Software",
    "odessaconnect": "OdessaConnect",
    "sentrics": "Sentrics",
    "yeticare": "YetiCare",
    "obieforseniors": "Obie",
    "connectcarehero": "ConnectCareHero",
    "welbi": "Welbi",
    "silvradventures": "SilvrAdventures",
    "goodlifesorted": "GoodLife Sorted",
    "meetcaregivers": "MeetCaregivers",
    "tuktu": "Tuktu",
    "neurorehabvr": "NeuroRehabVR",
    "kinumi": "Kinumi",
    "caspar": "Caspar",
    "nevisq": "NevisQ",
    "allycares": "Ally Cares",
    "assuredallies": "Assured Allies",
    "evondos": "Evondos",
    "tommedications": "Tom Medications",
    "mon4t": "Mon4t",
    "omcare": "Omcare",
    "qumea": "Qumea",
    "binah": "Binah",
    "wizecare": "WizeCare",
    "xr": "XR Health",
    "nuviomobility": "NuvoMobility",
    "restoreskills": "RestoreSkills",
    "fallcall": "FallCall",
    "livindi": "Livindi",
    "zemplee": "Zemplee",
    "agebold": "AgeBold",
    "spiro100": "Spiro100",
    "teamvivo": "Team Vivo",
    "youralcove": "Alcove",
    "aloecare": "Aloe Care",
    "tochtech": "Tochtech",
    "domalys": "Domalys",
    "caru-care": "Caru",
    "stack": "Stack Care",
    "nemlia": "Nemlia",
    "sensorscall": "SensorsCall",
    "gaitbetter": "GaitBetter",
    "caredaily": "CareDaily",
    "herohealth": "Hero Health",
    "getluna": "Luna",
    "customhealth": "Custom Health",
    "toilabs": "Toi Labs",
    "pacsana": "Pacsana",
    "homeguardian": "Home Guardian",
    "omekitchen": "OmeKitchen",
    "cognitivesystems": "Cognitive Systems",
    "mychirp": "Chirp",
    "nobi": "Nobi",
    "zibrio": "Zibrio",
    "tangobelt": "TangoBelt",
    "vayyar": "Vayyar",
    "nymblscience": "Nymbl",
    "safely-you": "SafelyYou",
    "altumview": "Altumview",
    "getbide": "Bide",
    "sound-eye": "SoundEye",
    "kamivision": "KamiVision",
    "carevocacy": "Carevocacy",
    "candootech": "Candoo",
    "careyaya": "CareYaya",
    "onestep": "OneStep",
    "imagorehab": "Imago Rehab",
    "voiceitt": "Voiceitt",
    "reev": "Reev",
    "mylumin": "MyLumin",
    "quiltt": "Quiltt",
    "avista": "Avista",
    "getmebright": "Bright",
    "mentia": "Mentia",
    "singfit": "SingFit",
    "effectivate": "Effectivate",
    "maphabit": "MapHabit",
    "virtuleap": "Virtuleap",
    "tembo": "Tembo Health",
    "lucidtherapeutics": "Lucid Therapeutics",
    "oroi": "Oroi",
    "zinniatv": "Zinnia TV",
    "liveivory": "LiveIvory",
    "ethhar": "Ethhar",
    "ellie": "Ellie",
    "bluemarblehealthco": "Blue Marble Health",
    "torchlight": "Torchlight",
    "somatix": "Somatix",
    "essencesmartcare": "Essence SmartCare",
    "cherishhealth": "Cherish Health",
    "envoyathome": "Envoy At Home",
    "voxela": "Voxela",
    "winihealth": "WiniHealth",
    "elliapp": "Elli",
    "seremy": "Seremy",
    "bayartis": "Bayartis",
    "wellsaid": "WellSaid",
    "crony": "Crony",
    "nasoni": "Nasoni",
    "mywisdom": "MyWisdom",
    "longliveapp": "LongLive",
    "gcare": "GCare",
    "trelawear": "TrelaWear",
    "careflick": "CareFlick",
    "speak2family": "Speak2Family",
    "tover": "Tover",
    "witlingo": "Witlingo",
    "memomate": "MemoMate",
    "patientcompanion": "Patient Companion",
    "roobrik": "Roobrik",
    "hayylo": "Hayylo",
    "heartlegacy": "HeartLegacy",
    "serenityengage": "Serenity Engage",
    "conpago": "Conpago",
    "lifeloop": "LifeLoop",
    "teiacare": "Teia Care",
    "tapestryhealth": "Tapestry Health",
    "care": "Care Life",
    "amaiacuida": "Amaia Cuida",
    "kando": "Kando",
    "sunboundhomes": "Sunbound Homes",
    "jubohealth": "Jubo Health",
    "dreamsedge": "DreamsEdge",
    "joinhively": "Hively",
    "medminder": "MedMinder",
    "sign-speak": "Sign-Speak",
    "aequilibria": "Aequilibria",
    "memoryboard": "MemoryBoard",
    "askelbi": "Askelbi",
    "birdiebox": "BirdieBox",
    "advocord": "Advocord",
    "trytendercare": "TenderCare",
    "supportpay": "SupportPay",
    "rubywell": "RubyWell",
    "theoak": "TheOak",
    "geni": "Geni",
    "khyaal": "Khyaal",
    "funandmoving": "FunAndMoving",
    "navelrobotics": "Navel Robotics",
    "livy-care": "Livy Care",
    "mercuryalert": "Mercury Alert",
    "wearehelpful": "Helpful",
    "mellie": "Mellie",
    "family-first": "Family First",
    "keep-company": "Keep Company",
    "withgrayce": "Grayce",
    "lottie": "Lottie",
    "yurtle": "Yurtle",
    "momentra": "Momentra",
    "joingivers": "Givers",
    "nomosmartcare": "Nomo Smart Care",
    "circleengage": "Circle Engage",
    "thehelperbees": "The Helper Bees",
    "6degrees": "6Degrees",
    "graceycare": "GraceyCare",
    "primeschedules": "Prime Schedules",
    "ludicahealth": "Ludica Health",
    "smartfitinc": "SmartFit",
    "clarishealthcare": "Claris Healthcare",
    "elderado": "Elderado",
    "go-paige": "Paige",
    "wearefamilial": "Familial",
    "seniorverse": "SeniorVerse",
    "storiicare": "StoriiCare",
    "diidii": "Diidii",
    "hubbit": "Hubbit",
    "en": "Hyodol",
    "careswitch": "CareSwitch",
    "lolacares": "Lola Cares",
    "careconnectmobile": "Care Connect Mobile",
    "myonacare": "Ona Care",
    "nevvon": "Nevvon",
    "electroniccaregiver": "Electronic Caregiver",
    "grand-app": "Grand-App",
    "eldycare": "Eldy Care",
    "gobloominghealth": "Blooming Health",
    "telegrafik": "Telegrafik",
    "kwido": "Kwido",
    "caribou": "Caribou",
    "monami": "MonAmi",
    "vermutapp": "Vermut",
    "cocooners": "Cocooners",
    "onscreeninc": "OnScreen",
    "iameve": "Eve",
    "getzoog": "Zoog",
    "mycarelink360": "MyCareLink360",
    "independa": "Independa",
    "kinsome": "Kinsome",
    "theloopvillage": "The Loop Village",
    "razmobility": "Raz Mobility",
    "e2c": "E2C",
    "caavo": "Caavo",
    "family": "Family Cards",
    "kluppen": "Kluppen",
    "nourishcare": "Nourish Care",
    "predicaire": "Predicaire",
    "genieconnect": "GenieConnect",
    "miicare": "MiiCare",
    "lifebio": "LifeBio",
    "meminto": "Meminto",
    "artifcts": "Artifcts",
    "aftercloud": "AfterCloud",
    "cajalegado": "Caja Legado",
    "stitch": "Stitch",
    "eversafe": "EverSafe",
    "ezio": "Ezio",
    "telecalmprotects": "TeleCalm",
}


def infer_category(x, y):
    """Infer company's category based on its (x, y) position relative to category labels."""
    # Define category regions as y-bands with x-subregions
    # The map is divided into horizontal bands and the company belongs to the nearest category

    # Build a list of (region, subcat, center_x, center_y) for each category
    cats = []
    for cr in CATEGORY_REGIONS:
        cats.append((cr["region"], cr["subcat"], cr["x"], cr["y"]))

    # Find nearest category by distance
    min_dist = float('inf')
    best_cat = None
    best_subcat = None
    best_region = None

    for region, subcat, cx, cy in cats:
        # Use weighted distance: y distance is more important than x
        # because the map is organized in horizontal bands
        dy = abs(y - cy)
        dx = abs(x - cx)

        # If company is within ~70px vertically of a label, it's likely in that category
        if dy < 80:
            dist = dy + dx * 0.3  # x matters less
            if dist < min_dist:
                min_dist = dist
                best_region = region
                best_subcat = subcat

    if best_region is None:
        # Fallback: find closest by y only
        min_dy = float('inf')
        for region, subcat, cx, cy in cats:
            dy = abs(y - cy)
            if dy < min_dy:
                min_dy = dy
                best_region = region
                best_subcat = subcat

    return best_region or "Unknown", best_subcat or "Unknown"


def normalize_name(domain_name):
    """Convert domain name to proper company name."""
    # Check corrections table first
    if domain_name in NAME_CORRECTIONS:
        return NAME_CORRECTIONS[domain_name]

    # Auto-format: split by hyphens, capitalize each word
    parts = domain_name.replace('-', ' ').replace('_', ' ').split()
    return ' '.join(p.capitalize() for p in parts)


def extract_companies():
    """Extract all companies from Market Map PDF."""
    companies = []
    seen_urls = set()

    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[0]
        hyperlinks = page.hyperlinks

        for h in hyperlinks:
            uri = h.get('uri', '')
            if not uri or 'thegerontechnologist.com' in uri:
                continue
            if uri in seen_urls:
                continue
            seen_urls.add(uri)

            domain = urlparse(uri).netloc.replace('www.', '')
            # Get the main domain name (before TLD)
            domain_parts = domain.split('.')
            domain_name = domain_parts[0] if domain_parts else domain

            # Skip geni.us affiliate links - they're not companies
            if domain_name == 'geni':
                continue

            name = normalize_name(domain_name)
            x = round(h.get('x0', 0), 1)
            y = round(h.get('top', 0), 1)

            region, subcat = infer_category(x, y)
            mapped_category = CATEGORY_MAPPING.get(subcat, "养老用品")

            companies.append({
                "name": name,
                "name_raw": domain_name,
                "url": uri,
                "domain": domain,
                "category_raw": subcat,
                "category_region": region,
                "category_mapped": mapped_category,
                "category": mapped_category,  # compatibility with existing system
                "region": "overseas",
                "priority": "P2",
                "source": "AgeTech Market Map 2025",
                "source_detail": "market_map",
                "pdf_x": x,
                "pdf_y": y,
                "tags": [region] if region != "Unknown" else [],
            })

    return companies


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Extracting companies from Market Map PDF...")
    companies = extract_companies()

    print(f"\nTotal companies extracted: {len(companies)}")

    # Category distribution
    cat_dist = {}
    for c in companies:
        cat = c["category_mapped"]
        cat_dist[cat] = cat_dist.get(cat, 0) + 1

    print("\nCategory distribution (mapped):")
    for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Region distribution
    region_dist = {}
    for c in companies:
        r = c["category_region"]
        region_dist[r] = region_dist.get(r, 0) + 1

    print("\nRegion distribution (raw):")
    for r, count in sorted(region_dist.items(), key=lambda x: -x[1]):
        print(f"  {r}: {count}")

    # Save
    output_path = os.path.join(DATA_DIR, "agetech_map_raw.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output_path}")
    print(f"Total: {len(companies)} companies")


if __name__ == '__main__':
    main()
