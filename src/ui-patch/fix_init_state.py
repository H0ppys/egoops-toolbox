import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 初始化容器
if 'self.site_rows = {}' not in s:
    s = s.replace('''        self.files = []
        self.checked = set()
        self.checked_sites = set()''', '''        self.files = []
        self.checked = set()
        self.checked_sites = set()
        self.site_rows = {}
        self.file_rows = {}
        self.loaded_sites = set()''')

# 2) _poll 里捕获异常并显示，别静默吞掉
s = s.replace('''    def _poll(self):
        try:
            while True:
                fn, args = self.events.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.root.after(80, self._poll)''', '''    def _poll(self):
        try:
            while True:
                fn, args = self.events.get_nowait()
                try:
                    fn(*args)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.set_status("界面出错：%s" % e, "#b3261e")
        except queue.Empty:
            pass
        self.root.after(80, self._poll)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('init fixed')
