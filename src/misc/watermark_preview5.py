"""按参考图实测比例复刻水印（单位 u = 宽度/1080）。

实测（344 宽裁剪图，地址字高 14px 记为 F）：
 时间字号 1.57F   日期字号 1.0F   底部小字 0.86F
 徽章高 2.36F     行距 1.43F     各段间距 0.93F
 左边距 0.64F     黄条宽 0.43F    两徽章间距 0.14F
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
    if d.textlength(text, font=fnt) <= max_w:
        return [text]

    def fits(s):
        return d.textlength(s, font=fnt) <= max_w

    # 参考图是在「大湾区」后面断的，优先让两行尽量均衡
    best, best_score = None, 10 ** 9
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        a, b = text[:i + 1], text[i + 1:]
        if not a or not b or not fits(a) or not fits(b):
            continue
        sc = abs(len(a) - len(b))
        if sc < best_score:
            best_score, best = sc, [a, b]
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


def verified_icon(d, x, y, size, color="#F0F0F0"):
    d.rounded_rectangle([x, y, x + size, y + size], radius=size * 0.26,
                        outline=color, width=max(2, int(size * 0.12)))
    d.line([x + size * 0.24, y + size * 0.52, x + size * 0.43, y + size * 0.70],
           fill=color, width=max(2, int(size * 0.13)))
    d.line([x + size * 0.43, y + size * 0.70, x + size * 0.78, y + size * 0.30],
           fill=color, width=max(2, int(size * 0.13)))


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.width, img.height
    u = w / 1080.0

    F = 40 * u                     # 地址字号
    f_addr = font(F)
    f_date = font(F)
    f_time = font(1.57 * F)
    f_tag = font(1.35 * F)
    f_small = font(0.86 * F)

    line_h = 1.43 * F
    chip_h = 2.36 * F
    gap = 0.93 * F
    margin = 0.64 * F
    bar_w = 0.43 * F

    max_w = w - margin - 0.5 * F - 0.7 * F
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = chip_h + gap * 0.6 + len(lines) * line_h + gap * 0.6 + 1.0 * F + gap * 0.6 + 0.86 * F
    top = h - margin - block_h

    # 打卡徽章
    tag_pad = 0.28 * F
    tag_text_w = d.textlength("打卡", font=f_tag)
    tag_w = tag_text_w + tag_pad * 2
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.16 * F, fill="#F6C243")
    d.text((margin + tag_pad, top + chip_h / 2), "打卡", font=f_tag, fill="#101010", anchor="lm")

    # 时间徽章（钢蓝半透明 + 浅描边）
    time_w = d.textlength(hhmm, font=f_time) + 0.42 * F
    bx = margin + tag_w + 0.14 * F
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.20 * F, fill=(150, 163, 180, 240))
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.20 * F, outline=(235, 240, 245, 210), width=max(1, int(0.06 * F)))
    d.text((bx + 0.21 * F, top + chip_h / 2 + 0.02 * F), hhmm, font=f_time,
           fill="#FFFFFF", anchor="lm")

    # 黄色竖条
    bar_top = top + chip_h + gap * 0.6
    bar_bot = bar_top + len(lines) * line_h + gap * 0.5 + F - 0.15 * F
    d.rectangle([margin + 0.1 * F, bar_top, margin + 0.1 * F + bar_w, bar_bot], fill="#F6C243")

    # 地址
    x = margin + 0.1 * F + bar_w + 0.45 * F
    y = bar_top
    for ln in lines:
        d.text((x + 0.05 * F, y + 0.05 * F), ln, font=f_addr, fill=(0, 0, 0, 190))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += line_h

    # 日期
    y += gap * 0.5
    d.text((x + 0.05 * F, y + 0.05 * F), date, font=f_date, fill=(0, 0, 0, 190))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # 底部验证行
    y += 1.0 * F + gap * 0.55
    ic = 0.8 * F
    verified_icon(d, x, y, ic)
    d.text((x + ic + 0.3 * F, y + 0.02 * F), "采集水印已验证 | 时间地点真实",
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
    print("saved (参考图放大 %.2f 倍对齐)" % scale)


if __name__ == "__main__":
    main()
