"""拿真实采集照片，按 v61 的参数把水印画上去，出前后对比图。"""

import io
import os
import sys

sys.path.insert(0, "viewer")

from PIL import Image

import tls
import urllib.request
import urllib.parse

import watermark_preview7 as W

BASE = "https://<FILL_ME>/relay"


def fetch_photo():
    # 登录拿 token
    body = io.BytesIO()
    import json
    data = json.dumps({"name": "预览"}).encode()
    req = urllib.request.Request(BASE + "/api/login", data=data,
                                 headers={"Content-Type": "application/json"})
    tok = json.loads(tls.urlopen(req, timeout=20).read()).get("token", "")

    req = urllib.request.Request(BASE + "/api/sites", headers={"Authorization": "Bearer " + tok})
    sites = json.loads(tls.urlopen(req, timeout=20).read())
    sites = sites.get("sites") or sites.get("items") or sites
    for s in sites:
        req = urllib.request.Request(BASE + "/api/sites/" + s["id"],
                                     headers={"Authorization": "Bearer " + tok})
        d = json.loads(tls.urlopen(req, timeout=20).read())
        for t in d.get("tasks") or []:
            for f in t.get("photos") or []:
                url = BASE + "/files/" + f["id"]
                r = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
                raw = tls.urlopen(r, timeout=60).read()
                path = "docs/_sample_photo.jpg"
                io.open(path, "wb").write(raw)
                print("取到照片:", f["filename"], len(raw) // 1024, "KB")
                return path
    return None


def main():
    path = fetch_photo()
    if not path:
        print("没取到照片")
        return

    src = Image.open(path).convert("RGB")
    print("照片尺寸:", src.size)

    # 原图缩到 1080 宽（模拟手机画质）
    w = 1080
    h = int(src.height * w / src.width)
    photo = src.resize((w, h), Image.LANCZOS)

    before = photo.copy()
    after = W.draw_stamp(photo.copy())

    gap = 24
    out = Image.new("RGB", (w * 2 + gap, h), "#111111")
    out.paste(before, (0, 0))
    out.paste(after, (w + gap, 0))
    out.save("docs/watermark-real-compare.png")

    after.save("docs/watermark-real.png")
    print("saved docs/watermark-real-compare.png", out.size)


if __name__ == "__main__":
    main()
