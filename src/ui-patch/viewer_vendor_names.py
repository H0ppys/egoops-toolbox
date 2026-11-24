"""查看器：厂商名从服务器拿（邀请码 → 厂家），不再要求本地配映射。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) vendor_of 优先用服务器给的码表，其次本地映射
s = s.replace('''    def vendor_of(self, site):
        code = (site.get("invite") or "").strip()
        if not code:
            return "—"
        # 大小写不敏感匹配：采集员填 zjmeiyi、你配 ZJMEIYI，都能对上
        for k, v in self.invites_map().items():
            if k.strip().upper() == code.upper():
                return v
        return code.upper() + "（未配置）"''',
'''    def vendor_of(self, site):
        code = (site.get("invite") or "").strip()
        if not code:
            return "—"
        up = code.upper()
        # 1) 服务器上的「邀请码 → 厂家」（飞书表同步过来的）
        names = getattr(self, "vendor_names", None) or {}
        if up in names:
            return names[up]
        # 2) 本机自己配的映射
        for k, v in self.invites_map().items():
            if k.strip().upper() == up:
                return v
        return up + "（未登记）"''')

# 2) 连上以后拉一次码表
if 'load_vendor_names' not in s:
    s = s.replace('''    def load_vendors(self):''', '''    def load_vendor_names(self):
        def work():
            try:
                items = self.api.vendor_names()
            except Exception:
                return
            self.vendor_names = {str(k).upper(): v for k, v in (items or {}).items()}
            self.ui(self.do_refresh)

        threading.Thread(target=work, daemon=True).start()

    def load_vendors(self):''')

    s = s.replace('''        self.load_vendors()
        self.do_refresh()''', '''        self.load_vendor_names()
        self.load_vendors()
        self.do_refresh()''', 1)

# 3) 初始化字段
s = s.replace('''        self.vendor_filter = ""''', '''        self.vendor_filter = ""
        self.vendor_names = {}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('查看器：厂商名走服务器码表')

# 4) api.py 加接口
p2 = 'viewer/api.py'
t = io.open(p2, encoding='utf-8').read()
if 'def vendor_names' not in t:
    t = t.replace('''    def vendors(self):''', '''    def vendor_names(self):
        return self._request("GET", "/api/vendor-names", timeout=10).get("items", {})

    def vendors(self):''')
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('api: vendor_names')
