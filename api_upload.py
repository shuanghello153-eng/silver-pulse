# -*- coding: utf-8 -*-
"""Upload key files to GitHub via Contents API (fallback when git push fails).

NOTE: switched the HTTP layer from `urllib` to `requests` because on the
Windows automation host `urllib` ignores the HTTPS_PROXY env var and the
direct TLS connection to api.github.com is reset (SSL EOF). `requests`
correctly honors the proxy and the token auth, so unattended daily deploys
succeed. Logic / file set / output format unchanged.
"""
import base64, json, os, sys

import requests

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "shuanghello153-eng"
REPO = "silver-pulse"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

# Honor proxy env vars (HTTPS_PROXY/HTTP_PROXY) if present; requests reads them
# automatically, but be explicit so it works regardless of urllib behaviour.
_PROXIES = {}
for _k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
    if os.environ.get(_k):
        _PROXIES["https" if _k.lower().startswith("https") else "http"] = os.environ[_k]
_HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

FILES = [
    "index.html",
    "enterprise.html",
    "about.html",
    "output/index.html",
    "output/enterprise.html",
    "output/about.html",
    "data/scored_latest.json",
    "data/enterprise/all_enterprises.json",
    "generator.py",
    "gen_enterprise.py",
    "gen_about.py",
    "config.py",
    "merge_v2.py",
]

def get_sha(path):
    url = f"{API_BASE}/{path}?ref={BRANCH}"
    try:
        r = requests.get(url, headers=_HEADERS, proxies=_PROXIES or None, timeout=60)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("sha")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise

def upload_file(path, content_bytes):
    sha = get_sha(path)
    body = {
        "message": f"daily update {path}",
        "content": base64.b64encode(content_bytes).decode("ascii"),
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha

    url = f"{API_BASE}/{path}"
    try:
        r = requests.put(
            url,
            headers={**_HEADERS, "Content-Type": "application/json"},
            data=json.dumps(body).encode(),
            proxies=_PROXIES or None,
            timeout=60,
        )
        r.raise_for_status()
        result = r.json()
        print(f"  OK: {path} (sha: {result.get('content', {}).get('sha', '?')[:7]})")
        return True
    except requests.HTTPError as e:
        msg = "?"
        try:
            msg = e.response.json().get("message", "?")
        except Exception:
            pass
        print(f"  FAIL: {path} - {msg}")
        return False

base_dir = os.path.dirname(os.path.abspath(__file__))
success = 0
fail = 0

for f in FILES:
    filepath = os.path.join(base_dir, f)
    if not os.path.exists(filepath):
        print(f"  SKIP: {f} (not found)")
        continue
    with open(filepath, "rb") as fh:
        content = fh.read()
    if upload_file(f, content):
        success += 1
    else:
        fail += 1

print(f"\nDone: {success} uploaded, {fail} failed")
