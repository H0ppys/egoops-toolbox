import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('"who": 78,', '"who": 100,')
s = s.replace('"name": 150, "vendor": 100, "detail": 190,', '"name": 140, "vendor": 96, "detail": 180,')

io.open(p, 'w', encoding='utf-8').write(s)
print('列宽微调 ok')
