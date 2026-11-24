"""勾了采集点但没展开时，「下载勾选 / 删除勾选」也能用：
   拿不到已加载文件时，直接用勾选的采集点去服务器取文件列表。
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''    def download_checked(self):
        files = self.checked_files()
        if not files:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return
        self.download_files(files)'''
new = '''    def _checked_sites(self):
        return [self.site_rows[i] for i in self.checked if i in self.site_rows]

    def download_checked(self):
        files = self.checked_files()
        if files:
            self.download_files(files)
            return

        sites = self._checked_sites()
        if not sites:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return

        # 勾了采集点但还没展开：直接去服务器取文件
        self.lbl_task.config(text="读取勾选采集点的文件…")

        def work():
            all_files = []
            for site in sites:
                try:
                    detail = self.api.site(site["id"])
                except Exception:
                    continue
                for t in detail.get("tasks") or []:
                    all_files += (t.get("photos") or []) + (t.get("videos") or [])
            if not all_files:
                self.ui(messagebox.showinfo, APP_NAME, "勾选的采集点里没有文件")
                return
            self.ui(self.download_files, all_files, False)

        threading.Thread(target=work, daemon=True).start()'''
assert old in s
s = s.replace(old, new)

old2 = '''    def delete_checked_files(self):
        files = [self.file_rows[i] for i in self.checked if i in self.file_rows]
        if not files:
            messagebox.showinfo(APP_NAME, "先在树里勾选文件（点最左边的方框）")
            return'''
new2 = '''    def delete_checked_files(self):
        files = self.checked_files()
        if not files:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('下载/删除勾选 支持未展开的采集点')
