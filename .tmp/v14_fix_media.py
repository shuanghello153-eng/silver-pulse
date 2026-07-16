import json, re

PATH = 'data/enterprise/all_enterprises.json'
L1MAP = json.load(open('data/enterprise/_l2_l1.json'))
d = json.load(open(PATH))

MEDIA_HINT = re.compile(r'行业资讯|媒体内容|资讯|媒体|刊物|老博会|博览会|CMEF|expo|展会|资源对接平台|平台.*资讯', re.I)
def is_media(e):
    if MEDIA_HINT.search(e.get('desc_cn') or ''): return True
    if MEDIA_HINT.search(e.get('description') or ''): return True
    if MEDIA_HINT.search(e['name']): return True
    return False

# 16 companies that would become 0-tag after stripping 行业媒体 -> assign a sensible specific label
FALLBACK = {
    '摩根大通': ['金融理财'],
    'Rendever': ['陪伴服务'],
    'Vynca': ['健康管理'],
    '101 Mobility': ['养老运营'],
    'Arbital Health': ['健康服务平台'],
    'Ciba Health': ['慢病管理'],
    'Cloud DX': ['慢病管理'],
    'GroundGame Health/SameSky Health': ['健康服务平台'],
    'Ilant Health': ['慢病管理'],
    'Lotus Ring': ['智能家居'],
    'Nobi': ['跌倒监测'],
    'Remodel Health': ['金融理财'],
    'Steadiwear': ['康复器械'],
    'Transcarent': ['健康服务平台'],
    'Vayyar': ['智能家居'],
    'ŌURA': ['可穿戴监测'],
}

def recompute_l1(tags):
    out = []
    for t in tags:
        for l1 in L1MAP.get(t, []):
            if l1 not in out:
                out.append(l1)
    return out

kept = stripped = fallbacked = 0
changed_names = []
for e in d:
    t2 = e.get('tag_l2', [])
    if '行业媒体' not in t2:
        continue
    if is_media(e):
        kept += 1
        continue
    # strip 行业媒体
    new = [t for t in t2 if t != '行业媒体']
    if not new:
        fb = FALLBACK.get(e['name'])
        if not fb:
            # safety: never leave 0-tag
            fb = ['健康服务平台']
        new = fb
        fallbacked += 1
        changed_names.append(f"{e['name']}: [行业媒体] -> {new}")
    else:
        stripped += 1
        changed_names.append(f"{e['name']}: {t2} -> {new}")
    e['tag_l2'] = new
    e['tag_l1'] = recompute_l1(new)

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=1)
print(f"kept(media): {kept} | stripped: {stripped} | fallbacked(0-tag saved): {fallbacked}")
print("--- fallback assignments ---")
for c in changed_names:
    if '-> [健康服务平台]' in c or any(c.startswith(n+': [行业媒体]') for n in FALLBACK):
        print(c)
