"""出带地图的最终效果图（用刚拿到的真实高德地图）。"""

import io
import sys
import urllib.request

sys.path.insert(0, "viewer")

from PIL import Image

import preview_final as P

KEY = "<FILL_ME>"


def fetch_map(lat=23.1291, lon=113.2644, px=320):
    url = ("https://restapi.amap.com/v3/staticmap?location=%s,%s&zoom=16&size=%d*%d"
           "&markers=mid,,A:%s,%s&key=%s" % (lon, lat, px, px, lon, lat, KEY))
    d = urllib.request.urlopen(url, timeout=20).read()
    open("docs/_map_live.png", "wb").write(d)
    return Image.open(io.BytesIO(d)).convert("RGB")


def main():
    src = Image.open("docs/_sample_photo.jpg").convert("RGB")
    w = 1080
    h = int(src.height * w / src.width)
    base = src.resize((w, h), Image.LANCZOS)

    m = fetch_map()
    img = P.draw(base.copy(), "广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园", map_img=m)
    img.save("docs/watermark-with-map.png")
    print("saved docs/watermark-with-map.png")


if __name__ == "__main__":
    main()
