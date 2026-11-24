"""和 App 里 Java 完全一致的参数，出当前水印效果（含防伪码；地图可选）。"""

import io
import sys

sys.path.insert(0, "viewer")

from PIL import Image, ImageDraw, ImageFont

F_BASE = 38          # 地址字号（/1080 宽）
BADGE = "采集水印相机已验证 | 时间地点真实"


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


def shield(d, x, y, size, color="#F2F2F2"):
    w = size
    pts = [(x + w * .5, y), (x + w * .95, y + w * .18), (x + w * .95, y + w * .55),
           (x + w * .5, y + w), (x + w * .05, y + w * .55), (x + w * .05, y + w * .18)]
    d.line(pts + [pts[0]], fill=color, width=max(2, int(w * .12)), joint="curve")
    d.line([x + w * .30, y + w * .50, x + w * .45, y + w * .66], fill=color, width=max(2, int(w * .13)))
    d.line([x + w * .45, y + w * .66, x + w * .72, y + w * .33], fill=color, width=max(2, int(w * .13)))


def draw(img, addr, hhmm="16:49", date="2026.11.24 星期二", code="53F577BC1BE9", map_img=None):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    u = w / 1080.0
    F = F_BASE * u

    chipH, gapChip = 2.15 * F, 0.93 * F
    lineH, offDate, offSmall = 1.30 * F, 1.62 * F, 1.72 * F
    margin, barW = 0.55 * F, 0.40 * F
    maxW = min(w - margin - 0.40 * F, 0.74 * w)

    f_addr = font(F); f_date = font(F); f_time = font(1.55 * F)
    f_tag = font(1.12 * F); f_small = font(0.78 * F)
    lines = split_addr(d, addr, f_addr, maxW)

    blockH = chipH + gapChip + len(lines) * lineH + offDate + offSmall
    top = h - margin - blockH

    # 打卡
    pad = 0.16 * F
    tagW = d.textlength("打卡", font=f_tag) + pad * 2
    d.rounded_rectangle([margin, top, margin + tagW, top + chipH], radius=0.20 * F, fill="#F6C23C")
    d.text((margin + pad, top + chipH / 2), "打卡", font=f_tag, fill="#0F0F0F", anchor="lm")

    # 时间（渐变）
    tp = 0.08 * F
    tw = d.textlength(hhmm, font=f_time) + tp * 2
    bx = margin + tagW + 0.08 * F
    grad = Image.new("RGBA", (max(2, int(tw)), max(2, int(chipH))))
    gd = ImageDraw.Draw(grad)
    for i in range(grad.height):
        k = i / max(1, grad.height - 1)
        gd.line([(0, i), (grad.width, i)],
                fill=(int(176 - 46 * k), int(188 - 46 * k), int(203 - 40 * k), 245))
    mask = Image.new("L", grad.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1],
                                           radius=int(0.26 * F), fill=255)
    img.paste(grad, (int(bx), int(top)), mask)
    d.rounded_rectangle([bx, top, bx + tw, top + chipH], radius=0.26 * F,
                        outline=(240, 245, 250, 230), width=max(1, int(0.05 * F)))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((bx + tp + dx, top + chipH / 2 + dy), hhmm, font=f_time,
               fill=(30, 44, 60, 200), anchor="lm")
    d.text((bx + tp, top + chipH / 2), hhmm, font=f_time, fill="#FFFFFF", anchor="lm")

    # 黄竖条
    barTop = top + chipH + gapChip * 0.55
    barBot = barTop + len(lines) * lineH + offDate * 0.62
    d.rectangle([margin + 0.06 * F, barTop, margin + 0.06 * F + barW, barBot], fill="#F6C23C")

    # 地址
    x = margin + 0.06 * F + barW + 0.36 * F
    y = barTop + 0.10 * F
    for ln in lines:
        for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
            d.text((x + dx, y + dy), ln, font=f_addr, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")
        y += lineH

    # 日期
    y += offDate - lineH + 0.10 * F
    for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        d.text((x + dx, y + dy), date, font=f_date, fill=(0, 0, 0, 170))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")

    # 验证行
    y += offSmall - 0.15 * F
    ic = 0.72 * F
    shield(d, x, y, ic)
    d.text((x + ic + 0.30 * F, y + 0.02 * F), BADGE, font=f_small, fill="#F2F2F2")

    # 防伪码
    if code:
        f_code = font(0.62 * F)
        txt = "防伪 " + code
        cw = d.textlength(txt, font=f_code)
        d.text((w - margin - cw, h - margin * 0.55 - f_code.size), txt, font=f_code, fill=(255, 255, 255, 210))

    # 地图
    if map_img is not None:
        cardW = w * 0.30
        cardH = cardW * 1.02
        mx = w - margin - cardW
        my = margin
        m = map_img.resize((int(cardW), int(cardH)), Image.LANCZOS).convert("RGBA")
        mmask = Image.new("L", m.size, 0)
        ImageDraw.Draw(mmask).rounded_rectangle([0, 0, m.width - 1, m.height - 1],
                                                radius=int(cardW * 0.06), fill=255)
        img.paste(m, (int(mx), int(my)), mmask)
        d.rounded_rectangle([mx, my, mx + cardW, my + cardH], radius=cardW * 0.06,
                            outline=(255, 255, 255, 240), width=max(2, int(cardW * 0.012)))
    return img


def main():
    src = Image.open("docs/_sample_photo.jpg").convert("RGB")
    w = 1080
    h = int(src.height * w / src.width)
    base = src.resize((w, h), Image.LANCZOS)

    a = draw(base.copy(), "广东省广州市黄埔区萝岗街道粤港澳大湾区青年创业科技园")
    a.save("docs/watermark-real.png")
    print("saved docs/watermark-real.png（当前版本，不含地图）")


if __name__ == "__main__":
    main()
