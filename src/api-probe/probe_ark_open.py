"""看这个 Ark 账号开通了哪些 chat 模型。"""
import os
import json
import urllib.error
import urllib.request

KEY = os.environ.get("ARK_API_KEY", "<FILL_ARK_API_KEY>")
BASE = "https://ark.cn-beijing.volces.com/api/v3"

CANDIDATES = [
    "glm-5-3-flash-260828",
    "glm-5-2-260617",
    "glm-4-5-air-20250728",
    "deepseek-v4-1-flash-261017",
    "deepseek-v4-1-flash-260910",
    "deepseek-v4-flash-ga-260731",
    "doubao-seed-2-1-lite-260915",
    "doubao-seed-2-0-mini-260428",
    "qwen3-32b-20250429",
]


def try_model(m):
    body = json.dumps({"model": m, "messages": [{"role": "user", "content": "回复：可用"}],
                       "max_tokens": 8}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            d = json.loads(r.read().decode())
        return True, d["choices"][0]["message"].get("content", "").strip()[:20]
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            return False, "%s %s" % (e.code, err.get("error", {}).get("code", ""))
        except Exception:
            return False, str(e.code)
    except Exception as e:
        return False, type(e).__name__


ok_models = []
for m in CANDIDATES:
    ok, info = try_model(m)
    print(("✓" if ok else "✗"), m, "->", info)
    if ok:
        ok_models.append(m)

print("\n可用:", ok_models)
