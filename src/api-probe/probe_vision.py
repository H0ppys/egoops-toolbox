"""测哪个 Ark 模型能读图（vision）。"""
import os
import base64
import json
import urllib.error
import urllib.request

KEY = os.environ.get("ARK_API_KEY", "<FILL_ARK_API_KEY>")
BASE = "https://ark.cn-beijing.volces.com/api/v3"

# 拿一张真实的照片，缩到很小，减少 token
from PIL import Image

src = r"docs\media\photo.jpg"
img = Image.open(src)
img.thumbnail((512, 512))
buf = "sim/vision_probe.jpg"
img.convert("RGB").save(buf, quality=80)
b64 = base64.b64encode(open(buf, "rb").read()).decode()
print("图片大小:", len(b64) // 1024, "KB(base64)")

CANDIDATES = ["glm-5-2-260617", "doubao-seed-2-1-pro-260915", "doubao-seed-2-1-lite-260915",
              "deepseek-v4-1-flash-261017", "doubao-seed-2-0-mini-260428"]


def probe(model):
    body = json.dumps({
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图里是什么场景？只回答一句话。"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
            ],
        }],
        "max_tokens": 60,
    }).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
        return True, d["choices"][0]["message"]["content"].strip()[:80]
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            return False, "%s %s" % (e.code, err.get("error", {}).get("code", ""))
        except Exception:
            return False, str(e.code)
    except Exception as e:
        return False, type(e).__name__


for m in CANDIDATES:
    ok, info = probe(m)
    print(("✓" if ok else "✗"), m, "->", info)
