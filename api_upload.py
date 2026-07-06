# -*- coding: utf-8 -*-
"""Upload key files to GitHub via Contents API (fallback when git push fails)."""
import base64, json, os, sys
import urllib.request, urllib.error

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "shuanghello153-eng"
REPO = "silver-pulse"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

FILES = [
    "index.html",
    "enterprise.html",
    "output/index.html",
    "output/enterprise.html",
    "data/scored_latest.json",
    "generator.py",
    "gen_enterprise.py",
]

def get_sha(path):
    url = f"{API_BASE}/{path}?ref={BRANCH}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
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
    req = urllib.request.Request(url, method="PUT")
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    req.data = json.dumps(body).encode()

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"  OK: {path} (sha: {result.get('content',{}).get('sha','?')[:7]})")
            return True
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode())
        print(f"  FAIL: {path} - {err.get('message','?')}")
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
