import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 采集点列表加勾选列
s = s.replace('''        cols = ("name", "by", "time", "scene", "area", "tasks", "count", "size")
        self.tv_sites = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, t, w in zip(cols, ("门店", "采集员", "时间", "场景分类", "面积", "任务", "文件", "大小"),
                           (180, 75, 125, 150, 55, 45, 45, 75)):
            self.tv_sites.heading(c, text=t)
            self.tv_sites.column(c, width=w, anchor="w" if c in ("name", "scene") else "center")
        self.tv_sites.pack(fill="both", expand=True)
        self.tv_sites.bind("<<TreeviewSelect>>", lambda e: self.on_site_select())''',
              '''        cols = ("sel", "name", "by", "time", "scene", "area", "tasks", "count", "size")
        self.tv_sites = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, t, w in zip(cols, ("选", "门店", "采集员", "时间", "场景分类", "面积", "任务", "文件", "大小"),
                           (36, 170, 70, 120, 140, 50, 40, 40, 70)):
            self.tv_sites.heading(c, text=t)
            self.tv_sites.column(c, width=w, anchor="w" if c in ("name", "scene") else "center")
        self.tv_sites.pack(fill="both", expand=True)
        self.tv_sites.bind("<<TreeviewSelect>>", lambda e: self.on_site_select())
        self.tv_sites.bind("<Button-1>", self.on_site_click)''')

# 2) 底部两行
s = s.replace('''        self.btn_dl = ttk.Button(bottom, text="下载选中文件", style="Big.TButton", command=self.download_selected)
        self.btn_dl.pack(side="left")
        self.btn_dl_checked = ttk.Button(bottom, text="下载勾选", style="Big.TButton", command=self.download_checked)
        self.btn_dl_checked.pack(side="left", padx=8)
        self.btn_check_all = ttk.Button(bottom, text="全选", command=self.toggle_all_checks)
        self.btn_check_all.pack(side="left")
        self.btn_dl_all = ttk.Button(bottom, text="下载这个采集点全部", style="Big.TButton", command=self.download_site)
        self.btn_dl_all.pack(side="left", padx=8)
        self.btn_open = ttk.Button(bottom, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left")''',
              '''        row1 = ttk.Frame(bottom)
        row1.pack(fill="x")
        self.btn_dl_checked = ttk.Button(row1, text="下载勾选文件（0）", style="Big.TButton", command=self.download_checked)
        self.btn_dl_checked.pack(side="left")
        self.btn_check_all = ttk.Button(row1, text="全选文件", command=self.toggle_all_checks)
        self.btn_check_all.pack(side="left", padx=6)
        self.btn_dl = ttk.Button(row1, text="下载当前选中文件", command=self.download_selected)
        self.btn_dl.pack(side="left", padx=6)
        self.btn_dl_all = ttk.Button(row1, text="下载这个采集点全部", command=self.download_site)
        self.btn_dl_all.pack(side="left", padx=6)

        row2 = ttk.Frame(bottom)
        row2.pack(fill="x", pady=(8, 0))
        self.btn_dl_sites = ttk.Button(row2, text="下载勾选的采集点（0）", style="Big.TButton", command=self.download_checked_sites)
        self.btn_dl_sites.pack(side="left")
        self.btn_check_sites = ttk.Button(row2, text="全选采集点", command=self.toggle_all_sites)
        self.btn_check_sites.pack(side="left", padx=6)
        self.btn_open = ttk.Button(row2, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left", padx=6)''')

# 3) checked_sites 初始化
s = s.replace('''        self.files = []
        self.checked = set()''', '''        self.files = []
        self.checked = set()
        self.checked_sites = set()''')

# 4) 采集点行插入时带勾选列
s = s.replace('''            self.tv_sites.insert("", "end", iid=it["id"], values=(
                it.get("name", ""),''', '''            self.tv_sites.insert("", "end", iid=it["id"], values=(
                "☐",
                it.get("name", ""),''')

# 5) 采集点勾选逻辑 + 批量下载
s = s.replace('''    # ---------- 勾选框 ----------

    def on_file_click(self, event):''', '''    # ---------- 勾选框 ----------

    def on_site_click(self, event):
        if self.tv_sites.identify("region", event.x, event.y) != "cell":
            return None
        if self.tv_sites.identify_column(event.x) != "#1":
            return None
        item = self.tv_sites.identify_row(event.y)
        if not item:
            return None
        cur = self.tv_sites.set(item, "sel")
        new = "☑" if cur != "☑" else "☐"
        self.tv_sites.set(item, "sel", new)
        if new == "☑":
            self.checked_sites.add(item)
        else:
            self.checked_sites.discard(item)
        self.update_site_check_label()
        return "break"

    def update_site_check_label(self):
        self.btn_dl_sites.config(text="下载勾选的采集点（%d）" % len(self.checked_sites))

    def toggle_all_sites(self):
        items = self.tv_sites.get_children()
        all_on = len(self.checked_sites) == len(items) and items
        for iid in items:
            self.tv_sites.set(iid, "sel", "☐" if all_on else "☑")
        self.checked_sites = set() if all_on else set(items)
        self.update_site_check_label()

    def download_checked_sites(self):
        if not self.checked_sites:
            messagebox.showinfo(APP_NAME, "先在左边勾选要下载的采集点（点最左边的方框）")
            return
        if self.busy:
            messagebox.showinfo(APP_NAME, "正在下载，请稍等")
            return
        target = self.ask_dir()
        if not target:
            return
        sites = [s for s in self.sites if s["id"] in self.checked_sites]
        self.busy = True
        self.progress["value"] = 0
        self.progress["maximum"] = 100

        def work():
            ok = fail = 0
            for i, s in enumerate(sites, 1):
                self.ui(self.lbl_task.config, text="采集点 %d/%d：%s" % (i, len(sites), s.get("name", "")))
                try:
                    detail = self.api.site(s["id"])
                except Exception:
                    fail += 1
                    continue
                folder = os.path.join(target, "".join(c for c in (s.get("name") or "采集点") if c not in '\\\\/:*?"<>|').strip() or "采集点")
                files = []
                for t in detail.get("tasks") or []:
                    files += (t.get("photos") or []) + (t.get("videos") or [])
                for f in files:
                    name = f.get("filename") or (f["id"] + ".bin")
                    dest = os.path.join(folder, name)
                    if os.path.exists(dest):
                        stem, ext = os.path.splitext(name)
                        dest = os.path.join(folder, "%s_%s%s" % (stem, f["id"][:6], ext))
                    try:
                        self.api.download("/files/" + f["id"], dest)
                        ok += 1
                    except Exception:
                        fail += 1
                self.ui(self.set_progress, i, len(sites))
            self.ui(self.download_done, ok, fail, target, False, [])

        threading.Thread(target=work, daemon=True).start()

    def on_file_click(self, event):''')

# 6) 文件勾选按钮文案
s = s.replace('''    def update_check_label(self):
        self.btn_dl_checked.config(text="下载勾选（%d）" % len(self.checked))''', '''    def update_check_label(self):
        self.btn_dl_checked.config(text="下载勾选文件（%d）" % len(self.checked))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('viewer patched')
