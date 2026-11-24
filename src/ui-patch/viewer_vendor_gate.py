"""查看器：只有美团（KWQZB）走 EgoOps；其它厂商的提交流程没接入，按钮直接拦住。"""

import io

# ---------- api.py ----------
p = 'viewer/api.py'
s = io.open(p, encoding='utf-8').read()
if 'def vendor_systems' not in s:
    s = s.replace('''    def vendor_names(self):''', '''    def vendor_systems(self):
        return self._request("GET", "/api/vendor-systems", timeout=10).get("items", {})

    def vendor_names(self):''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('api: vendor_systems')

# ---------- app.py ----------
p2 = 'viewer/app.py'
t = io.open(p2, encoding='utf-8').read()

# 1) 初始化 + 载入
t = t.replace('''        self.vendor_names = {}''', '''        self.vendor_names = {}
        self.vendor_systems = {}''')

if 'load_vendor_systems' not in t:
    t = t.replace('''    def load_vendor_names(self):''', '''    def load_vendor_systems(self):
        try:
            self.vendor_systems = {str(k).upper(): v for k, v in (self.api.vendor_systems() or {}).items()}
        except Exception:
            pass

    def system_of(self, site):
        code = (site.get("invite") or "").strip().upper()
        return self.vendor_systems.get(code, "")

    def load_vendor_names(self):''')

    t = t.replace('''        self.load_vendor_names()''', '''        self.load_vendor_systems()
        self.load_vendor_names()''', 1)

# 2) 厂商列：非美团标注「其他系统」
t = t.replace('''        names = getattr(self, "vendor_names", None) or {}
        if up in names:
            return names[up]''',
'''        names = getattr(self, "vendor_names", None) or {}
        sysname = (getattr(self, "vendor_systems", None) or {}).get(up, "")
        suffix = "" if sysname in ("meituan", "") else " · 其他系统"
        if up in names:
            return names[up] + suffix''')

# 3) 一键建草稿 / 批量建草稿：非美团直接拦
if '_ensure_meituan' not in t:
    t = t.replace('''    def fill_egoops(self):''', '''    def _ensure_meituan(self, site):
        """只有美团走 EgoOps；其它厂商的提交流程还没接，别把数据推进美团账号"""
        code = (site.get("invite") or "").strip().upper()
        sysname = self.vendor_systems.get(code, "")
        if sysname == "meituan":
            return True
        vendor = self.vendor_names.get(code) or (code or "未填邀请码")
        messagebox.showwarning(
            APP_NAME,
            "这个采集点的厂商是「%s」，提交系统和美团 EgoOps 不一样。\\n\\n"
            "目前只接入了美团的 EgoOps，其它厂商还需要单独对接。\\n"
            "这个采集点你可以照常：下载素材、质检、导出表格。" % vendor)
        return False

    def fill_egoops(self):''')

    t = t.replace('''        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return

        labels = [''', '''        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return
        if not self._ensure_meituan(site):
            return

        labels = [''')

    t = t.replace('''    def batch_draft(self):
        sites = [self.site_rows[i] for i in self.checked if i in self.site_rows]''',
'''    def batch_draft(self):
        picked = [self.site_rows[i] for i in self.checked if i in self.site_rows]
        sites = []
        skipped_other = []
        for x in picked:
            if self._ensure_meituan(x):
                sites.append(x)
            else:
                skipped_other.append(x)
        if skipped_other and not sites:
            return''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('查看器：非美团厂商拦住建草稿')
