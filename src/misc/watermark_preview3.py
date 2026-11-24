"""按参考图继续贴近：并排对比 + 更接近的细节。

细节调整：
  · 时间块：深色半透明 + 细白边 + 阴影，圆角更小
  · 打卡块：黄底黑字，字重更粗，垂直居中
  · 底部：画一个盾形勾图标（矢量，不依赖字体）
  · 整体边距/字号/行距按参考图比例微调
"""

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


def shield(d, x, y, size, color="#E8E8E8"):
    """画一个盾形 + 勾"""
    w = size
    pts = [(x + w * 0.5, y), (x + w, y + w * 0.16), (x + w, y + w * 0.55),
           (x + w * 0.5, y + w), (x, y + w * 0.55), (x, y + w * 0.16)]
    d.polygon(pts, outline=color)
    d.line([x + w * 0.28, y + w * 0.45, x + w * 0.45, y + w * 0.65], fill=color, width=max(2, int(w * 0.1)))
    d.line([x + w * 0.45, y + w * 0.65, x + w * 0.75, y + w * 0.3], fill=color, width=max(2, int(w * 0.1)))


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img)
    w, h = img.width, img.height
    u = w / 1080.0

    margin = 40 * u
    f_addr = font(39 * u)
    f_date = font(34 * u)
    f_time = font(47 * u)
    f_tag = font(35 * u)
    f_small = font(24 * u, bold=False)

    line_h = 51 * u
    date_h = 46 * u
    small_h = 34 * u
    tag_h = 50 * u

    max_w = w - margin * 2 - 30 * u
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = tag_h + 14 * u + len(lines) * line_h + date_h + small_h
    top = h - margin - block_h

    # ---- 打卡块 ----
    tag_w = d.textlength("打卡", font=f_tag) + 24 * u
    d.rounded_rectangle([margin, top, margin + tag_w, top + tag_h], radius=5 * u, fill="#FFD100")
    tw = d.textlength("打卡", font=f_tag)
    d.text((margin + (tag_w - tw) / 2, top + tag_h / 2), "打卡", font=f_tag,
           fill="#141414", anchor="lm")

    # ---- 时间块 ----
    tw2 = d.textlength(hhmm, font=f_time)
    box_w = tw2 + 26 * u
    bx = margin + tag_w + 6 * u
    d.rounded_rectangle([bx, top, bx + box_w, top + tag_h], radius=5 * u, fill=(60, 60, 60))
    d.rounded_rectangle([bx, top, bx + box_w, top + tag_h], radius=5 * u, outline="#EFEFEF", width=max(1, int(1.6 * u)))
    d.text((bx + 13 * u, top + tag_h / 2), hhmm, font=f_time, fill="#FFFFFF", anchor="lm")

    # ---- 黄竖条 ----
    bar_top = top + tag_h + 14 * u
    bar_bot = bar_top + len(lines) * line_h + date_h - 6 * u
    d.rectangle([margin + 2 * u, bar_top, margin + 2 * u + 5 * u, bar_bot], fill="#FFD100")

    # ---- 地址 ----
    x = margin + 20 * u
    y = bar_top
    for ln in lines:
        d.text((x + 2 * u, y + 2 * u), ln, font=f_addr, fill="#000000")
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += line_h

    # ---- 日期 ----
    y += 2 * u
    d.text((x + 2 * u, y + 2 * u), date, font=f_date, fill="#000000")
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # ---- 底部：盾形勾 + 文案 ----
    y += date_h
    ic = 26 * u
    shield(d, x, y + 2 * u, ic)
    d.text((x + ic + 10 * u, y + 4 * u), "采集水印已验证  |  时间地点真实",
           font=f_small, fill="#EDEDED")
    return img


def main():
    # 我的效果
    mine = Image.new("RGB", (1080, 560), "#2E2E2E")
    draw_stamp(mine)

    # 参考图（放大到同宽）
    if os.path.exists(REF):
        ref = Image.open(REF).convert("RGB")
        ref = ref.resize((1080, int(ref.height * 1080 / ref.width)))
        out = Image.new("RGB", (1080, ref.height + mine.height + 30), "#111111")
        out.paste(ref, (0, 0))
        out.paste(mine, (0, ref.height + 30))
    else:
        out = mine
    out.save("docs/watermark-compare.png")
    print("saved docs/watermark-compare.png")


if __name__ == "__main__":
    main()
