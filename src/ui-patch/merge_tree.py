import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 布局：左右两表合并成一个树 ----------
start = s.index('        # ---------- 主体 ----------')
end = s.index('        # ---------- 底部操作区 ----------')
new_body = '''        # ---------- 主体：一个树形表 ----------
        body = ttk.Frame(self.root, padding=(14, 0, 14, 0))
        body.pack(fill="both", expand=True, pady=(0, 6))

        self.lbl_site = ttk.Label(body, text="采集点（点开左侧三角展开任务和文件）", style="Title.TLabel")
        self.lbl_site.pack(anchor="w", pady=(0, 6))

        cols = ("sel", "name", "detail", "who", "time", "size")
        self.tree = ttk.Treeview(body, columns=cols, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=26, stretch=False)
        for c, t, w in zip(cols, ("选", "名称 / 文件", "地址 / 区域·任务 / 类型", "采集员 / 数量", "时间", "大小"),
                           (34, 200, 300, 110, 120, 70)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w" if c in ("name", "detail") else "center")

        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double)

        self.preview = tk.Label(body, text="选中照片可预览；视频双击用系统播放器打开",
                                anchor="center", background="#f4f6fa", foreground="#8a97a8")
        self.preview.pack(fill="both", expand=False, pady=(8, 0), ipady=8)

'''
s = s[:start] + new_body + s[end:]

# ---------- 2) 列表逻辑：整段替换 ----------
start = s.index('    # ---------------------------------------------------------------- 列表')
end = s.index('    # ---------------------------------------------------------------- 下载')
new_list = '''    # ---------------------------------------------------------------- 树形列表

    def fill_sites(self, items):
        self.sites = items
        self.site_rows.clear()
        self.file_rows.clear()
        self.checked = set()
        self.update_check_label()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for it in items:
            iid = "site:" + it["id"]
            self.site_rows[iid] = it
            self.tree.insert("", "end", iid=iid, text="", values=(
                "☐",
                it.get("name", ""),
                it.get("address") or "（未填地址）",
                "%s · %d文件" % (it.get("created_by", ""), it.get("file_count", 0)),
                (it.get("created_at") or "").replace("T", " ")[:16],
                human_size(it.get("bytes", 0)),
            ))
            self.tree.insert(iid, "end", iid=iid + ":loading", text="", values=("", "加载中…", "", "", "", ""))
        self.set_status("已连接 · 采集点 %d 个" % len(items), "#1f7a3d")
        self.lbl_site.config(text="采集点（点开左侧三角展开任务和文件）")

    def on_tree_open(self, event):
        iid = self.tree.focus()
        if not iid.startswith("site:") or iid in self.loaded_sites:
            return
        self.loaded_sites.add(iid)
        site = self.site_rows.get(iid)

        def work():
            try:
                detail = self.api.site(site["id"])
                self.ui(self.fill_detail, iid, detail)
            except Exception as e:
                self.ui(self.set_status, "读取文件失败：%s" % e, "#b3261e")

        threading.Thread(target=work, daemon=True).start()

    def fill_detail(self, iid, detail):
        for ch in self.tree.get_children(iid):
            self.tree.delete(ch)
        tasks = detail.get("tasks") or []
        if not tasks:
            self.tree.insert(iid, "end", text="", values=("", "（没有任务）", "", "", "", ""))
            return
        for t in tasks:
            tid = "%s:task:%s" % (iid, t.get("id") or t.get("name"))
            area = (t.get("area") or "").strip()
            label = (area + "：" if area else "") + (t.get("name") or "")
            photos = t.get("photos") or []
            videos = t.get("videos") or []
            self.tree.insert(iid, "end", iid=tid, text="", values=(
                "☐", label, "区域任务", "照片 %d · 视频 %d" % (len(photos), len(videos)), "", ""))
            for f in photos + videos:
                fid = "file:" + f["id"]
                self.file_rows[fid] = f
                self.tree.insert(tid, "end", iid=fid, text="", values=(
                    "☐",
                    f.get("filename", ""),
                    "%s · %s" % (label, "照片" if f.get("kind") == "photo" else "视频"),
                    "照片" if f.get("kind") == "photo" else "视频",
                    (f.get("created_at") or "").replace("T", " ")[:16],
                    human_size(f.get("size", 0)),
                ))
        self.tree.item(iid, open=True)

    def on_tree_click(self, event):
        if self.tree.identify("region", event.x, event.y) != "cell":
            return None
        if self.tree.identify_column(event.x) != "#1":
            return None
        iid = self.tree.identify_row(event.y)
        if not iid:
            return None
        cur = self.tree.set(iid, "sel")
        new = "☑" if cur != "☑" else "☐"
        self.tree.set(iid, "sel", new)
        if new == "☑":
            self.checked.add(iid)
        else:
            self.checked.discard(iid)
        self.update_check_label()
        return "break"

    def on_tree_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid or not iid.startswith("file:"):
            return
        f = self.file_rows.get(iid)
        if f:
            self.download_files([f], open_after=True)

    def update_check_label(self):
        self.btn_dl_checked.config(text="下载勾选（%d）" % len(self.checked))
        self.btn_dl_sites.config(text="下载勾选（%d）" % len(self.checked))

    def checked_files(self):
        """勾选的文件 + 勾选采集点下的所有文件"""
        out = []
        seen = set()
        for iid in self.checked:
            if iid in self.file_rows:
                f = self.file_rows[iid]
                if f["id"] not in seen:
                    seen.add(f["id"])
                    out.append(f)
        for iid in self.checked:
            if iid.startswith("site:"):
                for child in self.tree.get_children(iid):
                    for task in self.tree.get_children(child):
                        for f_iid in self.tree.get_children(task):
                            f = self.file_rows.get(f_iid)
                            if f and f["id"] not in seen:
                                seen.add(f["id"])
                                out.append(f)
                # 没展开的先展开
        return out

    def toggle_all_checks(self):
        all_rows = []
        for iid in self.tree.get_children():
            all_rows.append(iid)
        all_checked = all(self.tree.set(i, "sel") == "☑" for i in all_rows) if all_rows else False
        for i in all_rows:
            self.tree.set(i, "sel", "☐" if all_checked else "☑")
        for i in all_rows:
            if all_checked:
                self.checked.discard(i)
            else:
                self.checked.add(i)
        self.update_check_label()

    def toggle_all_sites(self):
        self.toggle_all_checks()

    def download_checked_sites(self):
        self.download_checked()

    def download_site(self):
        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return
        self.lbl_task.config(text="读取中…")

        def work():
            try:
                detail = self.api.site(site["id"])
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "读取失败：%s" % e)
                return
            files = []
            for t in detail.get("tasks") or []:
                files += (t.get("photos") or []) + (t.get("videos") or [])
            self.ui(self.download_files, files, False)

        threading.Thread(target=work, daemon=True).start()

    def update_site_check_label(self):
        pass

'''
s = s[:start] + new_list + s[end:]

io.open(p, 'w', encoding='utf-8').write(s)
print('tree merged')
