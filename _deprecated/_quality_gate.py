"""
企业库质量门禁校验脚本 — 每次部署前必跑。
规则设计原则：轻量、精准、不误报。
发现问题时 EXIT 1 阻止部署。
用法: python data/enterprise/_quality_gate.py
"""
import json, re, sys

DB_PATH = 'data/enterprise/all_enterprises.json'

# === 规则定义 ===
RULES = []

def check(func, name, severity='error'):
    """注册一条校验规则"""
    RULES.append({'func': func, 'name': name, 'severity': severity})

# ---- Rule 1: 无脏标记 ----
def no_dirty_markers(db):
    markers = ['【提供资源】', '【需求数源】', '【供需】', '【邀请函】', '[提供资源]']
    fails = []
    for e in db:
        d = e.get('description', '')
        dc = e.get('desc_cn', '')
        for m in markers:
            if m in d:
                fails.append(f"  #{e['serial']} {e.get('name','')} description含'{m}'")
            if m in dc:
                fails.append(f"  #{e['serial']} {e.get('name','')} desc_cn含'{m}'")
    return fails if fails else None
check(no_dirty_markers, "无飞书供需表脏标记")

# ---- Rule 2: description 最小长度 ----
def desc_min_length(db):
    MIN_LEN = 20
    fails = []
    for e in db:
        d = e.get('description', '')
        if len(d) < MIN_LEN:
            # 允许标了"信息不足"的
            if '信息不足' not in d:
                fails.append(f"  #{e['serial']} {e.get('name','')} description={len(d)}字(<{MIN_LEN})")
    return fails if fails else None
check(desc_min_length, "description >= 20字（信息不足除外）")

# ---- Rule 3: recommend 非空 ----
def recommend_not_empty(db):
    fails = []
    for e in db:
        r = e.get('recommend', '')
        if not r or (isinstance(r, str) and len(r.strip()) < 10):
            fails.append(f"  #{e['serial']} {e.get('name','')} recommend为空或过短")
    return fails if fails else None
check(recommend_not_empty, "recommend非空且>=10字")

# ---- Rule 4: tag_l1 非空 ----
def tag_l1_not_empty(db):
    fails = []
    for e in db:
        t = e.get('tag_l1', [])
        if not t or (isinstance(t, list) and len(t) == 0):
            fails.append(f"  #{e['serial']} {e.get('name','')} 无一级标签")
    return fails if fails else None
check(tag_l1_not_empty, "tag_l1非空")

# ---- Rule 5: 无异常字符/格式 ----
def no_format_anomalies(db):
    fails = []
    for e in db:
        d = e.get('description', '')
        # 纯JSON残留
        if d.startswith('{') or d.startswith('['):
            fails.append(f"  #{e['serial']} {e.get('name','')} description疑似JSON")
        # 连续3个以上相同标点
        if re.search(r'[。。。！？？]{3,}', d):
            fails.append(f"  #{e['serial']} {e.get('name','')} description有异常重复标点")
    return fails if fails else None
check(no_format_anomalies, "无格式异常(JSON/重复标点)")

# ---- Rule 6: serial 格式 ----
def serial_format(db):
    fails = []
    for e in db:
        s = e.get('serial', '')
        if not re.match(r'^#\d{4}$', s):
            fails.append(f"  serial格式异常: {s} ({e.get('name','')})")
    # 检查重复
    serials = [e.get('serial') for e in db]
    dupes = [s for s in set(serials) if serials.count(s) > 1]
    for s in dupes:
        names = [e.get('name') for e in db if e.get('serial') == s]
        fails.append(f"  重复serial: {s} → {names}")
    return fails if fails else None
check(serial_format, "serial格式正确且唯一")

# ---- Rule 7: 无英文主导描述 ----
def no_english_dominant(db):
    """description不能是英文主导(ascii字母占比>50%且长度>30)。允许常见专业术语。"""
    # 银发经济/医疗/金融领域常见英文术语白名单（出现在中文描述中不算违规）
    whitelist_terms = [
        'Medicare', 'Medicaid', 'FDA', 'REIT', 'IPO', 'NYSE', 'NASDAQ',
        'SaaS', 'API', 'AI', 'VR', 'IoT', 'GPS', 'SIM', 'DNA', 'RNA',
        'App', 'iOS', 'Android', 'KOL', 'B2B', 'B2C', 'O2O',
        'A/B', 'RPM', 'PACE', 'EMT', 'HMO', 'PPO', 'MA$',
        'Apple Watch', 'AirPods', 'iPhone', 'iPad',
        'a16z', 'CVS Health', 'UnitedHealth', 'Kaiser',
    ]
    fails = []
    for e in db:
        d = e.get('description', '')
        if len(d) < 30:
            continue
        # 先去掉白名单术语再检测
        cleaned = d
        for term in whitelist_terms:
            cleaned = cleaned.replace(term, '')
        
        alpha_chars = sum(1 for c in cleaned if c.isalpha())
        ascii_chars = sum(1 for c in cleaned if ord(c) < 128 and c.isalpha())
        if alpha_chars > 5 and (ascii_chars / alpha_chars) > 0.6:  # 放宽到60%，且至少5个字母才查
            fails.append(f"  #{e['serial']} {e.get('name','')} 英文占比>{int(ascii_chars/alpha_chars*100)}%")
    return fails if fails else None
check(no_english_dominant, "无英文主导描述(去专业术语后英文<60%)")

# ---- Rule 8: 无模板话术 ----
def no_template_phrases(db):
    """禁止万能填充式模板话术"""
    templates = [
        '公司主要通过渠道招商',
        '代理分销与产业链',
        '通过平台化运营与软硬件服务，连接银发人群',
        '面向银发人群及相关养老服务机构提供产品与服务',
        '对接私域流量',
    ]
    pattern = re.compile('|'.join(re.escape(t) for t in templates))
    fails = []
    for e in db:
        d = e.get('description', '')
        if pattern.search(d):
            fails.append(f"  #{e['serial']} {e.get('name','')} 含模板话术")
    return fails if fails else None
check(no_template_phrases, "无模板话术(渠道招商/代理分销等)")


def main():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"📋 企业库质量门禁 | 总数: {len(db)} 家 | {len(RULES)} 条规则\n")
    all_pass = True
    error_count = 0
    warn_count = 0
    
    for rule in RULES:
        result = rule['func'](db)
        sev = rule['severity']
        name = rule['name']
        
        if result is None:
            print(f"  ✅ {name}")
        else:
            count = len(result)
            if sev == 'error':
                print(f"  ❌ {name} ({count}项)")
                all_pass = False
                error_count += count
            else:
                print(f"  ⚠️  {name} ({count}项)")
                warn_count += count
            # 显示前10条详情
            for line in result[:10]:
                print(line)
            if count > 10:
                print(f"  ... 还有 {count-10} 项")
        sys.stdout.flush()
    
    print()
    if all_pass:
        print("🟢 全部通过，可以部署。")
        return 0
    else:
        print(f"🔴 未通过：{error_count} 个错误 / {warn_count} 个警告")
        print("   请修复后重新运行校验。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
