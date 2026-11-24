"""试探这个 key 能用哪个接口 + 哪个模型名（只看是否 200 且返回文本）。"""
import os
import json
import urllib.error
import urllib.request

KEY = os.environ.get("ARK_API_KEY", "<FILL_ARK_API_KEY>")

CANDIDATES = [
    ("https://ark.cn-beijing.volces.com/api/v3", "glm-4.5-flash"),
    ("https://ark.cn-beijing.volces.com/api/v3", "glm-5.3-flash"),
    ("https://ark.cn-beijing.volces.com/api/v3", "glm-4.6"),
    ("https://ark.cn-beijing.volces.com/api/v3", "doubao-seed-1-6-flash-250615"),
    ("https://open.bigmodel.cn/api/paas/v4", "glm-4.5-flash"),
]


def probe(base, model):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "只回复两个字：可用"}],
        "max_tokens": 16,
    }).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode())
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return True, text.strip()[:40]
    except urllib.error.HTTPError as e:
        return False, "%s %s" % (e.code, e.read().decode()[:160].replace("\n", " "))
    except Exception as e:
        return False, str(e)[:120]


for base, model in CANDIDATES:
    ok, info = probe(base, model)
    print(("✓" if ok else "✗"), base.split("//")[1].split("/")[0], model, "->", info)
