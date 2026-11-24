import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

block = '''    def delete_checked_sites(self):
        sites = [self.site_rows[i] for i in self.checked if i in self.site_rows]
        if not sites:
            messagebox.showinfo(APP_NAME, "先在树里勾选采集点（点最左边的方框）")
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
            messagebox.showinfo(APP_NAME, "先在树里勾选文件（点最左边的方框）")
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

    def download_checked(self):'''

s = s.replace('    def download_checked(self):', block, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('delete handlers restored')
