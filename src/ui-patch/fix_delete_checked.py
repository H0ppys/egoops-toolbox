"""修两个问题：
   1) 刷新时在工作线程里调 root.after() 导致异常（草稿自动同步因此失效）
   2) 删除勾选：勾了采集点但没展开时拿到 0 个文件 → 现在自动去服务器取该采集点的文件再删
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 线程里不能碰 tkinter：改成 ui 回调
s = s.replace('                self.root.after(300, self.auto_sync_drafts)',
              '                self.ui(self.auto_sync_drafts)')

# 2) 删除勾选：把「采集点」展开成文件
old = '''    def delete_checked_files(self):
        files = self.checked_files()
        if not files:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return'''
new = '''    def delete_checked_files(self):
        files = self.checked_files()
        sites = self._checked_sites()

        if not files and not sites:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return

        # 勾了采集点但还没展开：去服务器取它的文件
        if not files and sites:
            self.lbl_task.config(text="正在读取勾选采集点的文件…")

            def fetch():
                got = []
                for site in sites:
                    try:
                        detail = self.api.site(site["id"])
                    except Exception:
                        continue
                    for t in detail.get("tasks") or []:
                        got += (t.get("photos") or []) + (t.get("videos") or [])
                self.ui(self._confirm_delete_files, got)

            threading.Thread(target=fetch, daemon=True).start()
            return

        self._confirm_delete_files(files)

    def _confirm_delete_files(self, files):
        if not files:
            self.lbl_task.config(text="勾选的采集点里没有文件")
            messagebox.showinfo(APP_NAME, "勾选的采集点里没有文件")
            return'''
assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('已修：线程调用 + 删除勾选回退取文件')
