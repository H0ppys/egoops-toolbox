"""水印预览 v2：地址两行均衡断行、去掉缺字形的 ✓、间距更接近参考图。"""

import os

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=True):
    p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def split_addr(d, text, fnt, max_w):
    """优先在 区/街道/路/号 等处断开，并让两行长度接近"""
    if d.textlength(text, font=fnt) <= max_w:
        return [text]

    def fits(s):
        return d.textlength(s, font=fnt) <= max_w

    boundaries = [i + 1 for i, ch in enumerate(text) if ch in "区街道路号镇乡村巷弄段"]
    best = None
    for i in boundaries:
        a, b = text[:i], text[i:]
        if not fits(a) or not fits(b):
            continue
        score = abs(len(a) - len(b))
        if best is None or score < best[0]:
            best = (score, [a, b])
    if best:
        return best[1]

    # 退路：按宽度硬断
    out, cur = [], ""
    for ch in text:
        if not fits(cur + ch):
            out.append(cur)
            cur = ch
            if len(out) == 1:
                break
        else:
            cur += ch
    rest = text[len("".join(out)):]
    out.append(rest)
    return out[:2]


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img)
    w, h = img.width, img.height
    u = w / 1080.0

    margin = int(46 * u)
    f_addr = font(int(38 * u))
    f_date = font(int(36 * u))
    f_time = font(int(46 * u))
    f_tag = font(int(36 * u))
    f_small = font(int(25 * u), bold=False)

    line_h = int(52 * u)
    date_h = int(48 * u)
    small_h = int(34 * u)
    tag_h = int(50 * u)

    max_w = w - margin * 2 - int(26 * u)
    lines = split_addr(d, addr, f_addr, max_w)

    block_h = tag_h + int(16 * u) + len(lines) * line_h + date_h + small_h + int(10 * u)
    top = h - margin - block_h

    # 打卡标签
    tag_text = "打卡"
    tag_w = d.textlength(tag_text, font=f_tag) + int(26 * u)
    d.rounded_rectangle([margin, top, margin + tag_w, top + tag_h], radius=int(6 * u), fill="#FFC400")
    d.text((margin + int(13 * u), top + int(7 * u)), tag_text, font=f_tag, fill="#141414")

    # 时间块
    tx0 = margin + tag_w + int(8 * u)
    tw = d.textlength(hhmm, font=f_time) + int(22 * u)
    d.rounded_rectangle([tx0, top, tx0 + tw, top + tag_h], radius=int(6 * u), fill="#1A1A1A")
    d.text((tx0 + int(11 * u), top + int(3 * u)), hhmm, font=f_time, fill="#FFFFFF")

    # 左侧黄竖条
    bar_top = top + tag_h + int(14 * u)
    bar_bot = bar_top + len(lines) * line_h + date_h - int(8 * u)
    d.rectangle([margin, bar_top, margin + int(6 * u), bar_bot], fill="#FFC400")

    # 地址
    x = margin + int(18 * u)
    y = bar_top
    for ln in lines:
        d.text((x + int(2 * u), y + int(2 * u)), ln, font=f_addr, fill="#000000")
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += line_h

    # 日期
    y += int(2 * u)
    d.text((x + int(2 * u), y + int(2 * u)), date, font=f_date, fill="#000000")
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # 底部小字（不用特殊符号，避免缺字形）
    y += date_h
    d.text((x, y), "采集水印已验证  |  时间地点真实", font=f_small, fill="#CFCFCF")
    return img


def main():
    img = Image.new("RGB", (1080, 700), "#3A3A3A")
    d = ImageDraw.Draw(img)
    for i in range(0, 700, 40):
        d.line([(0, i), (1080, i)], fill="#434343")
    draw_stamp(img).save("docs/watermark-preview.png")
    print("saved")


if __name__ == "__main__":
    main()
