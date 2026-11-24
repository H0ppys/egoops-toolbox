import io

# ---------------- api.py：邀请码 + 厂商 ----------------
p = 'viewer/api.py'
s = io.open(p, encoding='utf-8').read()

if 'def invites' not in s:
    s = s.replace('''    def site(self, site_id):''', '''    def invites(self, admin_key):
        return self._request("GET", "/api/invites", headers={"x-admin-key": admin_key}, timeout=10).get("items", [])

    def add_invite(self, code, vendor, note, admin_key):
        return self._request("POST", "/api/invites", {"code": code, "vendor": vendor, "note": note},
                             headers={"x-admin-key": admin_key}, timeout=10)

    def del_invite(self, code, admin_key):
        return self._request("DELETE", "/api/invites?code=" + urllib.parse.quote(code),
                             headers={"x-admin-key": admin_key}, timeout=10)

    def vendors(self):
        return self._request("GET", "/api/vendors", timeout=10).get("items", [])

    def site(self, site_id):''')

    s = s.replace('''    def sites(self):
        return self._request("GET", "/api/sites").get("items", [])''',
'''    def sites(self, vendor=""):
        q = ("?vendor=" + urllib.parse.quote(vendor)) if vendor else ""
        return self._request("GET", "/api/sites" + q).get("items", [])''')

    io.open(p, 'w', encoding='utf-8').write(s)
    print('api.py 加了邀请码接口')

# ---------------- app.py ----------------
p2 = 'viewer/app.py'
t = io.open(p2, encoding='utf-8').read()

# 1) 工具栏加厂商筛选
old = '''        self.lbl_status = ttk.Label(top, text="未连接", foreground="#8a97a8")
        self.lbl_status.pack(side="right")'''
new = '''        ttk.Label(top, text="厂商", foreground="#6b7a90").pack(side="left", padx=(12, 0))
        self.cmb_vendor = ttk.Combobox(top, width=18, state="readonly", values=["全部"])
        self.cmb_vendor.set("全部")
        self.cmb_vendor.pack(side="left", padx=(6, 0))
        self.cmb_vendor.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())

        self.lbl_status = ttk.Label(top, text="未连接", foreground="#8a97a8")
        self.lbl_status.pack(side="right")'''
assert old in t
t = t.replace(old, new)

# 2) 表格加「厂商」列
t = t.replace('''        cols = ("sel", "name", "detail", "who", "time", "size")''',
              '''        cols = ("sel", "name", "vendor", "detail", "who", "time", "size")''')
t = t.replace('''        widths = {"sel": 30, "name": 175, "detail": 225, "who": 95, "time": 105, "size": 62}
        titles = {"sel": "选", "name": "名称 / 文件", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小"}''',
'''        widths = {"sel": 30, "name": 150, "vendor": 110, "detail": 190, "who": 88, "time": 100, "size": 60}
        titles = {"sel": "选", "name": "名称 / 文件", "vendor": "厂商", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小"}''')

# 3) 站点行填厂商
t = t.replace('''            self.tree.insert("", "end", iid=iid, text="", values=(
                "☐",
                it.get("name", ""),
                it.get("address") or "（未填地址）",''',
'''            self.tree.insert("", "end", iid=iid, text="", values=(
                "☐",
                it.get("name", ""),
                it.get("vendor") or "—",
                it.get("address") or "（未填地址）",''')

# 任务/文件行补一列占位
t = t.replace('''            self.tree.insert(iid, "end", iid=tid, text="", values=(
                "☐", label, "区域任务", "照片 %d · 视频 %d" % (len(photos), len(videos)), "", ""))''',
'''            self.tree.insert(iid, "end", iid=tid, text="", values=(
                "☐", label, "", "区域任务", "照片 %d · 视频 %d" % (len(photos), len(videos)), "", ""))''')
t = t.replace('''                self.tree.insert(tid, "end", iid=fid, text="", values=(
                    "☐",
                    f.get("filename", ""),
                    "%s · %s" % (label, "照片" if f.get("kind") == "photo" else "视频"),''',
'''                self.tree.insert(tid, "end", iid=fid, text="", values=(
                    "☐",
                    f.get("filename", ""),
                    "",
                    "%s · %s" % (label, "照片" if f.get("kind") == "photo" else "视频"),''')

# 4) do_refresh 带上厂商筛选
t = t.replace('''    def do_refresh(self):''', '''    def do_refresh(self):
        vendor = "" if self.cmb_vendor.get() in ("全部", "") else self.cmb_vendor.get()
        self.vendor_filter = vendor''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('app.py 厂商列/筛选已加')
