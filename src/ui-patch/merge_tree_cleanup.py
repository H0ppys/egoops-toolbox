import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) __init__ 增加容器
s = s.replace('''        self.files = []
        self.checked = set()
        self.checked_sites = set()''', '''        self.files = []
        self.checked = set()
        self.checked_sites = set()
        self.site_rows = {}
        self.file_rows = {}
        self.loaded_sites = set()''')

# 2) 删掉旧的站点选择/文件列表方法块（on_site_select ... selected_file）
def cut(start_marker, end_marker):
    global s
    i = s.index(start_marker)
    j = s.index(end_marker)
    s = s[:i] + s[j:]

cut('    def on_site_select(self):', '    # ---------------------------------------------------------------- 预览')

# 3) 删掉旧的 on_site_click / toggle_all_sites / update_site_check_label 旧实现
if '    def on_site_click(self, event):' in s:
    cut('    def on_site_click(self, event):', '    def download_checked_sites(self):')

# 4) download_selected 用树里的焦点文件
s = s.replace('''    def download_selected(self):
        f = self.selected_file()
        if not f:
            messagebox.showinfo(APP_NAME, "先在右边选中一个文件")
            return
        self.download_files([f])''', '''    def download_selected(self):
        iid = self.tree.focus()
        f = self.file_rows.get(iid)
        if not f:
            messagebox.showinfo(APP_NAME, "先在树里选中一个文件")
            return
        self.download_files([f])''')

# 5) 删除勾选：改成树
i = s.index('    def delete_checked_sites(self):')
j = s.index('    def on_file_click(self, event):')
new_del = '''    def delete_checked_sites(self):
        sites = [self.site_rows[i] for i in self.checked if i in self.site_rows]
        if not sites:
            messagebox.showinfo(APP_NAME, "先在树里勾选采集点")
            return
        names = [x.get("name", "") for x in sites]
        preview = "\\n".join("· " + n for n in names[:12])
        if not messagebox.askyesno("确认删除",
                                   "将永久删除 %d 个采集点及其全部照片视频：\\n\\n%s\\n\\n删除后无法恢复，确定吗？"
                                   % (len(names), preview), icon="warning"):
            return

        def work():
            ok = fail = 0
            for site in sites:
                try:
                    self.api.delete_site(site["id"])
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_sites, ok, fail)

        self.lbl_task.config(text="正在删除…")
        threading.Thread(target=work, daemon=True).start()

    def after_delete_sites(self, ok, fail):
        self.checked.clear()
        self.update_check_label()
        self.lbl_task.config(text="已删除 %d 个，失败 %d 个" % (ok, fail))
        messagebox.showinfo(APP_NAME, "删除完成：成功 %d 个，失败 %d 个" % (ok, fail))
        self.do_refresh()

    def delete_checked_files(self):
        files = [self.file_rows[i] for i in self.checked if i in self.file_rows]
        if not files:
            messagebox.showinfo(APP_NAME, "先在树里勾选文件")
            return
        names = [f.get("filename", "") for f in files]
        preview = "\\n".join("· " + n for n in names[:12])
        if not messagebox.askyesno("确认删除",
                                   "将永久删除 %d 个文件：\\n\\n%s\\n\\n删除后无法恢复，确定吗？"
                                   % (len(names), preview), icon="warning"):
            return

        def work():
            ok = fail = 0
            for f in files:
                try:
                    self.api.delete_file(f["id"])
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_files, ok, fail)

        self.lbl_task.config(text="正在删除…")
        threading.Thread(target=work, daemon=True).start()

    def after_delete_files(self, ok, fail):
        self.checked.clear()
        self.update_check_label()
        self.lbl_task.config(text="已删除 %d 个文件，失败 %d 个" % (ok, fail))
        messagebox.showinfo(APP_NAME, "删除完成：成功 %d 个，失败 %d 个" % (ok, fail))
        self.do_refresh()

    def on_file_click(self, event):'''
s = s[:i] + new_del + s[j + len('    def on_file_click(self, event):'):]

# 6) 删掉 on_file_click 之后的旧实现块（到 预览 前）
if '    def on_file_click(self, event):' in s:
    cut('    def on_file_click(self, event):', '    # ---------------------------------------------------------------- 预览')

# 7) selftest 用新的 tree
s = s.replace('cols=%s\\n" % (app.ent_server.get(), ",".join(app.tv_sites["columns"]))',
              'cols=%s\\n" % (app.ent_server.get(), ",".join(app.tree["columns"]))')

io.open(p, 'w', encoding='utf-8').write(s)
print('cleanup patched')
