# -*- coding: utf-8 -*-
"""临时驱动：在不修改 collector.py 的前提下，给所有源设置 10s 网络超时上限，
避免 Google News/Bing 30s 超时叠加导致整轮跑不完。collect_all 结束仍会落盘
data/raw_YYYYMMDD.json，保证结果可用。"""
import collector

for _sid, _cfg in collector.SOURCES.items():
    _cfg["timeout"] = 10

if __name__ == "__main__":
    arts = collector.collect_all()
    print("[wrapper] collect_all returned %d top articles" % len(arts))
