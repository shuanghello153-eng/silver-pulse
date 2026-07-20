# -*- coding: utf-8 -*-
"""工人自校工具：写完 draft_#XXXX.json 后运行  python check_one.py draft_#XXXX.json
输出 PASS / FAIL(具体规则)，FAIL 则退出码 1。工人须自校到 PASS 再交。"""
import json, sys, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
VAL = os.path.join(HERE, "validator.py")
spec = importlib.util.spec_from_file_location('val', VAL)
val = importlib.util.module_from_spec(spec); spec.loader.exec_module(val)


def main():
    if len(sys.argv) < 2:
        print("用法: python check_one.py draft_#XXXX.json"); sys.exit(2)
    fp = sys.argv[1]
    if not os.path.exists(fp):
        print(f"文件不存在: {fp}"); sys.exit(2)
    dr = json.load(open(fp, encoding='utf-8'))
    tmp = {}
    for k in ('recommend', 'desc_cn', 'silver_reason', 'payor_model'):
        if k in dr:
            tmp[k] = dr[k]
    r = dr.get('recommend')
    if isinstance(r, dict):
        for sc in ('signal_strength', 'info_score', 'diff_score', 'copy_score', 'research_value'):
            if sc in r:
                tmp[sc] = r[sc]
    iss = val.validate(tmp)
    if iss:
        print('FAIL:', iss); sys.exit(1)
    print('PASS'); sys.exit(0)


if __name__ == '__main__':
    main()
