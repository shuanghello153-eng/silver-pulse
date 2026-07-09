# -*- coding: utf-8 -*-
"""
selection/relevance_screener.py — 阶段2 低模二筛（relevance_screener）

定位（见 产品方案 / 决策记录）：在 collector.is_relevant 初筛（宽进）之后，
再做一次「严出」二筛，拦掉初筛放行但实则与银发经济弱相关的噪音
（如泛健康 / 泛医疗 / 一般医院并购，无明确老年服务或产品指向）。

设计要点
--------
1. 模型抽象接口：ScreenerBackend 抽象基类。
   - RuleBasedBackend：零成本规则，默认启用（无 key 也能跑）。
   - LLMBackend：hy3 / DeepSeek 语义判断，需 API key；当前未配 -> 骨架预留
     call_llm() 接入点，config.ENABLE_LLM_SCREENER=False 时不启用。
2. 被拦文章写入 data/blocked_log.json（时间 / 标题 / 来源 / 原因 / 命中词），
   供人工抽检与「误杀」回溯。绝不删除原始数据，随时可回捞。
3. 自动校验：每次跑完抽查前 20 条被拦 + 前 20 条保留；若被拦项正文同时命中
   已知银发企业（疑似误杀）-> 打印 WARN，便于回收。
4. 接入 run_daily：run_daily_step() 在 config.ENABLE_RELEVANCE_SCREENER=True
   时调用；默认 False（无 key 不启用），仅产出骨架 + 可被独立 CLI 演练。

注意：本模块默认不写回、不删除 scored_latest.json 主数据；只有显式启用
（config 开关或 --enable）才会从主流程剔除被拦项，且原始条目仍留于
blocked_log.json。
"""
import os
import json
import re
from datetime import datetime, timezone

import config


# ---- 已知银发企业集合（用于「弱词 + 已知企业 = 相关」判定）----
def _load_known_enterprises():
    try:
        from enterprise_names import ENT_NAME_SET
        return ENT_NAME_SET or set()
    except Exception:
        return set()


KNOWN_ENT = _load_known_enterprises()


class ScreenerBackend:
    """二筛后端抽象接口。子类实现 screen(title, text, source) -> (relevant, reason)。"""

    def screen(self, title, text, source=""):
        raise NotImplementedError


class RuleBasedBackend(ScreenerBackend):
    """规则二筛：强词命中或已知企业命中 => 相关；否则 => 拦（泛健康 / 无老年上下文）。"""

    def __init__(self):
        self.strong = [k.lower() for k in getattr(config, "SILVER_STRONG_KEYWORDS", [])]
        self.irrelevant = [k.lower() for k in getattr(config, "IRRELEVANT_KEYWORDS", [])]
        self.known = KNOWN_ENT

    @staticmethod
    def _has(blob, kws):
        blob_l = blob.lower()
        for kw in kws:
            if kw and kw in blob_l:
                return kw
        return None

    def screen(self, title, text, source=""):
        blob = "%s %s" % (title or "", text or "")
        # 反向词（儿科 / 孕产等）双保险
        hit_irr = self._has(blob, self.irrelevant)
        if hit_irr:
            return False, "反向词命中:%s" % hit_irr
        # 已知银发企业 => 相关
        if self.known:
            blob_l = blob.lower()
            for name in self.known:
                if name and len(name) >= 2 and name.lower() in blob_l:
                    return True, "已知银发企业:%s" % name
        # 强词命中 => 相关
        hit_strong = self._has(blob, self.strong)
        if hit_strong:
            return True, "强词命中:%s" % hit_strong
        # 否则：初筛已放行的宽入口项，二筛判为弱相关
        return False, "无强银发词/已知企业命中(弱相关)"


class LLMBackend(ScreenerBackend):
    """模型语义二筛（骨架）。当前未接入真实 API —— call_llm 为预留接入点。

    启用条件：config.ENABLE_LLM_SCREENER=True 且配置 API key 环境变量
    （config.LLM_SCREENER_API_KEY_ENV，默认 SILVER_LLM_API_KEY）。
    未配置时 screen() 回退到 RuleBasedBackend，保证不中断流水线。
    """

    def __init__(self, backend=None):
        self.backend = backend or getattr(config, "LLM_SCREENER_BACKEND", "deepseek")
        self.api_key_env = getattr(config, "LLM_SCREENER_API_KEY_ENV", "SILVER_LLM_API_KEY")
        self.fallback = RuleBasedBackend()

    def call_llm(self, title, text):
        """预留：调用 hy3 / DeepSeek 做语义相关性判断。

        返回 (relevant: bool, reason: str)。未配置 key 时抛 NotImplementedError，
        由 screen() 捕获并回退规则后端。
        """
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise NotImplementedError("未配置 %s，LLM 二筛不可用" % self.api_key_env)
        # TODO(阶段4): 按 self.backend 构造请求（hy3 / DeepSeek），
        # prompt: 判断资讯是否直接面向老年人群 / 为老人提供产品·服务 / Medicare 用户。
        # 输入 title + summary，输出 JSON {"relevant": bool, "reason": str}。
        raise NotImplementedError("LLM 后端接入待实现（需 API key + 阶段4）")

    def screen(self, title, text, source=""):
        try:
            return self.call_llm(title, text)
        except NotImplementedError:
            # 无 key 或后端未实现 -> 回退规则，保证流水线不中断
            return self.fallback.screen(title, text, source)


def get_backend():
    if getattr(config, "ENABLE_LLM_SCREENER", False):
        return LLMBackend()
    return RuleBasedBackend()


# ---- 单条 / 批量 ----
def screen_article(art, backend=None):
    backend = backend or get_backend()
    title = art.get("title_cn") or art.get("title") or ""
    summary = art.get("summary_cn") or art.get("summary") or ""
    source = art.get("source") or art.get("source_name") or ""
    rel, reason = backend.screen(title, summary, source)
    return rel, reason


def _auto_audit(blocked, kept):
    """抽查前 20 条被拦 + 前 20 条保留，疑似误杀（被拦项命中已知企业）WARN。"""
    warns = []
    for art in blocked[:20]:
        title = (art.get("title_cn") or art.get("title") or "")
        blob = (title + " " + (art.get("summary_cn") or art.get("summary") or "")).lower()
        for name in KNOWN_ENT:
            if name and len(name) >= 3 and name.lower() in blob:
                warns.append((title[:40], name))
                break
    return warns


def run_daily_step(backend=None, write=True):
    """run_daily 钩子。ENABLE_RELEVANCE_SCREENER=False 时直接跳过（默认）。

    Returns: dict(enabled, checked, kept, blocked, miskill_warn, error?)
    """
    enabled = getattr(config, "ENABLE_RELEVANCE_SCREENER", False)
    if not enabled:
        print("[relevance_screener] 未启用(ENABLE_RELEVANCE_SCREENER=False)，跳过。")
        return {"enabled": False, "checked": 0, "kept": 0, "blocked": 0, "miscill_warn": []}
    backend = backend or get_backend()
    path = os.path.join(config.DATA_DIR, "scored_latest.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            arts = json.load(f)
    except Exception as e:
        print("[relevance_screener] 读取失败: %s" % e)
        return {"enabled": True, "error": str(e)}
    kept, blocked = [], []
    for art in arts:
        rel, reason = screen_article(art, backend)
        if rel:
            kept.append(art)
        else:
            b = dict(art)
            b["_block_reason"] = reason
            b["_blocked_at"] = datetime.now(timezone.utc).isoformat()
            blocked.append(b)
    # 写 blocked_log.json（追加式）
    if write and blocked:
        log_path = os.path.join(config.DATA_DIR, "blocked_log.json")
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = []
        for b in blocked:
            log.append({
                "title": b.get("title_cn") or b.get("title"),
                "source": b.get("source") or b.get("source_name"),
                "reason": b.get("_block_reason"),
                "blocked_at": b.get("_blocked_at"),
                "url": b.get("url"),
            })
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print("[relevance_screener] 已写 blocked_log.json: +%d 条(累计%d)" % (len(blocked), len(log)))
    # 自动校验：疑似误杀
    warns = _auto_audit(blocked, kept)
    print("[relevance_screener] 检查%d 保留%d 拦截%d" % (len(arts), len(kept), len(blocked)))
    if warns:
        print("[relevance_screener] ⚠ 疑似误杀(被拦但命中已知企业) %d 条，建议人工回捞：" % len(warns))
        for t, n in warns[:10]:
            print("   - %s  (命中的企业:%s)" % (t, n))
    # 写回：从主流程剔除被拦项（原始已留档 blocked_log）
    if write:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(kept, f, ensure_ascii=False, indent=2)
        print("[relevance_screener] 已更新 scored_latest.json（剔除%d条）" % len(blocked))
    return {"enabled": True, "checked": len(arts), "kept": len(kept),
            "blocked": len(blocked), "miskill_warn": warns}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="阶段2 低模二筛（relevance_screener）")
    ap.add_argument("--enable", action="store_true", help="无视 config 开关，强制执行二筛并写回")
    ap.add_argument("--dry-run", action="store_true", help="只扫描不写回（演练，不改动数据）")
    args = ap.parse_args()
    if args.enable:
        config.ENABLE_RELEVANCE_SCREENER = True
    be = get_backend()
    run_daily_step(backend=be, write=not args.dry_run)
