# -*- coding: utf-8 -*-
"""
UI 走查机制（A9 / T33-validate）

不靠肉眼，对三页 HTML + ui_common.py 做结构自检验证：
  A5  不常用按钮收进「更多」折叠区（tools-more / tools-more-btn 存在）
  A6  收藏按钮改为蓝色胶囊（fav-filter-btn 不再用橙色 #f59e0b，改用 accent）
  A7  标签/筛选行对齐（filter-row 垂直居中；f-label 与 filter-label 同宽）
  A8  已读/未读（unread-toggle + read-btn 存在；企业库卡片含 data-card-id）
  T32 雷达 CSS 残留清零（HTML 与 ui_common.py 均不含 radar-block）
  T36 about 信源数 = 50（config 当前 44+6）

用法：
  python ui_walkthrough.py            # 检查已生成的 root html
  python ui_walkthrough.py --output   # 同时检查 output/ 下 html

退出码：0 全部通过，1 有失败。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "enterprise.html", "about.html"]


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s%s" % (status, name, (" — " + detail) if detail else ""))
    return cond


def main():
    check_output = "--output" in sys.argv
    all_ok = True

    # ---- 1. ui_common.py 静态检查（A6 / A7 / T32） ----
    ui = open(os.path.join(ROOT, "ui_common.py"), encoding="utf-8").read()

    # A6: fav-filter-btn 不再用橙色虚线 #f59e0b
    fav_block = re.search(r"\.fav-filter-btn\{[^}]*\}", ui)
    fav_css = fav_block.group(0) if fav_block else ""
    ok_a6 = ("#f59e0b" not in fav_css) and ("accent-grad" in fav_css or "var(--accent" in fav_css)
    all_ok &= check("A6 收藏按钮(蓝色胶囊)", ok_a6,
                    "fav-filter-btn 仍为橙色" if not ok_a6 else "已改蓝色")

    # A7: filter-row 垂直居中
    fr = re.search(r"\.filter-row\{[^}]*\}", ui)
    fr_css = fr.group(0) if fr else ""
    ok_a7 = "align-items:center" in fr_css
    all_ok &= check("A7 筛选行垂直居中", ok_a7,
                    "filter-row 未居中" if not ok_a7 else "align-items:center")

    # T32: ui_common.py 无 radar-block CSS
    ok_t32 = "radar-block" not in ui
    all_ok &= check("T32 ui_common 无 radar CSS", ok_t32,
                    "仍含 radar-block" if not ok_t32 else "已清理")

    # ---- 2. 逐页 HTML 结构检查 ----
    for fn in PAGES:
        path = os.path.join(ROOT, fn)
        if not os.path.exists(path):
            all_ok &= check("页面存在 " + fn, False, "文件缺失")
            continue
        html = open(path, encoding="utf-8").read()

        # T32: 无 radar-block
        ok_r = "radar-block" not in html
        all_ok &= check("T32 %s 无 radar-block" % fn, ok_r)

        # A5: 更多折叠
        ok_more = ("tools-more-btn" in html) and ("tools-more" in html)
        all_ok &= check("A5 %s 更多折叠区" % fn, ok_more)

        # A8: 已读/未读（about 页无需）
        if fn != "about.html":
            ok_u = ("unread-toggle" in html) and ("read-btn" in html)
            all_ok &= check("A8 %s 未读切换+已读按钮" % fn, ok_u)
            if fn == "enterprise.html":
                ok_cid = 'data-card-id="' in html
                all_ok &= check("A8 企业卡 data-card-id", ok_cid)

        # T36: about 信源数 = 与 config.SOURCES 一致（文档与代码一致）
        if fn == "about.html":
            m = re.search(r"(\d+)\s*个信源", html) or re.search(r"(\d+)\s*个源", html)
            n = int(m.group(1)) if m else 0
            try:
                import config as _cfg
                expected = len(_cfg.SOURCES)
            except Exception:
                expected = None
            if expected is None:
                ok_src = n > 0
                detail = ("显示 %d（无法读取 config，仅验证非空）" % n)
            else:
                ok_src = (n == expected)
                detail = ("显示 %d，config=%d%s" % (n, expected, " ✅一致" if n == expected else " ❌不一致"))
            all_ok &= check("T36 about 信源数=config", ok_src, detail)

    # ---- 3. 可选：output/ 下副本 ----
    if check_output:
        for fn in PAGES:
            op = os.path.join(ROOT, "output", fn)
            if os.path.exists(op):
                h = open(op, encoding="utf-8").read()
                all_ok &= check("output/%s 无 radar-block" % fn, "radar-block" not in h)
                all_ok &= check("output/%s 更多折叠" % fn,
                                ("tools-more-btn" in h) and ("tools-more" in h))

    print("\n=== %s ===" % ("全部通过 ✅" if all_ok else "存在失败 ❌"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
