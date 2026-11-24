import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 刷新时按厂商过滤
s = s.replace('''                items = self.api.sites()''',
              '''                items = self.api.sites(getattr(self, "vendor_filter", "") or "")''')

# 2) 连上之后填充厂商下拉
s = s.replace('''    def on_connected(self, health):''', '''    def load_vendors(self):
        def work():
            try:
                items = self.api.vendors()
            except Exception:
                return
            values = ["全部"] + [x.get("vendor") for x in items if x.get("vendor")]
            self.ui(lambda: self.cmb_vendor.configure(values=values))

        threading.Thread(target=work, daemon=True).start()

    def on_connected(self, health):''')

s = s.replace('''        self.do_refresh()''', '''        self.load_vendors()
        self.do_refresh()''', 1)

# 3) 初始化 vendor_filter
s = s.replace('''        self._preview_cache = {}''', '''        self.vendor_filter = ""
        self._preview_cache = {}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('vendor filter wired')
