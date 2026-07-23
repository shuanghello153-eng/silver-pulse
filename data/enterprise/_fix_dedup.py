import json, re
from collections import defaultdict

DB = "data/enterprise/all_enterprises.json"
data = json.load(open(DB, encoding="utf-8"))


def nz(e, k):
    return str(e.get(k) or "").strip()


def has(e, k):
    v = e.get(k)
    if isinstance(v, list):
        return len(v) > 0
    return bool(nz(e, k))


def s(v):
    return str(v or "").strip()


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()] if str(v).strip() else []


# normalize list-typed fields globally (some records store them as strings)
for e in data:
    for fld in ("highlights", "tag_l1", "tag_l2"):
        e[fld] = as_list(e.get(fld))
    if isinstance(e.get("category_l1"), list):
        e["category_l1"] = e["category_l1"][0] if e["category_l1"] else ""
    if isinstance(e.get("category_l2"), list):
        e["category_l2"] = e["category_l2"][0] if e["category_l2"] else ""

thin_set = set(e.get("serial") for e in data if 0 < len(nz(e, "description")) <= 20)

# (a) desc_cn backfill for 313
filled = 0
for e in data:
    if not nz(e, "desc_cn") and nz(e, "description"):
        e["desc_cn"] = nz(e, "description")
        filled += 1
print("desc_cn backfilled:", filled)

# (b) _desc_patch application (exact + fuzzy)
dp = json.load(open("data/enterprise/_desc_patch.json", encoding="utf-8"))
by_name = {nz(e, "name").lower(): e for e in data}
exact_applied = 0
fuzzy_applied = 0
no_match = []


def try_apply(rec, desc):
    cur = nz(rec, "description")
    if 20 < len(cur) <= 50 and rec.get("serial") not in thin_set:
        rec["description"] = desc
        if not nz(rec, "desc_cn"):
            rec["desc_cn"] = desc
        return True
    return False


for nm, desc in dp.items():
    rec = by_name.get(nm.lower())
    if rec and try_apply(rec, desc):
        exact_applied += 1
        continue
    if rec:
        continue  # matched but not in apply range
    # fuzzy: part before paren / first token
    pre = re.split(r"[（(]", nm)[0].strip()
    cand = None
    for e in data:
        en = nz(e, "name")
        if en == pre or en.startswith(pre) or (pre and pre in en):
            cand = e
            break
    if cand and try_apply(cand, desc):
        fuzzy_applied += 1
    elif not cand:
        no_match.append(nm)
print(f"_desc_patch: exact={exact_applied}, fuzzy={fuzzy_applied}, no_match={no_match}")

# (c) dedup 6 normalized pairs
SUF = re.compile(r"(股份有限公司|有限责任公司|有限公司|股份公司|集团|公司|企业|科技|技术|网络|信息|有限|责任|corp|inc|llc|ltd|co|gmbh|plc|\.|,|，|、|\s)+$", re.I)


def norm(n):
    n = n.lower().strip()
    n = re.sub(r"[\s\-—_.，、。,()（）/]+", "", n)
    return SUF.sub("", n)


groups = defaultdict(list)
for e in data:
    nm = nz(e, "name")
    if nm:
        groups[norm(nm)].append(e)


def score(e):
    s_ = sum(1 for k in ("recommend", "founded", "funding_latest", "website_url", "region", "payor_model", "investors") if has(e, k))
    s_ += len(e.get("highlights") or []) > 0
    s_ += len(e.get("tag_l2") or e.get("category_l2") or []) > 0
    s_ += len(nz(e, "description")) / 40.0 + len(nz(e, "recommend")) / 80.0
    return s_


report = []
SKIP = {"唯艾"}
for k, v in groups.items():
    if len(v) <= 1:
        continue
    if any(x.get("serial") in thin_set for x in v):
        report.append(f"SKIP(thin-in-pair): {[(x.get('serial'), nz(x,'name')) for x in v]}")
        continue
    names = set(nz(x, "name") for x in v)
    if names & SKIP:
        report.append(f"SKIP(collision): {sorted(names)}")
        continue
    v = sorted(v, key=score, reverse=True)
    K, D = v[0], v[1]
    for fld in ("founded", "stage", "funding_latest", "funding_total", "investors", "website_url", "region", "payor_model"):
        if not has(K, fld) and has(D, fld):
            K[fld] = D[fld]
    kh = set(K["highlights"])
    for h in D["highlights"]:
        hs = s(h)
        if hs and hs not in kh:
            K["highlights"].append(h)
            kh.add(hs)
    for fld in ("tag_l1", "tag_l2"):
        base = K.get(fld) or []
        add = D.get(fld) or []
        merged = list(base)
        for t in add:
            if t not in merged:
                merged.append(t)
        K[fld] = merged
    if not nz(K, "desc_cn") and nz(D, "desc_cn"):
        K["desc_cn"] = nz(D, "desc_cn")
    data = [x for x in data if x is not D]
    report.append(f"MERGED keep={K.get('serial')} drop={D.get('serial')} ({nz(K,'name')})")

# (d) AARP (only if both still present)
aarp = [e for e in data if "aarp" in nz(e, "name").lower()]
if len(aarp) > 1:
    keep = [e for e in aarp if e.get("serial") == "#0485"][0]
    drop = [e for e in aarp if e.get("serial") == "#0601"][0]
    insight = "其会员信任资产高度商业化——公开资料显示约六成收入来自品牌授权与保险分销抽成，'信任即分销渠道'是稀缺定位。"
    if "会员信任" not in nz(keep, "description"):
        keep["description"] = nz(keep, "description").rstrip("。") + "。" + insight
    if not nz(keep, "desc_cn"):
        keep["desc_cn"] = nz(keep, "description")
    if "品牌授权" not in nz(keep, "recommend"):
        keep["recommend"] = nz(keep, "recommend").rstrip("。") + "。补充视角：" + insight
    data = [x for x in data if x is not drop]
    report.append("AARP MERGED keep=#0485 drop=#0601")

# (e) deep_article_links field
for e in data:
    if "deep_article_links" not in e:
        e["deep_article_links"] = []

print("\n=== DEDUP REPORT ===")
for r in report:
    print(" ", r)
print("\nrecords now:", len(data))
json.dump(data, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("saved", DB)
