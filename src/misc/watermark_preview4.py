"""水印再贴近参考图（第三版）：时间块改钢蓝、字号/断行/图标按参考图对齐。"""

import os

from PIL import Image, ImageDraw, ImageFont

REF = r"C:\Users\Administrator\.dsh\attachments\v1\objects\6c\6ccef35c990e989933fb24be8a8fa87ad2cccd69ca6e9a2bfd7c92f7245e7f36"


def font(size, bold=True):
    p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
    try:
        return ImageFont.truetype(p, int(size))
    except Exception:
        return ImageFont.load_default()


def split_addr(d, text, fnt, max_w):
    if d.textlength(text, font=fnt) <= max_w:
        return [text]

    def fits(s):
        return d.textlength(s, font=fnt) <= max_w

    best, best_score = None, 10 ** 9
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        cut = i + 1
        a, b = text[:cut], text[cut:]
        if not a or not b:
            continue
        if not fits(a) or not fits(b):
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


def verified_icon(d, x, y, size, color="#EDEDED"):
    """圆角方框 + 勾（参考图是这种，不是盾牌）"""
    r = size * 0.28
    d.rounded_rectangle([x, y, x + size, y + size], radius=r, outline=color,
                        width=max(2, int(size * 0.11)))
    d.line([x + size * 0.26, y + size * 0.52, x + size * 0.44, y + size * 0.70],
           fill=color, width=max(2, int(size * 0.12)))
    d.line([x + size * 0.44, y + size * 0.70, x + size * 0.76, y + size * 0.32],
           fill=color, width=max(2, int(size * 0.12)))


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.width, img.height
    u = w / 1080.0

    margin = 36 * u
    f_addr = font(36 * u)
    f_date = font(33 * u)
    f_time = font(46 * u)
    f_tag = font(36 * u)
    f_small = font(23 * u, bold=False)

    line_h = 48 * u
    date_h = 44 * u
    small_h = 32 * u
    tag_h = 50 * u

    max_w = w - margin * 2 - 26 * u
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = tag_h + 13 * u + len(lines) * line_h + date_h + small_h
    top = h - margin - block_h

    # 打卡
    tag_w = d.textlength("打卡", font=f_tag) + 26 * u
    d.rounded_rectangle([margin, top, margin + tag_w, top + tag_h], radius=6 * u, fill="#FFD100")
    tw = d.textlength("打卡", font=f_tag)
    d.text((margin + (tag_w - tw) / 2, top + tag_h / 2), "打卡", font=f_tag,
           fill="#111111", anchor="lm")

    # 时间（钢蓝半透明 + 浅色描边）
    tw2 = d.textlength(hhmm, font=f_time)
    box_w = tw2 + 28 * u
    bx = margin + tag_w + 8 * u
    d.rounded_rectangle([bx, top, bx + box_w, top + tag_h], radius=7 * u, fill=(84, 102, 120, 235))
    d.rounded_rectangle([bx, top, bx + box_w, top + tag_h], radius=7 * u,
                        outline=(220, 228, 236, 200), width=max(1, int(1.4 * u)))
    d.text((bx + 14 * u, top + tag_h / 2 + 1 * u), hhmm, font=f_time, fill="#FFFFFF", anchor="lm")

    # 黄色竖条
    bar_top = top + tag_h + 13 * u
    bar_bot = bar_top + len(lines) * line_h + date_h - 4 * u
    d.rectangle([margin + 2 * u, bar_top, margin + 2 * u + 5 * u, bar_bot], fill="#FFD100")

    # 地址
    x = margin + 20 * u
    y = bar_top
    for ln in lines:
        d.text((x + 2 * u, y + 2 * u), ln, font=f_addr, fill=(0, 0, 0, 200))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += line_h

    # 日期
    y += 1 * u
    d.text((x + 2 * u, y + 2 * u), date, font=f_date, fill=(0, 0, 0, 200))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # 底部验证行
    y += date_h
    ic = 24 * u
    verified_icon(d, x, y + 3 * u, ic)
    d.text((x + ic + 9 * u, y + 3 * u), "采集水印已验证  |  时间地点真实",
           font=f_small, fill="#E6E6E6")
    return img


def main():
    mine = Image.new("RGB", (1080, 400), "#2E2E2E")
    draw_stamp(mine)
    ref = Image.open(REF).convert("RGB")
    ref = ref.resize((1080, int(ref.height * 1080 / ref.width)))
    out = Image.new("RGB", (1080, ref.height + mine.height + 20), "#0D0D0D")
    out.paste(ref, (0, 0))
    out.paste(mine, (0, ref.height + 20))
    out.save("docs/watermark-compare.png")
    mine.save("docs/watermark-preview.png")
    print("saved")


if __name__ == "__main__":
    main()
