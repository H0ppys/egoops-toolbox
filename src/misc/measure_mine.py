"""把我画的水印缩到和参考图同尺寸，逐项量尺寸，和参考图对比，输出差异表。"""

import os

import numpy as np
from PIL import Image

REF = r"C:\Users\Administrator\.dsh\attachments\v1\objects\6c\6ccef35c990e989933fb24be8a8fa87ad2cccd69ca6e9a2bfd7c92f7245e7f36"


def measure(img, tag):
    a = np.array(img.convert("RGB"))
    h, w, _ = a.shape
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)

    yellow = (r > 200) & (g > 150) & (g < 245) & (b < 110)
    ys, xs = np.where(yellow)
    steel = (b > r + 8) & (b > 90) & (b < 235) & (r > 60)
    ys2, xs2 = np.where(steel)
    white = (r > 225) & (g > 225) & (b > 225)
    rows = white.sum(axis=1)

    runs, inrun, start = [], False, 0
    for y in range(h):
        if rows[y] > 3 and not inrun:
            start, inrun = y, True
        elif rows[y] <= 3 and inrun:
            runs.append((start, y - 1))
            inrun = False
    if inrun:
        runs.append((start, h - 1))

    out = {
        "w": w, "h": h,
        "yellow": (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else None,
        "steel": (xs2.min(), xs2.max(), ys2.min(), ys2.max()) if len(xs2) else None,
        "lines": runs,
    }
    print("[%s] %dx%d" % (tag, w, h))
    if out["yellow"]:
        x0, x1, y0, y1 = out["yellow"]
        print("  黄色: x %d-%d, y %d-%d (宽 %d)" % (x0, x1, y0, y1, x1 - x0))
    if out["steel"]:
        x0, x1, y0, y1 = out["steel"]
        print("  钢蓝: x %d-%d, y %d-%d (宽 %d, 高 %d)" % (x0, x1, y0, y1, x1 - x0, y1 - y0))
    print("  文字行:", [(s, e, e - s + 1) for s, e in runs])
    return out


def main():
    ref = Image.open(REF)
    r = measure(ref, "参考")

    mine = Image.open("docs/watermark-preview.png")
    # 缩放到参考宽度
    scale = ref.width / mine.width
    m = mine.resize((ref.width, int(mine.height * scale)), Image.LANCZOS)
    m.save("docs/watermark-mine-small.png")
    mm = measure(m, "我的（同宽）")

    print("\n== 相对宽度比例（占图宽%）==")
    def pct(v, w):
        return "%.2f%%" % (v * 100.0 / w)
    if r["yellow"] and mm["yellow"]:
        print("  黄色块宽: 参考 %s / 我的 %s" % (pct(r["yellow"][1] - r["yellow"][0], r["w"]),
                                            pct(mm["yellow"][1] - mm["yellow"][0], mm["w"])))
    if r["steel"] and mm["steel"]:
        print("  时间块宽: 参考 %s / 我的 %s" % (pct(r["steel"][1] - r["steel"][0], r["w"]),
                                            pct(mm["steel"][1] - mm["steel"][0], mm["w"])))


if __name__ == "__main__":
    main()
