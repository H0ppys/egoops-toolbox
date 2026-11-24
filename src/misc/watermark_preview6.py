"""水印贴近参考图（第四版）：加宽断行位置、徽章配色/描边、字重加粗、盾形图标。"""

import os

from PIL import Image, ImageDraw, ImageFont

REF = r"C:\Users\Administrator\.dsh\attachments\v1\objects\6c\6ccef35c990e989933fb24be8a8fa87ad2cccd69ca6e9a2bfd7c92f7245e7f36"


def font(size, bold=True):
    p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
    try:
        return ImageFont.truetype(p, int(round(size)))
    except Exception:
        return ImageFont.load_default()


def bold_text(d, xy, text, fnt, fill, outline=(0, 0, 0, 170)):
    """双描边让字更粗、在任何背景上都清楚"""
    x, y = xy
    o = 1
    for dx in (-o, 0, o):
        for dy in (-o, 0, o):
            if dx or dy:
                d.text((x + dx, y + dy), text, font=fnt, fill=outline)
    d.text((x, y), text, font=fnt, fill=fill)
    


def split_addr(d, text, fnt, max_w):
    if d.textlength(text, font=fnt) <= max_w:
        return [text]

    def fits(s):
        return d.textlength(s, font=fnt) <= max_w

    best = None
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        a, b = text[:i + 1], text[i + 1:]
        if not a or not b or not fits(a) or not fits(b):
            continue
        best = [a, b]          # 取最靠右的可行断点：第一行尽量排满
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


def shield_icon(d, x, y, size, color="#F0F0F0"):
    w = size
    pts = [(x + w * 0.5, y), (x + w * 0.95, y + w * 0.18), (x + w * 0.95, y + w * 0.55),
           (x + w * 0.5, y + w), (x + w * 0.05, y + w * 0.55), (x + w * 0.05, y + w * 0.18)]
    d.line(pts + [pts[0]], fill=color, width=max(2, int(w * 0.13)), joint="curve")
    d.line([x + w * 0.3, y + w * 0.5, x + w * 0.45, y + w * 0.66],
           fill=color, width=max(2, int(w * 0.14)))
    d.line([x + w * 0.45, y + w * 0.66, x + w * 0.72, y + w * 0.33],
           fill=color, width=max(2, int(w * 0.14)))


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.width, img.height
    u = w / 1080.0

    F = 40 * u
    f_addr = font(F)
    f_date = font(F)
    f_time = font(1.55 * F)
    f_tag = font(1.3 * F)
    f_small = font(0.8 * F)

    line_h = 1.42 * F
    chip_h = 2.3 * F
    gap = 0.9 * F
    margin = 0.6 * F
    bar_w = 0.42 * F

    max_w = w - margin - 0.45 * F
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = chip_h + gap * 0.55 + len(lines) * line_h + gap * 0.35 + 1.0 * F + gap * 0.5 + 0.85 * F
    top = h - margin - block_h

    # 打卡徽章
    tag_pad = 0.3 * F
    tag_w = d.textlength("打卡", font=f_tag) + tag_pad * 2
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h], radius=0.15 * F, fill="#F5C243")
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h], radius=0.15 * F,
                        outline=(255, 255, 255, 150), width=max(1, int(0.05 * F)))
    d.text((margin + tag_pad, top + chip_h / 2), "打卡", font=f_tag, fill="#0F0F0F", anchor="lm")

    # 时间徽章（钢蓝 + 白描边 + 内暗边）
    time_w = d.textlength(hhmm, font=f_time) + 0.44 * F
    bx = margin + tag_w + 0.12 * F
    chip_color = (124, 146, 170, 245)
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h], radius=0.18 * F, fill=chip_color)
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h], radius=0.18 * F,
                        outline=(240, 244, 248, 230), width=max(2, int(0.07 * F)))
    bold_text(d, (bx + 0.22 * F, top + chip_h / 2 - 0.62 * F), hhmm, f_time, "#FFFFFF",
              (20, 30, 45, 160))

    # 黄竖条
    bar_top = top + chip_h + gap * 0.55
    bar_bot = bar_top + len(lines) * line_h + gap * 0.3 + F
    d.rectangle([margin + 0.08 * F, bar_top, margin + 0.08 * F + bar_w, bar_bot], fill="#F5C243")

    # 地址（双描边加粗）
    x = margin + 0.08 * F + bar_w + 0.42 * F
    y = bar_top
    for ln in lines:
        bold_text(d, (x, y), ln, f_addr, "#FFFFFF")
        y += line_h

    # 日期
    y += gap * 0.3
    bold_text(d, (x, y), date, f_date, "#FFFFFF")

    # 底部
    y += F + gap * 0.45
    ic = 0.82 * F
    shield_icon(d, x, y + 0.06 * F, ic)
    d.text((x + ic + 0.35 * F, y + 0.05 * F), "采集水印已验证 | 时间地点真实",
           font=f_small, fill="#F2F2F2")
    return img


def main():
    mine = Image.new("RGB", (1080, 420), "#2C2C2C")
    draw_stamp(mine)
    mine.save("docs/watermark-preview.png")

    ref = Image.open(REF).convert("RGB")
    scale = 1080 / ref.width
    ref = ref.resize((1080, int(ref.height * scale)), Image.LANCZOS)
    out = Image.new("RGB", (1080, ref.height + mine.height + 16), "#0A0A0A")
    out.paste(ref, (0, 0))
    out.paste(mine, (0, ref.height + 16))
    out.save("docs/watermark-compare.png")
    print("saved")


if __name__ == "__main__":
    main()
