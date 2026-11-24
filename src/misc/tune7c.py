"""再做一轮模仿：微调圆角/描边，并把我的水印叠到参考图上做 50% 混合，看是否重合。"""

import io

p = 'tools/watermark_preview7.py'
s = io.open(p, encoding='utf-8').read()

# 圆角更接近参考图
s = s.replace('radius=0.12 * F, fill="#F6C23C"', 'radius=0.20 * F, fill="#F6C23C"')
s = s.replace('radius=0.12 * F, outline=(255, 255, 255, 120)', 'radius=0.20 * F, outline=(255, 255, 255, 120)')
s = s.replace('radius=0.14 * F, outline=(240, 245, 250, 230)', 'radius=0.26 * F, outline=(240, 245, 250, 230)')
s = s.replace('mask = Image.new("L", grad.size, 0)\n    ImageDraw.Draw(mask).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1],\n                                           radius=int(0.14 * F), fill=255)',
              'mask = Image.new("L", grad.size, 0)\n    ImageDraw.Draw(mask).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1],\n                                           radius=int(0.26 * F), fill=255)')

# 混合图
s = s.replace('''    out.save("docs/watermark-compare.png")
    print("saved")''',
'''    out.save("docs/watermark-compare.png")

    # 50% 混合：验证是否重合
    blend = Image.blend(ref2.convert("RGB"), mine.convert("RGB").resize(ref2.size), 0.5)
    blend.save("docs/watermark-blend.png")
    print("saved")''')

io.open(p, 'w', encoding='utf-8').write(s)
print('微调 + 混合图')
