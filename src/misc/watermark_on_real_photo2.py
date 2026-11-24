"""用 Api 登录 token 下载一张真实照片，然后画水印做对比图。"""

import io
import os
import sys

sys.path.insert(0, "viewer")

import urllib.request
from PIL import Image

import tls
import watermark_preview7 as W
from api import Api

BASE = "https://<FILL_ME>/relay"


def fetch():
    a = Api(BASE)
    a.login("预览")
    tok = getattr(a, "token", "")
    s = [x for x in a.sites() if x["name"] == "盛宴公寓"][0]
    d = a.site(s["id"])
    f = d["tasks"][0]["photos"][0]
    req = urllib.request.Request(BASE + "/files/" + f["id"])
    req.add_header("Authorization", "Bearer " + tok)
    raw = tls.urlopen(req, timeout=60).read()
    io.open("docs/_sample_photo.jpg", "wb").write(raw)
    print("取到:", f["filename"], len(raw) // 1024, "KB")
    return "docs/_sample_photo.jpg"


def main():
    if not os.path.exists("docs/_sample_photo.jpg"):
        fetch()
    src = Image.open("docs/_sample_photo.jpg").convert("RGB")
    print("原始尺寸:", src.size)

    w = 1080
    h = int(src.height * w / src.width)
    photo = src.resize((w, h), Image.LANCZOS)

    before = photo.copy()
    after = W.draw_stamp(photo.copy())

    gap = 20
    out = Image.new("RGB", (w * 2 + gap, h), "#0A0A0A")
    out.paste(before, (0, 0))
    out.paste(after, (w + gap, 0))
    out.save("docs/watermark-real-compare.png")
    after.save("docs/watermark-real.png")
    print("saved", out.size)


if __name__ == "__main__":
    main()
