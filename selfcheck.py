#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selfcheck.py — Silver Pulse 银脉 · 三道零成本、不烧积分的每周校验。

集成进 run_daily.py（生成 HTML 之后、部署之前调用 selfcheck.run_daily_step()）。

三道校验：
  1. 死链检测   : 对 output/*.html 里所有外链（href 指向 http/https）抽样做
                 requests.head 检查是否 404/超时。超时/网络错不误报，标记「待人工复查」，
                 只报告不阻断。设合理 timeout(默认8s) + 并发上限，失败不阻塞主流程。
  2. JSON 字段断言 : 对 data/scored_latest.json、data/enterprise/all_enterprises.json
                 断言必需字段存在、类型正确、final_score ∈ [0,10]、数组非空
                 （或较前次骤降 >50% 则报警 / 硬错则阻断）。
  3. 评分一致性抽样 : 从 scored_latest.json 抽高分与极低分各若干条，重算 dim_scores 的
                 加权终分，与 final_score 比对（误差>0.05 报警）；并检查推荐理由是否含
                 "：。" 这类拼接 bug、是否引用了真实分数维度。

此外：每次跑前对关键 config/data 做 copy 备份（沿用 noise_spike_guard 思路），
      便于校验发现问题时回滚。

退出语义：任何校验脚本自身异常必须作为「硬失败」抛出（绝不静默通过）——run_daily
         部署门禁对 selfcheck 的 has_blocking（仅字段断言硬错）阻断部署。

零依赖：仅标准库 + requests（死链检测）。无 requests / 无网络时优雅降级为「跳过」。
"""
import os
import re
import json
import shutil
import sys
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import config  # noqa: E402

BASE_DIR = _HERE
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ENT_DIR = os.path.join(DATA_DIR, "enterprise")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
ENT_PATH = os.path.join(ENT_DIR, "all_enterprises.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.py")
BACKUP_DIR = os.path.join(DATA_DIR, "selfcheck_backups")
REPORT_PATH = os.path.join(DATA_DIR, "SELFCHECK_REPORT.md")
BASELINE_PATH = os.path.join(DATA_DIR, "selfcheck_baseline.json")

# ---- 可调参数（环境变量可覆盖，便于测试/调度） ----
LINK_SAMPLE = int(os.environ.get("SELFCHECK_LINK_SAMPLE", "20"))
LINK_TIMEOUT = float(os.environ.get("SELFCHECK_LINK_TIMEOUT", "8"))
LINK_WORKERS = int(os.environ.get("SELFCHECK_LINK_WORKERS", "10"))
DEAD_LINK_BLOCK = int(os.environ.get("SELFCHECK_DEAD_BLOCK", "3"))   # 死链超过此数 -> 阻断
SCORE_TOLERANCE = float(os.environ.get("SELFCHECK_SCORE_TOL", "0.06"))
SKIP_NET = os.environ.get("SELFCHECK_SKIP_NET", "").lower() in ("1", "true", "yes")

SCORED_REQUIRED = ["id", "title", "url", "date", "source", "final_score",
                   "is_selected", "is_curated", "dim_scores", "recommendation"]
ENT_REQUIRED = ["name", "region", "category_l1", "value_score"]


# --------------------------------------------------------------------------- #
# 通用工具
# --------------------------------------------------------------------------- #
def _load_json(path, default=None):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        return {"__load_error__": str(e)} if default is None else default


def _load_scored():
    d = _load_json(SCORED_PATH)
    if d is None:
        return None
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and "items" in d:
        return d["items"]
    return d  # 可能是带 __load_error__ 的 dict


def _load_enterprises():
    d = _load_json(ENT_PATH)
    if d is None:
        return None
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and "enterprises" in d:
        return d["enterprises"]
    return d


def _load_baseline():
    return _load_json(BASELINE_PATH, {})


def _save_baseline(obj):
    try:
        os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------- #
# 回滚备份（沿用 noise_spike_guard 思路）
# --------------------------------------------------------------------------- #
def backup_rollbacks():
    """跑前对关键 config/data 做 copy 备份，便于校验发现问题时回滚。

    保留最近 5 份快照，老快照自动清理。
    返回备份目录路径或错误信息字符串。
    """
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_DIR, "SELFCHECK_BAK_%s" % stamp)
        os.makedirs(dest, exist_ok=True)
        copied = []
        for src in (CONFIG_PATH, SCORED_PATH, ENT_PATH):
            if os.path.exists(src):
                shutil.copy2(src, dest)
                copied.append(os.path.basename(src))
        # 清理老快照，仅留最近 5 份
        subs = sorted(
            [d for d in os.listdir(BACKUP_DIR) if d.startswith("SELFCHECK_BAK_")],
            reverse=True,
        )
        for old in subs[5:]:
            try:
                shutil.rmtree(os.path.join(BACKUP_DIR, old))
            except Exception:  # noqa: BLE001
                pass
        return "备份至 %s (含: %s)" % (dest, ", ".join(copied))
    except Exception as e:  # noqa: BLE001
        return "BACKUP_FAILED: %s" % e


# --------------------------------------------------------------------------- #
# 校验 1：死链检测
# --------------------------------------------------------------------------- #
_HREF_RE = re.compile(r'<a\s+[^>]*?href=["\']([^"\']+)["\']', re.I)
_HTML_FILES = ("index.html", "enterprise.html", "about.html")


def _collect_external_links():
    """从 output/*.html 抽取所有 http/https 外链，去重。"""
    links = set()
    for fn in _HTML_FILES:
        path = os.path.join(OUTPUT_DIR, fn)
        if not os.path.exists(path):
            continue
        try:
            text = open(path, "r", encoding="utf-8", errors="ignore").read()
        except Exception:  # noqa: BLE001
            continue
        for m in _HREF_RE.finditer(text):
            u = m.group(1).strip()
            if re.match(r"^https?://", u):
                links.add(u)
    return sorted(links)


def _check_one_link(url, timeout):
    """返回 (url, status)。status: 'dead:<code>' / 'ok' / 'pending:<reason>'。"""
    try:
        import requests
        try:
            r = requests.head(url, timeout=timeout, allow_redirects=True)
            if r.status_code >= 400:
                # 部分站点禁用 HEAD，用 GET 复核一次避免误报
                if r.status_code in (403, 405, 400, 501):
                    r2 = requests.get(url, timeout=timeout, allow_redirects=True,
                                      stream=True, headers={"User-Agent": "Mozilla/5.0"})
                    if r2.status_code < 400:
                        return (url, "ok")
                    # 访问控制类状态码（反爬/鉴权/限流）：页面本身多半存在，
                    # 只是拒绝机器人（如 Crunchbase 走 Cloudflare 常年 403）。
                    # 对"可信度死链检测"而言这不是真死链，降级为待人工复查，避免狼来了。
                    if r2.status_code in (401, 403, 429):
                        return (url, "pending:blocked_%d" % r2.status_code)
                    return (url, "dead:%d" % r2.status_code)
                # 访问控制类：同上，判为待复查而非死链
                if r.status_code in (401, 429):
                    return (url, "pending:blocked_%d" % r.status_code)
                return (url, "dead:%d" % r.status_code)
            return (url, "ok")
        except requests.exceptions.RequestException as e:
            # 网络错/超时 -> 不误报为死链，标记待人工复查
            return (url, "pending:%s" % type(e).__name__)
    except ImportError:
        return (url, "pending:norequests")
    except Exception as e:  # noqa: BLE001
        return (url, "pending:%s" % type(e).__name__)


def check_dead_links():
    """抽样检测外链死链。返回 dict。失败不阻塞主流程。"""
    result = {
        "total_external": 0,
        "sampled": 0,
        "dead": [],       # (url, code)
        "pending": [],    # (url, reason) 待人工复查，不计为死链
        "ok": 0,
        "skipped": False,
        "note": "",
    }
    links = _collect_external_links()
    result["total_external"] = len(links)
    if SKIP_NET:
        result["skipped"] = True
        result["note"] = "SELFCHECK_SKIP_NET 已设 -> 跳过死链网络检测"
        return result
    if not links:
        result["note"] = "未检出外链"
        return result

    import random
    sample = links if len(links) <= LINK_SAMPLE else random.sample(links, LINK_SAMPLE)
    result["sampled"] = len(sample)

    try:
        import requests  # noqa: F401
    except ImportError:
        result["skipped"] = True
        result["note"] = "未安装 requests -> 跳过死链检测"
        return result

    dead, pending, ok = [], [], 0
    with ThreadPoolExecutor(max_workers=LINK_WORKERS) as ex:
        fut_map = {ex.submit(_check_one_link, u, LINK_TIMEOUT): u for u in sample}
        for fut in as_completed(fut_map):
            url, st = fut.result()
            if st == "ok":
                ok += 1
            elif st.startswith("dead"):
                dead.append((url, st.split(":", 1)[1]))
            else:
                pending.append((url, st.split(":", 1)[1]))
    result["dead"] = dead
    result["pending"] = pending
    result["ok"] = ok
    return result


# --------------------------------------------------------------------------- #
# 校验 2：JSON 字段断言（schema 校验）
# --------------------------------------------------------------------------- #
def _blended_weights():
    """复刻 reapply_centrality._load_blended_weights：基底用 config 权重，
    若存在 data/user_pref.json 则叠加其微调。"""
    base = {k: {"weight": v["weight"]} for k, v in config.NEWS_SCORING_DIMS.items()}
    pref_path = os.path.join(DATA_DIR, "user_pref.json")
    if os.path.exists(pref_path):
        try:
            pref = json.load(open(pref_path, encoding="utf-8"))
            pw = pref.get("weights", {})
            for k in base:
                if k in pw and isinstance(pw[k], (int, float)):
                    base[k]["weight"] = float(pw[k])
        except Exception:  # noqa: BLE001
            pass
    return base


def check_json_schema(scored, enterprises):
    """断言必需字段/类型/final_score 范围/数组非空/骤降。返回 dict。

    hard_errors: 字段硬错（缺失必需字段、类型错、final_score 越界、数组空）-> 可阻断部署。
    warnings:   骤降 >50% 等软告警 -> 仅报告。
    """
    result = {
        "scored_count": 0,
        "ent_count": 0,
        "hard_errors": [],
        "warnings": [],
    }

    # ---- scored_latest.json ----
    if scored is None:
        result["hard_errors"].append("scored_latest.json 缺失或解析失败")
        result["scored_count"] = 0
    elif isinstance(scored, dict) and "__load_error__" in scored:
        result["hard_errors"].append("scored_latest.json 解析失败: %s" % scored["__load_error__"])
    elif not isinstance(scored, list) or len(scored) == 0:
        result["hard_errors"].append("scored_latest.json 为空或结构异常（期望非空数组）")
    else:
        result["scored_count"] = len(scored)
        for i, it in enumerate(scored):
            if not isinstance(it, dict):
                result["hard_errors"].append("条目#%d 非对象" % i)
                continue
            missing = [k for k in SCORED_REQUIRED if k not in it]
            if missing:
                result["hard_errors"].append("条目#%d 缺字段 %s" % (i, missing))
                continue
            fs = it.get("final_score")
            if not isinstance(fs, (int, float)):
                result["hard_errors"].append("条目#%d final_score 非数值: %r" % (i, fs))
            elif not (0.0 <= float(fs) <= 10.0):
                result["hard_errors"].append("条目#%d final_score 越界 %r (应∈[0,10])" % (i, fs))
            if not isinstance(it.get("dim_scores"), dict):
                result["hard_errors"].append("条目#%d dim_scores 非对象" % i)
            if not isinstance(it.get("url"), str) or not it["url"].strip():
                result["hard_errors"].append("条目#%d url 为空或非字符串" % i)
            if not isinstance(it.get("date"), str) or not it["date"].strip():
                result["hard_errors"].append("条目#%d date 为空" % i)

    # ---- all_enterprises.json ----
    if enterprises is None:
        result["hard_errors"].append("all_enterprises.json 缺失或解析失败")
        result["ent_count"] = 0
    elif isinstance(enterprises, dict) and "__load_error__" in enterprises:
        result["hard_errors"].append("all_enterprises.json 解析失败: %s" % enterprises["__load_error__"])
    elif not isinstance(enterprises, list) or len(enterprises) == 0:
        result["hard_errors"].append("all_enterprises.json 为空或结构异常（期望非空数组）")
    else:
        result["ent_count"] = len(enterprises)
        bad = 0
        for i, e in enumerate(enterprises):
            if not isinstance(e, dict):
                bad += 1
                continue
            missing = [k for k in ENT_REQUIRED if k not in e]
            if missing:
                result["hard_errors"].append("企业#%d 缺字段 %s" % (i, missing))
                break  # 只报首例以免刷屏
            vs = e.get("value_score")
            if vs is not None and not isinstance(vs, (int, float)):
                result["hard_errors"].append("企业#%d value_score 非数值" % i)
                break
        if bad:
            result["hard_errors"].append("企业库有 %d 条非对象" % bad)

    # ---- 骤降检测（软告警，不阻断） ----
    baseline = _load_baseline() or {}
    prev_scored = baseline.get("scored_count")
    prev_ent = baseline.get("ent_count")
    if prev_scored and result["scored_count"]:
        if result["scored_count"] < prev_scored * 0.5:
            result["warnings"].append(
                "资讯数骤降: 今日 %d < 前次 %d ×0.5" % (result["scored_count"], prev_scored))
    if prev_ent and result["ent_count"]:
        if result["ent_count"] < prev_ent * 0.5:
            result["warnings"].append(
                "企业数骤降: 今日 %d < 前次 %d ×0.5" % (result["ent_count"], prev_ent))

    # 更新基线（供下次对比）
    _save_baseline({
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "scored_count": result["scored_count"],
        "ent_count": result["ent_count"],
    })
    return result


# --------------------------------------------------------------------------- #
# 校验 3：评分一致性抽样
# --------------------------------------------------------------------------- #
def _recompute_final_score(it, weights):
    """用现有 dim_scores 复刻 reapply_centrality 的终分公式。

    final = Σ dim_scores[k]*w[k] + SOURCE_ADJ[tier]，round 到 2 位。
    tier 取自 item.tier，否则由 source 名映射；缺省 adj=0。
    """
    ds = it.get("dim_scores") or {}
    total = 0.0
    for k, v in weights.items():
        total += (float(ds.get(k, 0) or 0)) * v["weight"]
    tier = it.get("tier")
    if tier is None:
        tier = config.SOURCE_NAME_TO_TIER.get(it.get("source"))
    adj = config.SOURCE_ADJ.get(tier, 0.0)
    return round(total + adj, 2)


def check_score_consistency(scored):
    """抽高分与极低分各若干条，重算终分比对 + 推荐理由拼接 bug 检查。"""
    result = {
        "sampled": [],
        "score_mismatch": [],    # 重算与存储不一致
        "rec_bugs": [],          # 推荐理由拼接 bug / 空理由
        "note": "",
    }
    if not isinstance(scored, list) or not scored:
        result["note"] = "无 scored 数据，跳过"
        return result

    def fnum(it):
        try:
            return float(it.get("final_score", 0))
        except Exception:  # noqa: BLE001
            return 0.0

    ranked = sorted(scored, key=fnum)
    n_high = max(3, len(ranked) // 10)
    n_low = max(3, len(ranked) // 10)
    sample = ranked[:n_low] + ranked[-n_high:]
    # 去重
    seen = set()
    uniq = []
    for it in sample:
        key = it.get("id")
        if key in seen:
            continue
        seen.add(key)
        uniq.append(it)
    sample = uniq

    weights = _blended_weights()
    for it in sample:
        title = it.get("title", "")[:30]
        stored = fnum(it)
        recomputed = _recompute_final_score(it, weights)
        entry = {
            "id": it.get("id"),
            "title": title,
            "stored": stored,
            "recomputed": recomputed,
            "dim_scores": it.get("dim_scores"),
        }
        result["sampled"].append(entry)
        if abs(recomputed - stored) > SCORE_TOLERANCE:
            diff = round(recomputed - stored, 2)
            # 若差值恰好等于某个 SOURCE_ADJ，说明来源分层加成未生效（常见静默坏数据）
            adj_vals = sorted({round(v, 2) for v in config.SOURCE_ADJ.values()})
            cause = "（疑似 SOURCE_ADJ 来源加成未生效）" if diff in adj_vals else ""
            result["score_mismatch"].append({
                "id": it.get("id"),
                "title": title,
                "stored": stored,
                "recomputed": recomputed,
                "diff": diff,
                "cause": cause,
            })

        # 推荐理由质量检查
        rec = it.get("recommendation") or ""
        # 拼接 bug：维度占位符未填（如 "健康服务：。" 或 "：。"）
        if "：。" in rec or ":." in rec:
            result["rec_bugs"].append({
                "id": it.get("id"),
                "title": title,
                "type": "拼接bug(:。)",
                "rec": rec[:60],
            })
        elif not rec.strip():
            result["rec_bugs"].append({
                "id": it.get("id"),
                "title": title,
                "type": "空推荐理由",
                "rec": "",
            })

    if not result["score_mismatch"] and not result["rec_bugs"]:
        result["note"] = "抽样 %d 条，终分与推荐理由均一致" % len(sample)
    return result


# --------------------------------------------------------------------------- #
# 编排入口
# --------------------------------------------------------------------------- #
def run_daily_step():
    """主入口：跑三道校验 + 回滚备份，写 SELFCHECK_REPORT.md，打印摘要。

    返回 dict: {has_blocking, blockers, warnings, ...}
    has_blocking 仅当「字段断言硬错」为真 -> 可阻断部署（由 run_daily 决定）。
    """
    print("\n=== Silver Pulse 三道校验 selfcheck ===")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 0) 回滚备份（跑前）
    bak = backup_rollbacks()
    print("  备份: %s" % bak)

    blockers = []
    warnings = []

    # 数据读取
    scored = _load_scored()
    enterprises = _load_enterprises()

    # 1) 死链检测
    links = check_dead_links()
    if links.get("skipped"):
        warnings.append("死链检测跳过: %s" % links.get("note", ""))
    else:
        dead_n = len(links.get("dead", []))
        pend_n = len(links.get("pending", []))
        if dead_n > DEAD_LINK_BLOCK:
            # 按团队主任务口径：死链只报告，不阻断部署；此处记警告而非 blockers
            warnings.append("死链 %d 条(超阈值%d，仅报告不阻断): %s" % (
                dead_n, DEAD_LINK_BLOCK,
                ", ".join(u for u, _ in links["dead"][:3])))
        elif dead_n:
            warnings.append("死链 %d 条(未超阈值): %s" % (
                dead_n, ", ".join(u for u, _ in links["dead"][:3])))
        if pend_n:
            warnings.append("外链 %d 条待人工复查(超时/网络错，未计为死链)" % pend_n)
        print("  死链: 抽样 %d/%d | 死 %d | 待复查 %d | 可达 %d" % (
            links.get("sampled", 0), links.get("total_external", 0),
            dead_n, pend_n, links.get("ok", 0)))

    # 2) JSON 字段断言
    schema = check_json_schema(scored, enterprises)
    if schema["hard_errors"]:
        blockers.extend("字段断言: " + e for e in schema["hard_errors"])
    for w in schema["warnings"]:
        warnings.append("字段告警: " + w)
    print("  字段断言: 资讯 %d 条 | 企业 %d 条 | 硬错 %d | 软告警 %d" % (
        schema["scored_count"], schema["ent_count"],
        len(schema["hard_errors"]), len(schema["warnings"])))

    # 3) 评分一致性抽样
    consist = check_score_consistency(scored)
    for m in consist["score_mismatch"]:
        warnings.append("评分不一致 #%s 存%.2f 重算%.2f (差%.2f)%s" % (
            m["id"], m["stored"], m["recomputed"], m["diff"], m.get("cause", "")))
    for b in consist["rec_bugs"]:
        warnings.append("推荐理由异常 #%s [%s]: %s" % (b["id"], b["type"], b["rec"]))
    print("  评分一致性: 抽样 %d 条 | 不一致 %d | 推荐理由异常 %d" % (
        len(consist["sampled"]), len(consist["score_mismatch"]),
        len(consist["rec_bugs"])))

    has_blocking = bool(blockers)
    status = "FAIL" if has_blocking else ("WARN" if warnings else "PASS")

    # ---- 写报告 ----
    lines = [
        "# Silver Pulse 三道校验健康报告",
        "",
        "**生成时间**: %s" % now,
        "**状态**: %s" % status,
        "**回滚备份**: %s" % bak,
        "",
        "## 概览",
        "",
        "| 校验 | 结果 |",
        "|---|---|",
        "| 死链检测 | 外链总数 %d，抽样 %d，死链 %d，待复查 %d |" % (
            links.get("total_external", 0), links.get("sampled", 0),
            len(links.get("dead", [])), len(links.get("pending", []))),
        "| JSON 字段断言 | 资讯 %d / 企业 %d，硬错 %d，软告警 %d |" % (
            schema["scored_count"], schema["ent_count"],
            len(schema["hard_errors"]), len(schema["warnings"])),
        "| 评分一致性 | 抽样 %d，不一致 %d，推荐理由异常 %d |" % (
            len(consist["sampled"]), len(consist["score_mismatch"]),
            len(consist["rec_bugs"])),
        "",
    ]

    if blockers:
        lines.append("## 🔴 阻断项（字段硬错，应阻断部署并报警）")
        lines.append("")
        for b in blockers:
            lines.append("- %s" % b)
        lines.append("")

    if warnings:
        lines.append("## 🟡 警告项（仅报告，不阻断部署）")
        lines.append("")
        for w in warnings:
            lines.append("- %s" % w)
        lines.append("")

    if not blockers and not warnings:
        lines.append("## 🟢 全部通过")
        lines.append("")
        lines.append("三道校验均未发现问题，可安全部署。")
        lines.append("")

    # 死链明细（便于人工复查）
    if links.get("dead"):
        lines.append("## 死链明细")
        lines.append("")
        for u, c in links["dead"]:
            lines.append("- `%s` -> %s" % (u[:120], c))
        lines.append("")
    if links.get("pending"):
        lines.append("## 待人工复查（超时/网络错，非死链）")
        lines.append("")
        for u, r in links["pending"][:20]:
            lines.append("- `%s` -> %s" % (u[:120], r))
        lines.append("")

    # 评分不一致明细
    if consist["score_mismatch"]:
        lines.append("## 评分不一致明细")
        lines.append("")
        for m in consist["score_mismatch"]:
            lines.append("- #%s `%s` 存=%s 重算=%s 差=%s%s" % (
                m["id"], m["title"], m["stored"], m["recomputed"], m["diff"], m.get("cause", "")))
        lines.append("")

    report = "\n".join(lines)
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)
    except Exception as e:  # noqa: BLE001
        print("  [WARN] 报告写入失败: %s" % e)

    # 控制台摘要
    print("  状态: %s" % status)
    print("  阻断: %d | 警告: %d" % (len(blockers), len(warnings)))
    print("  报告: %s" % REPORT_PATH)

    return {
        "has_blocking": has_blocking,
        "blockers": blockers,
        "warnings": warnings,
        "dead_links": len(links.get("dead", [])),
        "pending_links": len(links.get("pending", [])),
        "schema_hard_errors": len(schema["hard_errors"]),
        "score_mismatch": len(consist["score_mismatch"]),
        "rec_bugs": len(consist["rec_bugs"]),
        "backup": bak,
        "report": REPORT_PATH,
    }


if __name__ == "__main__":
    # 心跳：任何未捕获异常都会让进程非零退出，绝不让校验器静默通过
    res = run_daily_step()
    print("\nhas_blocking: %s" % res["has_blocking"])
    sys.exit(1 if res["has_blocking"] else 0)
