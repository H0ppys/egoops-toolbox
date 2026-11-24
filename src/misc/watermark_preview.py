"""按「今日水印相机」的样式重画水印，并生成一张预览图对比。

样式：
  [打卡] [15:32]        ← 黄底黑字标签 + 深底白字时间
  ▌地址第一行
  ▌地址第二行
  ▌2026.11.24 星期二
  ✓ 采集水印已验证 | 时间地点真实
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 700            # 预览画布（模拟一张照片的下半部分）


def font(size, bold=True):
    for name in (("msyhbd.ttc" if bold else "msyh.ttc"), "simhei.ttf"):
        for base in (r"C:\Windows\Fonts",):
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()


def draw_stamp(img, addr="广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园",
               hhmm="15:32", date="2026.11.24 星期二"):
    d = ImageDraw.Draw(img)
    w = img.width
    h = img.height
    u = w / 1080.0

    margin = int(48 * u)
    bold_big = font(int(38 * u))
    bold_mid = font(int(34 * u))
    bold_time = font(int(44 * u))
    small = font(int(26 * u), bold=False)

    # 底部整体从下往上排
    small_h = int(30 * u)
    date_h = int(44 * u)
    line_h = int(50 * u)

    # 地址折行（最多两行）
    max_w = w - margin * 2 - int(18 * u)
    lines, cur = [], ""
    for ch in addr:
        if d.textlength(cur + ch, font=bold_big) > max_w:
            lines.append(cur)
            cur = ch
            if len(lines) >= 2:
                break
        else:
            cur += ch
    if cur and len(lines) < 2:
        lines.append(cur)

    block_h = int(56 * u) + len(lines) * line_h + date_h + small_h + int(16 * u)
    top = h - margin - block_h

    # ---- 打卡 + 时间 ----
    y = top
    tag_text = "打卡"
    tag_w = d.textlength(tag_text, font=bold_big) + int(28 * u)
    tag_h = int(52 * u)
    d.rounded_rectangle([margin, y, margin + tag_w, y + tag_h], radius=int(8 * u), fill="#FFC400")
    d.text((margin + int(14 * u), y + int(6 * u)), tag_text, font=bold_big, fill="#111111")

    time_x = margin + tag_w + int(10 * u)
    time_w = d.textlength(" " + hhmm + " ", font=bold_time) + int(16 * u)
    d.rounded_rectangle([time_x, y, time_x + time_w, y + tag_h], radius=int(8 * u), fill="#000000")
    d.text((time_x + int(10 * u), y + int(2 * u)), hhmm, font=bold_time, fill="#FFFFFF")

    # ---- 左侧黄条 ----
    bar_top = y + tag_h + int(14 * u)
    bar_bottom = bar_top + len(lines) * line_h + date_h - int(6 * u)
    d.rectangle([margin, bar_top, margin + int(6 * u), bar_bottom], fill="#FFC400")

    # ---- 地址 ----
    tx = margin + int(18 * u)
    ty = bar_top
    for ln in lines:
        d.text((tx + int(2 * u), ty + int(2 * u)), ln, font=bold_big, fill="#000000")  # 阴影
        d.text((tx, ty), ln, font=bold_big, fill="#FFFFFF")
        ty += line_h

    # ---- 日期 ----
    ty += int(2 * u)
    d.text((tx + int(2 * u), ty + int(2 * u)), date, font=bold_mid, fill="#000000")
    d.text((tx, ty), date, font=bold_mid, fill="#FFFFFF")

    # ---- 底部小字 ----
    ty += date_h
    d.text((tx, ty), "✓ 采集水印已验证  |  时间地点真实", font=small, fill="#D9D9D9")
    return img


def main():
    base = Image.open("docs/wm_base.jpg") if os.path.exists("docs/wm_base.jpg") else None
    if base is None:
        base = Image.new("RGB", (W, H), "#3A3A3A")
        # 加点纹理模拟照片
        d = ImageDraw.Draw(base)
        for i in range(0, H, 40):
            d.line([(0, i), (W, i)], fill="#444444")
    img = draw_stamp(base.convert("RGB").resize((W, H)))
    img.save("docs/watermark-preview.png")
    print("saved docs/watermark-preview.png")


if __name__ == "__main__":
    main()
