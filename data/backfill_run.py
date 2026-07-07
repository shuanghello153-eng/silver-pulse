#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 银发经济新闻数据回填：补全缺失的 title_cn / summary_cn
# 规则：
#  - 中文标题 -> title_cn = title
#  - 英文标题且在 manual_titles.json -> 使用人工翻译
#  - 英文标题仅为 " - Source" 残片 -> 原样保留 (passthrough)
#  - 其余英文标题 -> MyMemory 兜底翻译
#  - 中文摘要 -> summary_cn = summary (&nbsp; 解码)
#  - 英文摘要且与标题重复 -> summary_cn = title_cn
#  - 其余英文摘要 -> MyMemory 翻译
# 不修改任何非翻译字段，不删除条目。
import json, re, sys, time, requests

DATA_DIR = r"G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data"
FILES = ["raw_20260702.json", "raw_20260704.json", "raw_20260706.json", "raw_20260707.json"]

def is_cn(s):
    return bool(re.search(r'[一-鿿]', s or ''))

def has_latin(s):
    return bool(re.search(r'[A-Za-z]', s or ''))

def is_junk_title(t):
    # 去掉结尾 " - Source" 后所剩无几（如 "- McKnight's Senior Living"）
    s = re.sub(r'\s*-\s*[^-\n]+$', '', t).strip()
    return (s == '' or s == '-') and not has_latin(s)

def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', s or '')).strip().lower()

def clean(t):
    if not t:
        return t
    t = t.replace('&nbsp;', ' ')
    # 去掉金额前多余的 "$"（MyMemory 有时保留 "$ 5000万"）
    t = re.sub(r'\$\s*(?=\d)', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# ---- MyMemory 翻译（带重试/配额检测）----
MM = "https://api.mymemory.translated.net/get"
_cache = {}

def translate(text):
    if not text:
        return ''
    if text in _cache:
        return _cache[text]
    out = None
    for attempt in range(4):
        try:
            r = requests.get(MM, params={'q': text, 'langpair': 'en|zh-CN'}, timeout=25)
            j = r.json()
            st = j.get('responseStatus')
            if st == 200:
                tr = clean(j.get('responseData', {}).get('translatedText', ''))
                _cache[text] = tr
                time.sleep(0.3)
                return tr
            msg = str(j.get('responseMessage', ''))
            if st == 429 or 'QUOTA' in msg.upper():
                sys.stderr.write("[QUOTA] MyMemory 配额耗尽\n")
                out = None
                break
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
    return out

def load_manual():
    try:
        return json.load(open(DATA_DIR + "/manual_titles.json", encoding='utf-8'))
    except Exception:
        return {}

def process(path, manual):
    arr = json.load(open(path, encoding='utf-8'))
    tcount = 0
    scount = 0
    quota_hit = False
    for x in arr:
        title = x.get('title') or ''
        summary = x.get('summary')
        # ---- title_cn ----
        if not x.get('title_cn'):
            if is_cn(title):
                x['title_cn'] = title
            elif title in manual:
                x['title_cn'] = manual[title]
            elif is_junk_title(title):
                x['title_cn'] = title
            else:
                tr = translate(title)
                if tr is None:
                    quota_hit = True
                else:
                    x['title_cn'] = tr
            if x.get('title_cn'):
                tcount += 1
        # ---- summary_cn ----
        if not x.get('summary_cn') and summary:
            s = summary
            if is_cn(s):
                x['summary_cn'] = s.replace('&nbsp;', ' ')
            else:
                tn = re.sub(r'-\s*\w+$', '', norm(title)).strip()
                sn = re.sub(r'-\s*\w+$', '', norm(s)).strip()
                if sn and (sn in tn or tn in sn):
                    x['summary_cn'] = x.get('title_cn') or ''
                else:
                    tr = translate(s)
                    if tr is None:
                        quota_hit = True
                    else:
                        x['summary_cn'] = tr
            if x.get('summary_cn'):
                scount += 1
    json.dump(arr, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    name = path.split('/')[-1].split('\\')[-1]
    print(f"DONE {name}: title_cn 翻译 {tcount} 条, summary_cn 翻译 {scount} 条"
          + ("  [注意: MyMemory 配额耗尽，部分条目未翻译]" if quota_hit else ""))

def main():
    manual = load_manual()
    print(f"已加载人工标题翻译 {len(manual)} 条")
    for f in FILES:
        process(DATA_DIR + "/" + f, manual)

if __name__ == "__main__":
    main()
