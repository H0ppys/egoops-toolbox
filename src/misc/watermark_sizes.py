"""缩小水印：按 F 值给出三档效果，选定后写进 App。"""

import io
import os
import sys

sys.path.insert(0, "viewer")

from PIL import Image

import watermark_preview7 as W


def stamp(photo, F):
    old = W.__dict__.get("_F_OVERRIDE")
    W.__dict__["F_OVERRIDE"] = F
    return photo


def main():
    src = Image.open("docs/_sample_photo.jpg").convert("RGB")
    w = 900
    h = int(src.height * w / src.width)
    base = src.resize((w, h), Image.LANCZOS)

    # 用模块里的函数，但改 F 值：直接调用内部实现
    import types

    variants = []
    for F in (46, 42, 38):
        mod = types.ModuleType("wm")
        code = io.open("tools/watermark_preview7.py", encoding="utf-8").read()
        code = code.replace("    F = 50 * u", "    F = %d * u" % F)
        exec(compile(code, "wm", "exec"), mod.__dict__)
        img = mod.draw_stamp(base.copy())
        variants.append((F, img))

    gap = 16
    out = Image.new("RGB", (w * 3 + gap * 2, h + 40), "#0A0A0A")
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 26)
    except Exception:
        f = ImageFont.load_default()
    for i, (F, img) in enumerate(variants):
        x = i * (w + gap)
        out.paste(img, (x, 40))
        d.text((x + 12, 8), "字号 F=%d" % F, font=f, fill="#FFFFFF")
    out.save("docs/watermark-size-options.png")
    print("saved docs/watermark-size-options.png")


if __name__ == "__main__":
    main()
