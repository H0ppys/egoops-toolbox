import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 底部改为三行：文件操作 / 采集点操作 / 其他
old_start = s.index('        row1 = ttk.Frame(bottom)')
old_end = s.index('        self.progress = ttk.Progressbar(bottom')
new_bottom = '''        row1 = ttk.Frame(bottom)
        row1.pack(fill="x")
        ttk.Label(row1, text="文件：", foreground="#6b7a90").pack(side="left")
        self.btn_dl_checked = ttk.Button(row1, text="下载勾选文件（0）", style="Big.TButton", command=self.download_checked)
        self.btn_dl_checked.pack(side="left")
        self.btn_check_all = ttk.Button(row1, text="全选文件", command=self.toggle_all_checks)
        self.btn_check_all.pack(side="left", padx=6)
        self.btn_del_files = ttk.Button(row1, text="删除勾选文件", command=self.delete_checked_files)
        self.btn_del_files.pack(side="left", padx=6)
        self.btn_dl = ttk.Button(row1, text="下载当前选中文件", command=self.download_selected)
        self.btn_dl.pack(side="left", padx=6)

        row2 = ttk.Frame(bottom)
        row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="采集点：", foreground="#6b7a90").pack(side="left")
        self.btn_dl_sites = ttk.Button(row2, text="下载勾选采集点（0）", style="Big.TButton", command=self.download_checked_sites)
        self.btn_dl_sites.pack(side="left")
        self.btn_check_sites = ttk.Button(row2, text="全选采集点", command=self.toggle_all_sites)
        self.btn_check_sites.pack(side="left", padx=6)
        self.btn_del_sites = ttk.Button(row2, text="删除勾选采集点", command=self.delete_checked_sites)
        self.btn_del_sites.pack(side="left", padx=6)
        self.btn_dl_all = ttk.Button(row2, text="下载这个采集点全部", command=self.download_site)
        self.btn_dl_all.pack(side="left", padx=6)
        self.btn_open = ttk.Button(row2, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left", padx=6)

'''
s = s[:old_start] + new_bottom + s[old_end:]

# 2) 删除方法（插到 download_checked_sites 之前）
anchor = '    def download_checked_sites(self):'
delete_code = '''    def delete_checked_sites(self):
        if not self.checked_sites:
            messagebox.showinfo(APP_NAME, "先在左边勾选要删除的采集点")
            return
        names = [x.get("name", "") for x in self.sites if x["id"] in self.checked_sites]
        preview = "\\n".join("· " + n for n in names[:12])
        if len(names) > 12:
            preview += "\\n… 还有 %d 个" % (len(names) - 12)
        if not messagebox.askyesno(
                "确认删除",
                "将永久删除 %d 个采集点，以及它们的全部照片和视频：\\n\\n%s\\n\\n删除后无法恢复，确定吗？" % (len(names), preview),
                icon="warning"):
            return

        def work():
            ok = fail = 0
            for sid in list(self.checked_sites):
                try:
                    self.api.delete_site(sid)
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_sites, ok, fail)

        self.busy = True
        self.lbl_task.config(text="正在删除…")
        threading.Thread(target=work, daemon=True).start()

    def after_delete_sites(self, ok, fail):
        self.busy = False
        self.checked_sites.clear()
        self.update_site_check_label()
        self.lbl_task.config(text="已删除 %d 个，失败 %d 个" % (ok, fail))
        messagebox.showinfo(APP_NAME, "删除完成：成功 %d 个，失败 %d 个" % (ok, fail))
        self.do_refresh()
        self.tv_files.delete(*self.tv_files.get_children())
        self.files = []
        self.checked = set()
        self.update_check_label()
        self.preview.config(image="", text="（选中照片可预览，视频双击用系统播放器打开）")

    def delete_checked_files(self):
        if not self.checked:
            messagebox.showinfo(APP_NAME, "先在右边勾选要删除的文件")
            return
        names = [f.get("filename", "") for f in self.files if f["id"] in self.checked]
        preview = "\\n".join("· " + n for n in names[:12])
        if len(names) > 12:
            preview += "\\n… 还有 %d 个" % (len(names) - 12)
        if not messagebox.askyesno(
                "确认删除",
                "将永久删除 %d 个文件：\\n\\n%s\\n\\n删除后无法恢复，确定吗？" % (len(names), preview),
                icon="warning"):
            return

        def work():
            ok = fail = 0
            for fid in list(self.checked):
                try:
                    self.api.delete_file(fid)
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_files, ok, fail)

        self.busy = True
        self.lbl_task.config(text="正在删除…")
        threading.Thread(target=work, daemon=True).start()

    def after_delete_files(self, ok, fail):
        self.busy = False
        self.checked.clear()
        self.update_check_label()
        self.lbl_task.config(text="已删除 %d 个文件，失败 %d 个" % (ok, fail))
        messagebox.showinfo(APP_NAME, "删除完成：成功 %d 个，失败 %d 个" % (ok, fail))
        if self.current_site:
            self.on_site_select()

'''
s = s.replace(anchor, delete_code + anchor, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('delete buttons patched')
