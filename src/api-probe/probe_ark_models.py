"""列出 Ark 可用模型（或试一批候选 id）。"""
import os
import json
import urllib.error
import urllib.request

KEY = os.environ.get("ARK_API_KEY", "<FILL_ARK_API_KEY>")
BASE = "https://ark.cn-beijing.volces.com/api/v3"


def get(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()[:1000]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


print("GET /models ->", get("/models"))

CANDIDATES = [
    "doubao-seed-1-6-flash-250828",
    "doubao-seed-1-6-250615",
    "doubao-1-5-lite-32k-250115",
    "doubao-1-5-pro-32k-250115",
    "deepseek-v3-250324",
    "deepseek-r1-250528",
    "kimi-k2-250711",
    "glm-4-5",
    "glm-4-5-flash",
    "GLM-4.5-Flash",
]

for m in CANDIDATES:
    body = json.dumps({"model": m, "messages": [{"role": "user", "content": "回复：可用"}],
                       "max_tokens": 8}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
        print("✓", m, "->", d["choices"][0]["message"]["content"].strip()[:20])
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:120].replace("\n", " ")
        print("✗", m, "->", e.code, msg)
