"""量一下参考图里各个元素的位置和颜色，照着复刻。"""

import os

import numpy as np
from PIL import Image

REF = r"C:\Users\Administrator\.dsh\attachments\v1\objects\6c\6ccef35c990e989933fb24be8a8fa87ad2cccd69ca6e9a2bfd7c92f7245e7f36"

img = Image.open(REF).convert("RGB")
a = np.array(img)
h, w, _ = a.shape
print("size:", w, h)

r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)

# 黄色区域
yellow = (r > 200) & (g > 150) & (g < 240) & (b < 90)
ys, xs = np.where(yellow)
print("黄色像素:", len(xs))
if len(xs):
    print("  黄色 bbox: x %d-%d, y %d-%d" % (xs.min(), xs.max(), ys.min(), ys.max()))
    # 主色
    px = a[yellow]
    print("  黄色均值:", px.mean(axis=0).round(0))

# 时间块：偏蓝灰
steel = (b > r + 10) & (b > g + 5) & (b > 90) & (b < 230) & (r > 40)
ys2, xs2 = np.where(steel)
print("钢蓝像素:", len(xs2))
if len(xs2):
    print("  钢蓝 bbox: x %d-%d, y %d-%d" % (xs2.min(), xs2.max(), ys2.min(), ys2.max()))
    print("  钢蓝均值:", a[steel].mean(axis=0).round(0))

# 白色文字（地址/日期）
white = (r > 225) & (g > 225) & (b > 225)
ys3, xs3 = np.where(white)
print("白字 bbox: x %d-%d, y %d-%d" % (xs3.min(), xs3.max(), ys3.min(), ys3.max()))

# 逐行统计白像素，找出文字行的位置
rows = white.sum(axis=1)
runs = []
inrun = False
for y in range(h):
    if rows[y] > 3 and not inrun:
        start = y
        inrun = True
    elif rows[y] <= 3 and inrun:
        runs.append((start, y - 1, rows[start:y].max()))
        inrun = False
if inrun:
    runs.append((start, h - 1, rows[start:].max()))
print("文字行（y范围, 峰值像素）:")
for s, e, m in runs:
    print("  %3d - %3d  (高 %d, 峰值 %d)" % (s, e, e - s + 1, m))
