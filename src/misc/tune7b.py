"""最后一轮：时间块加渐变+数字描边，地址字重调轻，徽章加细边。"""

import io

p = 'tools/watermark_preview7.py'
s = io.open(p, encoding='utf-8').read()

# 1) 时间块：渐变 + 数字描边
old = '''    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.14 * F, fill=(155, 167, 183, 240))
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.14 * F, outline=(232, 238, 244, 220), width=max(1, int(0.05 * F)))
    d.text((bx + time_pad, top + chip_h / 2 + 0.01 * F), hhmm, font=f_time,
           fill="#FFFFFF", anchor="lm")'''
new = '''    grad = Image.new("RGBA", (max(2, int(time_w)), max(2, int(chip_h))))
    gd = ImageDraw.Draw(grad)
    for i in range(grad.height):
        k = i / max(1, grad.height - 1)
        col = (int(176 - 46 * k), int(188 - 46 * k), int(203 - 40 * k), 245)
        gd.line([(0, i), (grad.width, i)], fill=col)
    mask = Image.new("L", grad.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1],
                                           radius=int(0.14 * F), fill=255)
    img.paste(grad, (int(bx), int(top)), mask)
    d.rounded_rectangle([bx, top, bx + time_w, top + chip_h],
                        radius=0.14 * F, outline=(240, 245, 250, 230), width=max(1, int(0.05 * F)))
    tx = bx + time_pad
    ty = top + chip_h / 2 + 0.01 * F
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((tx + dx, ty + dy), hhmm, font=f_time, fill=(30, 44, 60, 200), anchor="lm")
    d.text((tx, ty), hhmm, font=f_time, fill="#FFFFFF", anchor="lm")'''
assert old in s
s = s.replace(old, new)

# 2) 徽章细边
old2 = '''    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.12 * F, fill="#F6C23C")'''
new2 = '''    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.12 * F, fill="#F6C23C")
    d.rounded_rectangle([margin, top, margin + tag_w, top + chip_h],
                        radius=0.12 * F, outline=(255, 255, 255, 120), width=max(1, int(0.04 * F)))'''
assert old2 in s
s = s.replace(old2, new2)

# 3) 地址字重：只留 1px 阴影，不叠加描边
old3 = '''        d.text((x + 0.04 * F, y + 0.04 * F), ln, font=f_addr, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")'''
new3 = '''        d.text((x + 1, y + 1), ln, font=f_addr, fill=(0, 0, 0, 165))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")'''
assert old3 in s
s = s.replace(old3, new3)

io.open(p, 'w', encoding='utf-8').write(s)
print('渐变+描边+字重 已调整')
