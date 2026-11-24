import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''    def ui(self, fn, *args, **kwargs):'''
if old in s:
    print('ui 已经支持 kwargs')
else:
    # 找到现有 ui 定义并让它接受 kwargs
    import re
    m = re.search(r'    def ui\(self, fn[^)]*\):\n(.*?)\n\n', s, re.S)
    print('现有 ui 定义:\n', m.group(0) if m else '未找到')
    s = s.replace('    def ui(self, fn, *args):\n',
                  '    def ui(self, fn, *args, **kwargs):\n')
    # 把入队内容也带上 kwargs
    s = s.replace('''                fn, args = self.events.get_nowait()
                try:
                    fn(*args)''', '''                item = self.events.get_nowait()
                fn, args = item[0], item[1]
                kwargs = item[2] if len(item) > 2 else {}
                try:
                    fn(*args, **kwargs)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
