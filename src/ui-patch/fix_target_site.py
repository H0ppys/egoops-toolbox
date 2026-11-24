"""修：勾了采集点但没点行 → 提示"先选中"。
   1) 点勾选框时同时把该行设为选中
   2) 建草稿 / 质检 / 下载全部：优先当前行，没有就用勾选的第一条
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 点勾选框 = 也选中这一行
s = s.replace('''        want = self.tree.set(iid, "sel") != "☑"     # 点一下要变成的状态''',
'''        try:
            self.tree.focus(iid)
            self.tree.selection_set(iid)
        except Exception:
            pass
        want = self.tree.set(iid, "sel") != "☑"     # 点一下要变成的状态''')

# 2) 统一取目标采集点
if '_target_site' not in s:
    s = s.replace('''    def draft_text(self, site):''', '''    def _target_site(self):
        """当前选中的采集点；没选中就用勾选的第一条"""
        iid = self.tree.focus()
        if iid in self.site_rows:
            return self.site_rows[iid], iid
        for c in self.checked:
            if c in self.site_rows:
                try:
                    self.tree.focus(c)
                    self.tree.selection_set(c)
                except Exception:
                    pass
                return self.site_rows[c], c
        return None, None

    def draft_text(self, site):''')

# 3) 建草稿
s = s.replace('''        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return
        if not self._ensure_meituan(site):
            return''',
'''        site, iid = self._target_site()
        if not site:
            messagebox.showinfo(APP_NAME, "先勾选一个采集点（点最左边的方框）")
            return
        if not self._ensure_meituan(site):
            return''')

# 4) 质检
s = s.replace('''    def qc_site(self):
        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return''',
'''    def qc_site(self):
        site, iid = self._target_site()
        if not site:
            messagebox.showinfo(APP_NAME, "先勾选一个采集点（点最左边的方框）")
            return''')

# 5) 下载这个采集点全部
s = s.replace('''    def download_site(self):
        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return''',
'''    def download_site(self):
        site, iid = self._target_site()
        if not site:
            messagebox.showinfo(APP_NAME, "先勾选一个采集点（点最左边的方框）")
            return''')

# 6) 下载当前选中文件
s = s.replace('''    def download_selected(self):
        iid = self.tree.focus()
        f = self.file_rows.get(iid)''',
'''    def download_selected(self):
        iid = self.tree.focus()
        f = self.file_rows.get(iid)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('目标采集点取法已修')
