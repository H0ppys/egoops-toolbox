import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 邀请码 → 厂商 的本地映射 ----------
s = s.replace('''    def load_vendors(self):''', '''    def invites_map(self):
        """本地配置：{"ZJMEIYI": "湛江盛宴科技有限公司"}"""
        m = self.cfg.get("invites")
        if not isinstance(m, dict):
            m = {}
            self.cfg["invites"] = m
        return m

    def vendor_of(self, site):
        code = (site.get("invite") or "").strip().upper()
        if not code:
            return "—"
        return self.invites_map().get(code) or (code + "（未配置）")

    def load_vendors(self):''')

# ---------- 2) 厂商列用本地映射 ----------
s = s.replace('''                it.get("vendor") or "—",''', '''                self.vendor_of(it),''')

# ---------- 3) 筛选改成按本地映射 ----------
s = s.replace('''    def do_refresh(self):
        vendor = "" if self.cmb_vendor.get() in ("全部", "") else self.cmb_vendor.get()
        self.vendor_filter = vendor''', '''    def do_refresh(self):
        self.vendor_filter = "" if self.cmb_vendor.get() in ("全部", "") else self.cmb_vendor.get()''')

s = s.replace('''                items = self.api.sites(getattr(self, "vendor_filter", "") or "")''',
'''                items = self.api.sites()
                want = getattr(self, "vendor_filter", "")
                if want:
                    items = [x for x in items if self.vendor_of(x) == want]''')

# ---------- 4) 厂商下拉由本地映射生成 ----------
old_lv = s[s.index('    def load_vendors(self):'):s.index('    def on_connected(self, health):')]
new_lv = '''    def load_vendors(self):
        m = self.invites_map()
        values = ["全部"] + sorted(set(v for v in m.values() if v))
        self.cmb_vendor.configure(values=values)
        if self.cmb_vendor.get() not in values:
            self.cmb_vendor.set("全部")

'''
s = s.replace(old_lv, new_lv)

io.open(p, 'w', encoding='utf-8').write(s)
print('本地映射已接入')
