"""修进度条一直满：下载把 maximum 改成了文件个数，草稿又按 0-100 写 value，导致溢出。
   统一成 maximum=100，value 一律是百分比。
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''    def _set_progress(self, pct, text):
        self.progress["value"] = pct
        self.lbl_task.config(text=text)'''
new = '''    def _set_progress(self, pct, text):
        self.progress["maximum"] = 100
        self.progress["value"] = max(0, min(100, pct))
        self.lbl_task.config(text=text)'''
assert old in s
s = s.replace(old, new)

old2 = '''    def set_progress(self, done, total):
        if total:
            self.progress["maximum"] = total
            self.progress["value"] = min(done, total)'''
new2 = '''    def set_progress(self, done, total):
        if total:
            self.progress["maximum"] = 100
            self.progress["value"] = max(0, min(100, done * 100.0 / total))'''
assert old2 in s
s = s.replace(old2, new2)

# 下载开始时也统一
s = s.replace('''        self.progress["value"] = 0
        self.progress["maximum"] = 100''', '''        self.progress["maximum"] = 100
        self.progress["value"] = 0''')

# 建草稿开始时复位
if 'def _reset_progress' not in s:
    s = s.replace('''    def _set_progress(self, pct, text):''', '''    def _reset_progress(self):
        self.progress["maximum"] = 100
        self.progress["value"] = 0

    def _set_progress(self, pct, text):''')
    s = s.replace('''        self.btn_fill.config(state="disabled")''',
                  '''        self.btn_fill.config(state="disabled")
        self._reset_progress()''', 1)

# 完成后满格
s = s.replace('''    def _draft_done(self, res):
        self.progress["value"] = 100''', '''    def _draft_done(self, res):
        self.progress["maximum"] = 100
        self.progress["value"] = 100''')

io.open(p, 'w', encoding='utf-8').write(s)
print('进度条统一为百分比')
