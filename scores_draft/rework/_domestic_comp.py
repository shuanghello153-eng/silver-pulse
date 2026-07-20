# -*- coding: utf-8 -*-
"""国内竞品核查 helper。
给定一家企业，从企业库里找 region=='国内' 且 tag_l1/tag_l2 有重叠的其他企业，
用于防止工人瞎写「国内空白/缺乏」。纯查库，零联网，秒级返回。

用法（被 check_single.py 与工人脚本 import）：
  from _domestic_comp import DomesticComp
  dc = DomesticComp()                      # 加载一次
  hits = dc.find(serial, top=5)            # 返回 [(serial, name, name_cn, tag_l2, overlap), ...]
  dc.has(serial)                           # 是否有国内竞品
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")


class DomesticComp:
    _cache = None

    def _load(self):
        if DomesticComp._cache is None:
            d = json.load(open(DB, encoding="utf-8"))
            by = {}
            for e in d:
                s = str(e.get("serial", "")).lstrip("#")
                by[s] = e
            DomesticComp._cache = (d, by)
        return DomesticComp._cache

    def find(self, serial, top=5):
        _, by = self._load()
        self_serial = str(serial).lstrip("#")
        self_e = by.get(self_serial)
        if not self_e:
            return []
        self_l1 = set(self_e.get("tag_l1") or [])
        self_l2 = set(self_e.get("tag_l2") or [])
        hits = []
        for s, e in by.items():
            if s == self_serial:
                continue
            if e.get("region") != "国内":
                continue
            ol1 = set(e.get("tag_l1") or []) & self_l1
            ol2 = set(e.get("tag_l2") or []) & self_l2
            if ol1 or ol2:
                nm = e.get("name_cn") or e.get("name") or s
                hits.append((s, e.get("name"), nm, list(ol2), len(ol1) + len(ol2)))
        # 重叠维度多的排前面；并列按 serial
        hits.sort(key=lambda x: (-x[4], x[0]))
        return hits[:top]

    def has(self, serial):
        return len(self.find(serial, top=1)) > 0

    def names(self, serial, top=5):
        """返回国内竞品的中文名列表，方便写进推荐理由。"""
        return [h[2] for h in self.find(serial, top=top)]


if __name__ == "__main__":
    import sys
    dc = DomesticComp()
    for s in sys.argv[1:]:
        print(f"=== #{s} 国内竞品 ===")
        for h in dc.find(s):
            print(f"  #{h[0]} {h[2]}  重叠二级标签:{h[3]}")
