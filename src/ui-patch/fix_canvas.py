import io

p = 'tools/watermark_preview7.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('mine = Image.new("RGB", (1080, 430), "#2C2C2C")',
              'mine = Image.new("RGB", (1080, 780), "#2C2C2C")')
io.open(p, 'w', encoding='utf-8').write(s)
print('canvas 780')
