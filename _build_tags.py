# -*- coding: utf-8 -*-
"""[已废弃-薄壳] 旧标签构建脚本。

历史教训：本脚本的 MERGE 映射表仅覆盖 ~46 个规范词，原始二级分类(284种)与
Excel 细分领域_2(333种) 中大量值找不到对应会被【静默丢弃】——SODH / 相亲 等
标签就是这样丢的。为避免任何人再用旧逻辑重跑导致标签回退，本文件已改为
委托 `_rebuild_tags.py`（零丢失映射 + 产业资本方案B + 细分领域_2白名单）。

如需重打全量标签，请直接运行：
    python _rebuild_tags.py
本壳仅作转发，行为完全等价。
"""
import runpy, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
print('[_build_tags] 已废弃，转发到 _rebuild_tags.py（零丢失重建）...', file=sys.stderr)
runpy.run_path('_rebuild_tags.py', run_name='__main__')
