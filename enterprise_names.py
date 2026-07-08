"""企业库已知银发企业名称集合（小写），供相关性交叉校验。

当一篇资讯仅命中"弱词"（融资/机器人/AI 等泛词）时，
若其主体在企业库已知名单中，仍视为银发相关。
"""
import json
import os

_ENT_PATH = os.path.join("data", "enterprise", "all_enterprises.json")


def _load():
    try:
        with open(_ENT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set()
    s = set()
    for e in data:
        for k in ("name", "name_cn"):
            v = e.get(k)
            if v:
                s.add(str(v).strip().lower())
    return s


ENT_NAME_SET = _load()
