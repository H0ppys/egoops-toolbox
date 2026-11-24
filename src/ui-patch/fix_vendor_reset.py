"""修：do_refresh 里误把 vendor_names / vendor_systems 清空了（导致厂商列一直显示"未登记"）。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

bad = '''    def do_refresh(self):
        self.vendor_filter = ""
        self.vendor_names = {}
        self.vendor_systems = {} if self.cmb_vendor.get() in ("全部", "") else self.cmb_vendor.get()
'''
good = '''    def do_refresh(self):
'''
assert bad in s, '找不到 do_refresh 里的错误片段'
s = s.replace(bad, good)

# 确保 __init__ 里有这两个字段
if 'self.vendor_names = {}' not in s.split('def _build')[0]:
    s = s.replace('''        self.vendor_filter = ""''', '''        self.vendor_filter = ""
        self.vendor_names = {}
        self.vendor_systems = {}''', 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('已修 do_refresh 清空问题')
