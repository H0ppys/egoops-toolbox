"""按实测比例重排（第五版）：
   参考图 344 宽量得：地址字高 14px、徽章高 32px、行距 20px、日期偏移 26px、底部偏移 26px
   折算成 F（地址字号）= 50u 时的比例。
"""

import os

from PIL import Image, ImageDraw, ImageFont

REF = r"C:\Users\Administrator\.dsh\attachments\v1\objects\6c\6ccef35c990e989933fb24be8a8fa87ad2cccd69ca6e9a2bfd7c92f7245e7f36"


def font(size, bold=True):
    p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
    try:
        return ImageFont.truetype(p, int(round(size)))
    except Exception:
        return ImageFont.load_default()


def split_addr(d, text, fnt, max_w):
    """第一行尽量排满，在 区/街道/路/号 处断"""
    if d.textlength(text, font=fnt) <= max_w:
        return [text]

    def fits(s):
        return d.textlength(s, font=fnt) <= max_w

    best = None
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        a, b = text[:i + 1], text[i + 1:]
        if a and b and fits(a) and fits(b):
            best = [a, b]
    if best:
        return best

    out, cur = [], ""
    for ch in text:
        if not fits(cur + ch):
            out.append(cur)
            cur = ch
            if len(out) == 1:
                break
        else:
            cur += ch
    out.append(text[len("".join(out)):])
    return [x for x in out if x][:2]


def shield_icon(d, x, y, size, color="#F2F2F2"):
    w = size
    pts = [(x + w * 0.5, y), (x + w * 0.95, y + w * 0.18), (x + w * 0.95, y + w * 0.55),
           (x + w * 0.5, y + w), (x + w * 0.05, y + w * 0.55), (x + w * 0.05, y + w * 0.18)]
    d.line(pts + [pts[0]], fill=color, width=max(2, int(w * 0.12)), joint="curve")
    d.line([x + w * 0.30, y + w * 0.50, x + w * 0.45, y + w * 0.66],
           fill=color, width=max(2, int(w * 0.13)))
    d.line([x + w * 0.45, y + w * 0.66, x + w * 0.72, y + w * 0.33],
           fill=color, width=max(2, int(w * 0.13)))


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.width, img.height
    u = w / 1080.0

    F = 38 * u
    f_addr = font(F)
    f_date = font(F)
    f_time = font(1.55 * F)
    f_tag = font(1.12 * F)
    f_small = font(0.78 * F)

    chip_h = 2.15 * F
    gap_chip = 0.93 * F
    line_h = 1.30 * F
    off_date = 1.62 * F
    off_small = 1.72 * F
    margin = 0.55 * F
    bar_w = 0.40 * F

    max_w = min(w - margin - 0.4 * F, 0.74 * w)
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = chip_h + gap_chip + len(lines) * line_h + off_date + off_small
    top = h - margin - block_h

    # 打卡徽章（黄 #F6C23C）
    tag_pad = 0.16 * F
    tag_w = d.textlength("打卡", font=f_tag) + tag_pad * 2
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.20 * F, fill="#F6C23C")
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.20 * F, outline=(255, 255, 255, 120), width=max(1, int(0.04 * F)))
    d.text((margin + tag_pad, top + chip_h / 2), "打卡", font=f_tag, fill="#0F0F0F", anchor="lm")

    # 时间块（钢蓝 #9BA7B7）
    time_pad = 0.08 * F
    time_w = d.textlength(hhmm, font=f_time) + time_pad * 2
    bx = margin + tag_w + 0.08 * F
    grad = Image.new("RGBA", (max(2, int(time_w)), max(2, int(chip_h))))
    gd = ImageDraw.Draw(grad)
    for i in range(grad.height):
        k = i / max(1, grad.height - 1)
        col = (int(176 - 46 * k), int(188 - 46 * k), int(203 - 40 * k), 245)
        gd.line([(0, i), (grad.width, i)], fill=col)
    mask = Image.new("L", grad.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1],
                                           radius=int(0.26 * F), fill=255)
    img.paste(grad, (int(bx), int(top)), mask)
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.26 * F, outline=(240, 245, 250, 230), width=max(1, int(0.05 * F)))
    tx = bx + time_pad
    ty = top + chip_h / 2 + 0.01 * F
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((tx + dx, ty + dy), hhmm, font=f_time, fill=(30, 44, 60, 200), anchor="lm")
    d.text((tx, ty), hhmm, font=f_time, fill="#FFFFFF", anchor="lm")

    # 黄竖条
    bar_top = top + chip_h + gap_chip * 0.55
    bar_bot = bar_top + len(lines) * line_h + off_date * 0.62
    d.rectangle([margin + 0.06 * F, bar_top, margin + 0.06 * F + bar_w, bar_bot], fill="#F6C23C")

    # 地址
    x = margin + 0.06 * F + bar_w + 0.36 * F
    y = bar_top + 0.10 * F
    for ln in lines:
        for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
            d.text((x + dx, y + dy), ln, font=f_addr, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += line_h

    # 日期
    y += off_date - line_h + 0.1 * F
    for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        d.text((x + dx, y + dy), date, font=f_date, fill=(0, 0, 0, 170))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # 底部验证行
    y += off_small - 0.15 * F
    ic = 0.72 * F
    shield_icon(d, x, y, ic)
    d.text((x + ic + 0.30 * F, y + 0.02 * F), "采集水印相机已验证 | 时间地点真实",
           font=f_small, fill="#F2F2F2")
    return img


def main():
    mine = Image.new("RGB", (1080, 780), "#2C2C2C")
    draw_stamp(mine)
    mine.save("docs/watermark-preview.png")

    ref = Image.open(REF).convert("RGB")
    out_w = 1080
    ref2 = ref.resize((out_w, int(ref.height * out_w / ref.width)), Image.LANCZOS)
    out = Image.new("RGB", (out_w, ref2.height + mine.height + 16), "#0A0A0A")
    out.paste(ref2, (0, 0))
    out.paste(mine, (0, ref2.height + 16))
    out.save("docs/watermark-compare.png")

    # 50% 混合：验证是否重合
    blend = Image.blend(ref2.convert("RGB"), mine.convert("RGB").resize(ref2.size), 0.5)
    blend.save("docs/watermark-blend.png")
    print("saved")


if __name__ == "__main__":
    main()
