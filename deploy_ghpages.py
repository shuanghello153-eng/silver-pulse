#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy the built static site (output/) to the gh-pages branch via git plumbing.

Design notes
------------
- Builds an *orphan-friendly* commit that contains ONLY the built HTML/JSON at
  the branch root (GitHub Pages serves branch root). It never touches `main`,
  which is owned by the daily data automations.
- Uses git low-level commands (hash-object / mktree / commit-tree) so we don't
  need a worktree checkout of gh-pages and never risk clobbering main.
- A `.nojekyll` file is always included so GitHub serves every file verbatim
  (fixes the `weekly_topics.json` 404 that Jekyll would otherwise cause).
- `deploy()` is best-effort: callers should catch exceptions and keep going.
"""
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(REPO, "output")
FILES = ["index.html", "enterprise.html", "about.html", "weekly_topics.json"]


def _no_proxy_env():
    """Return a copy of the environment with proxy vars cleared.

    The automation host sets HTTPS_PROXY=http://127.0.0.1:7890, but that local
    proxy resets HTTPS tunnels to github.com (WinError 10054). Direct connections
    to github.com work fine, so we strip the proxy for all git ops here. Without
    NOTE: network posture is flaky — sometimes the direct path resets and the
    local proxy (127.0.0.1:7890) is required, sometimes the reverse. As of the
    current environment the proxy is the working path, so we KEEP proxy vars.
    """
    e = dict(os.environ)
    return e


def _run(cmd, input_text=None):
    """Run a git plumbing command; return stdout. Raise on non-zero exit."""
    res = subprocess.run(
        cmd,
        cwd=REPO,
        input=input_text,
        capture_output=True,
        text=True,
        env=_no_proxy_env(),
    )
    if res.returncode != 0:
        raise RuntimeError(
            "git command failed: %s\n%s" % (" ".join(cmd), res.stderr.strip())
        )
    return res.stdout


def deploy():
    """Build the gh-pages tree and force-push. Returns (ok: bool, message: str)."""
    # Ensure .nojekyll exists in output/
    noj = os.path.join(OUTPUT, ".nojekyll")
    if not os.path.exists(noj):
        open(noj, "w", encoding="utf-8").close()

    entries = []
    for fname in FILES + [".nojekyll"]:
        path = os.path.join(OUTPUT, fname)
        if not os.path.exists(path):
            print("[deploy] skip missing %s" % fname)
            continue
        blob = _run(["git", "hash-object", "-w", path]).strip()
        # tab-separated entries for mktree
        entries.append("100644 blob %s\t%s" % (blob, fname))

    if not entries:
        return False, "no build files found in output/"

    # Write mktree input to a temp file with EXPLICIT LF line endings.
    # (Passing via stdin on Windows can translate \n -> \r\n, which makes the
    # trailing \r part of each filename and breaks GitHub Pages serving.)
    tf_path = None
    try:
        fd, tf_path = tempfile.mkstemp(suffix=".mktree")
        with os.fdopen(fd, "wb") as tf:
            tf.write(("\n".join(entries) + "\n").encode("utf-8"))
        with open(tf_path, "rb") as tf:
            res = subprocess.run(
                ["git", "mktree"],
                cwd=REPO,
                stdin=tf,
                capture_output=True,
                text=True,
            )
        if res.returncode != 0:
            raise RuntimeError("git mktree failed: %s" % res.stderr.strip())
        tree = res.stdout.strip()
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)

    # Build on top of existing gh-pages if present (linear history), else orphan.
    parent = None
    try:
        parent = _run(["git", "rev-parse", "gh-pages"]).strip()
    except RuntimeError:
        parent = None

    msg = "deploy: Silver Pulse 银脉 site build (auto)"
    if parent:
        commit = _run(
            ["git", "commit-tree", tree, "-p", parent, "-m", msg]
        ).strip()
    else:
        commit = _run(["git", "commit-tree", tree, "-m", msg]).strip()

    _run(["git", "branch", "-f", "gh-pages", commit])
    # Push with retry — network resets (curl 35) are transient; retry up to 3×.
    import time
    last_err = None
    for attempt in range(1, 4):
        try:
            _run(["git", "push", "--force", "origin", "gh-pages"])
            return True, "pushed commit %s to gh-pages (attempt %d)" % (commit[:10], attempt)
        except RuntimeError as e:
            last_err = e
            print("[deploy] push attempt %d failed: %s" % (attempt, e))
            time.sleep(3)
    raise RuntimeError("git push failed after 3 attempts: %s" % last_err)


if __name__ == "__main__":
    try:
        ok, msg = deploy()
        print(("OK: " if ok else "FAIL: ") + msg)
        sys.exit(0 if ok else 1)
    except Exception as e:  # noqa: BLE001
        print("FAIL: %s" % e)
        sys.exit(1)
