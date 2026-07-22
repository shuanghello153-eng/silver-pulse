# -*- coding: utf-8 -*-
"""企业实体匹配器：由 entity_name（或文章标题）匹配 all_enterprises 的 serial。
集中调用，避免每个子智能体重复加载 1780 条企业库。
用法：
    from _ent_match import match_serial, match_from_text
"""
import json
import os
import re

REPO = os.path.dirname(os.path.abspath(__file__))
ENT_PATH = os.path.join(REPO, "enterprise", "all_enterprises.json")

_CACHE = None


def _load():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    ents = json.load(open(ENT_PATH, encoding="utf-8"))
    # 建立 name/alias -> serial 索引（小写）
    by_name = {}
    for e in ents:
        ser = e.get("serial")
        if not ser:
            continue
        nm = (e.get("name") or "").strip()
        if nm:
            by_name[nm.lower()] = (ser, nm)
        al = e.get("alias")
        if isinstance(al, list):
            for a in al:
                if a and str(a).strip():
                    by_name[str(a).strip().lower()] = (ser, nm)
        elif isinstance(al, str) and al.strip():
            by_name[al.strip().lower()] = (ser, nm)
    _CACHE = (ents, by_name)
    return _CACHE


def match_serial(entity_name):
    """给定 entity_name，返回匹配到的 #xxxx serial 或 ''（未命中）。"""
    if not entity_name or not str(entity_name).strip():
        return ""
    ents, by_name = _load()
    key = str(entity_name).strip().lower()
    if key in by_name:
        return by_name[key][0]
    # 部分包含匹配（entity_name 可能是企业名子串）
    for k, (ser, nm) in by_name.items():
        if k and (k in key or key in k):
            return ser
    return ""


def match_from_text(text):
    """从文章标题/正文里找是否提及企业库企业名，返回 (serial, name) 或 ('', '')。"""
    if not text:
        return ("", "")
    ents, by_name = _load()
    low = text.lower()
    best = ("", "")
    # 优先全称命中
    for k, (ser, nm) in by_name.items():
        if k and len(k) >= 3 and k in low:
            # 越长越精确
            if not best[0] or len(k) > len(best[1] or ""):
                best = (ser, nm)
    return best


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "优必选"
    print(q, "->", match_serial(q))
