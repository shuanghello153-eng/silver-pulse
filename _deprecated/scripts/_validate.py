import json, re

def bigrams(s):
    # extract CJK characters and ASCII words; build char-level bigrams for CJK,
    # and token bigrams for ascii words, to avoid cross-language false matches.
    s = str(s)
    bg = set()
    # CJK char bigrams
    cjk = re.findall(r'[\u4e00-\u9fff]', s)
    for i in range(len(cjk)-1):
        bg.add(cjk[i]+cjk[i+1])
    # ascii word tokens
    words = re.findall(r'[A-Za-z]+', s)
    for i in range(len(words)-1):
        bg.add((words[i]+' '+words[i+1]).lower())
    return bg

data = json.load(open('_batch_in_001.json', encoding='utf-8'))
rew = json.load(open('_batch_rewrites.json', encoding='utf-8'))

names = [d['name'] for d in data]
missing = [n for n in names if n not in rew]
extra = [n for n in rew if n not in names]
print('records:', len(data), 'rewrites:', len(rew))
print('missing in rewrites:', missing)
print('extra in rewrites:', extra)

overlaps = []
flagged = []
for d in data:
    n = d['name']
    desc = d['description'] or ''
    rec = rew.get(n, '')
    bd, br = bigrams(desc), bigrams(rec)
    if not br:
        ov = 0.0
    else:
        ov = len(bd & br) / len(br)
    overlaps.append(ov)
    if ov > 0.30:
        flagged.append((n, round(ov*100,1)))

avg = sum(overlaps)/len(overlaps)
print('avg bigram overlap: %.1f%%' % (avg*100))
print('flagged (>30%%):', flagged)
print('max overlap: %.1f%%' % (max(overlaps)*100))

# write output keyed by name (ids are all null, name is the unique key)
out = {d['name']: rew[d['name']] for d in data}
json.dump(out, open('_batch_out_001.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('written', len(out), 'entries to _batch_out_001.json')
