"""白墙/浅色场景下也要看清：加深描边阴影；再出一张竖版示例。"""

import io

p = 'tools/watermark_preview7.py'
s = io.open(p, encoding='utf-8').read()

# 地址与日期：加更强的描边（先画 4 方向深色，再画白字）
old = '''        d.text((x + 1, y + 1), ln, font=f_addr, fill=(0, 0, 0, 165))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")'''
new = '''        for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
            d.text((x + dx, y + dy), ln, font=f_addr, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=f_addr, fill="#FFFFFF")'''
assert old in s
s = s.replace(old, new)

old2 = '''    d.text((x + 0.04 * F, y + 0.04 * F), date, font=f_date, fill=(0, 0, 0, 170))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")'''
new2 = '''    for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        d.text((x + dx, y + dy), date, font=f_date, fill=(0, 0, 0, 170))
    d.text((x, y), date, font=f_date, fill="#FFFFFF")'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('加深描边')
