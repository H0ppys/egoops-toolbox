import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('root.geometry("1320x760")', 'root.geometry("1440x820")')
s = s.replace('root.minsize(980, 600)', 'root.minsize(1100, 640)')

s = s.replace('body.add(left, weight=2)', 'body.add(left, weight=3)')
s = s.replace('body.add(right, weight=3)', 'body.add(right, weight=4)')

s = s.replace('(34, 140, 200, 58, 100, 105, 46, 38, 38, 62)',
              '(32, 132, 178, 54, 92, 96, 44, 36, 36, 58)')

io.open(p, 'w', encoding='utf-8').write(s)
print('layout tuned')
