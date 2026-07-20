# -*- coding: utf-8 -*-
"""
重做合并 + 独立门禁：只合并通过 check_single 的草稿，不过的留队列打回重做。
用法：python rework_merge.py           合并 scores_draft/rework/draft_#*.json
      python rework_merge.py --commit  合并后 git commit 检查点
流程铁律：安全草稿(绝不直写库) -> 主智能体单线程合并 -> 独立门禁 -> 过则写库删草稿 -> git 检查点
"""
import json, os, glob, argparse, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTDIR = HERE  # 草稿落在 rework 顶层 draft_#XXXX.json
sys.path.insert(0, HERE)
from check_single import validate, content_len

SAFE = ("recommend", "desc_cn", "silver_reason", "payor_model", "update_time", "flag")


def ser(e):
    return int(str(e["serial"]).lstrip("#"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    d = json.load(open(DB, encoding="utf-8"))
    by = {ser(e): e for e in d}
    drafts = glob.glob(os.path.join(DRAFTDIR, "draft_*.json"))
    print(f"发现草稿 {len(drafts)} 个")

    # 先收集所有草稿的 recommend，用于跨企业去重(R10)
    draft_recs = {}
    for fp in drafts:
        try:
            dr = json.load(open(fp, encoding="utf-8"))
            draft_recs[ser(dr)] = dr.get("recommend", "")
        except Exception:
            pass
    others = list(draft_recs.values())

    patched = 0
    fails = {}
    flagged = {}
    for fp in drafts:
        try:
            dr = json.load(open(fp, encoding="utf-8"))
        except Exception as ex:
            fails[fp] = [f"草稿坏: {ex}"]
            continue
        s = ser(dr)
        e = by.get(s)
        if not e:
            fails[s] = ["serial不在库"]
            continue
        tmp = dict(e)
        for k in SAFE:
            if k in dr and dr[k] is not None:
                tmp[k] = dr[k]
        iss = validate(tmp, others=others)
        if not iss:
            for k in SAFE:
                if k in dr and dr[k] is not None:
                    e[k] = dr[k]
            if dr.get("flag"):
                flagged[s] = dr["flag"]
            patched += 1
            os.remove(fp)
        else:
            fails[s] = iss
    if patched:
        json.dump(d, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"已合并通过门禁的草稿 {patched} 家，写回 DB")
    else:
        print("无通过门禁的草稿，DB 未改动")
    json.dump({"fails": fails, "patched": patched},
              open(os.path.join(HERE, "merge_fails.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if flagged:
        fpath = os.path.join(HERE, "flags_merged.json")
        prev = json.load(open(fpath, encoding="utf-8")) if os.path.exists(fpath) else {}
        prev.update({str(k): v for k, v in flagged.items()})
        json.dump(prev, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"收集到 {len(flagged)} 条源库疑误 flag -> {fpath}")
    print(f"本次合并通过 {patched} | 未过留队列 {len(fails)}")
    if args.commit and patched:
        subprocess.run(["git", "add", DB], cwd=BASE)
        subprocess.run(["git", "-c", "user.email=agent@local", "-c", "user.name=agent",
                        "commit", "-m", f"rework: merge {patched} enterprises (check_single-passed)"], cwd=BASE)
        print("已 git commit 检查点")
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if main() > 0 else 0)
