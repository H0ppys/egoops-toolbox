import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    # ---------------------------------------------------------------- 布局')
end = s.index('    # ---------------------------------------------------------------- 邀请码')

new_build = '''    # ---------------------------------------------------------------- 布局

    def _build(self):
        # ---------- 顶部工具条 ----------
        top = ttk.Frame(self.root, padding=(14, 10, 14, 6))
        top.pack(fill="x")

        ttk.Label(top, text="服务器", foreground="#6b7a90").pack(side="left")
        self.ent_server = ttk.Entry(top, width=30, font=("Consolas", 10))
        self.ent_server.pack(side="left", padx=(6, 12))

        ttk.Label(top, text="姓名", foreground="#6b7a90").pack(side="left")
        self.ent_name = ttk.Entry(top, width=10)
        self.ent_name.pack(side="left", padx=(6, 10))

        self.btn_connect = ttk.Button(top, text="连接", style="Primary.TButton", command=self.do_connect)
        self.btn_connect.pack(side="left")
        self.btn_refresh = ttk.Button(top, text="刷新", command=self.do_refresh)
        self.btn_refresh.pack(side="left", padx=6)
        self.btn_settings = ttk.Button(top, text="设置", command=self.open_settings)
        self.btn_settings.pack(side="left")

        self.lbl_invite = ttk.Label(top, text="邀请码")
        self.ent_invite = ttk.Entry(top, width=12, show="*")
        self.lbl_invite.pack_forget()
        self.ent_invite.pack_forget()

        self.lbl_status = ttk.Label(top, text="未连接", foreground="#8a97a8")
        self.lbl_status.pack(side="right")

        # ---------- 主体 ----------
        body = ttk.PanedWindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        left = ttk.Labelframe(body, text=" 采集点 ", padding=8)
        body.add(left, weight=2)

        cols = ("sel", "name", "address", "by", "time", "scene", "area", "tasks", "count", "size")
        self.tv_sites = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, t, w in zip(cols, ("选", "门店", "现场地址", "采集员", "时间", "场景分类", "面积", "任务", "文件", "大小"),
                           (34, 140, 200, 58, 100, 105, 46, 38, 38, 62)):
            self.tv_sites.heading(c, text=t)
            self.tv_sites.column(c, width=w, anchor="w" if c in ("name", "address", "scene") else "center")
        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tv_sites.yview)
        self.tv_sites.configure(yscrollcommand=vsb.set)
        self.tv_sites.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tv_sites.bind("<<TreeviewSelect>>", lambda e: self.on_site_select())
        self.tv_sites.bind("<Button-1>", self.on_site_click)

        right = ttk.Labelframe(body, text=" 文件 ", padding=8)
        body.add(right, weight=3)

        self.lbl_site = ttk.Label(right, text="选中左边的采集点", style="Title.TLabel")
        self.lbl_site.pack(anchor="w", pady=(0, 6))

        cols2 = ("sel", "area", "task", "kind", "name", "size", "time")
        self.tv_files = ttk.Treeview(right, columns=cols2, show="headings", height=9)
        for c, t, w in zip(cols2, ("选", "区域", "任务", "类型", "文件名", "大小", "上传时间"), (34, 66, 86, 42, 158, 60, 100)):
            self.tv_files.heading(c, text=t)
            self.tv_files.column(c, width=w, anchor="center" if c != "name" else "w")
        fsb = ttk.Scrollbar(right, orient="vertical", command=self.tv_files.yview)
        self.tv_files.configure(yscrollcommand=fsb.set)
        self.tv_files.pack(side="left", fill="both", expand=True)
        fsb.pack(side="right", fill="y")
        self.tv_files.bind("<<TreeviewSelect>>", lambda e: self.on_file_select())
        self.tv_files.bind("<Double-1>", lambda e: self.preview_file())
        self.tv_files.bind("<Button-1>", self.on_file_click)

        self.preview = tk.Label(right, text="选中照片可预览；视频双击用系统播放器打开",
                                anchor="center", background="#f4f6fa", foreground="#8a97a8")
        self.preview.pack(fill="both", expand=False, pady=(8, 0), ipady=10)

        # ---------- 底部操作区 ----------
        bottom = ttk.Frame(self.root, padding=(14, 4, 14, 12))
        bottom.pack(side="bottom", fill="x", before=body)

        row1 = ttk.Frame(bottom)
        row1.pack(fill="x")
        ttk.Label(row1, text="文件", style="Group.TLabel").pack(side="left")
        self.btn_dl_checked = ttk.Button(row1, text="下载勾选（0）", style="Primary.TButton", command=self.download_checked)
        self.btn_dl_checked.pack(side="left")
        self.btn_check_all = ttk.Button(row1, text="全选", command=self.toggle_all_checks)
        self.btn_check_all.pack(side="left", padx=6)
        self.btn_del_files = ttk.Button(row1, text="删除勾选", style="Danger.TButton", command=self.delete_checked_files)
        self.btn_del_files.pack(side="left")
        self.btn_dl = ttk.Button(row1, text="下载当前选中", command=self.download_selected)
        self.btn_dl.pack(side="left", padx=6)

        ttk.Separator(row1, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Label(row1, text="进度", style="Group.TLabel").pack(side="left")
        self.progress = ttk.Progressbar(row1, mode="determinate", length=200)
        self.progress.pack(side="left", padx=(6, 10))
        self.lbl_task = ttk.Label(row1, text="", foreground="#8a97a8")
        self.lbl_task.pack(side="left")

        row2 = ttk.Frame(bottom)
        row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="采集点", style="Group.TLabel").pack(side="left")
        self.btn_dl_sites = ttk.Button(row2, text="下载勾选（0）", style="Primary.TButton", command=self.download_checked_sites)
        self.btn_dl_sites.pack(side="left")
        self.btn_check_sites = ttk.Button(row2, text="全选", command=self.toggle_all_sites)
        self.btn_check_sites.pack(side="left", padx=6)
        self.btn_del_sites = ttk.Button(row2, text="删除勾选", style="Danger.TButton", command=self.delete_checked_sites)
        self.btn_del_sites.pack(side="left")
        self.btn_dl_all = ttk.Button(row2, text="下载这个采集点全部", command=self.download_site)
        self.btn_dl_all.pack(side="left", padx=6)
        self.btn_open = ttk.Button(row2, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left", padx=6)

        row3 = ttk.Frame(bottom)
        row3.pack(fill="x", pady=(8, 0))
        ttk.Label(row3, text="美团", style="Group.TLabel").pack(side="left")
        self.btn_draft = ttk.Button(row3, text="生成草稿（先核对）", style="Primary.TButton", command=self.show_draft)
        self.btn_draft.pack(side="left")
        self.btn_fill = ttk.Button(row3, text="申请采集点（自动填表）", command=self.fill_egoops)
        self.btn_fill.pack(side="left", padx=6)
        ttk.Label(row3, text="用保存的登录态打开 EgoOps，只建草稿、不提交审核",
                  foreground="#8a97a8").pack(side="left", padx=8)

    # ---------------------------------------------------------------- 设置（服务器 / 大模型）

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("设置")
        win.geometry("560x430")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        # --- 服务器 ---
        tab1 = ttk.Frame(nb, padding=14)
        nb.add(tab1, text="服务器")
        ttk.Label(tab1, text="采集服务器地址").pack(anchor="w")
        e_server = ttk.Entry(tab1, font=("Consolas", 10))
        e_server.insert(0, self.ent_server.get())
        e_server.pack(fill="x", pady=(4, 12))
        ttk.Label(tab1, text="姓名（只用来记谁在看）").pack(anchor="w")
        e_name = ttk.Entry(tab1)
        e_name.insert(0, self.ent_name.get())
        e_name.pack(fill="x", pady=(4, 12))
        ttk.Label(tab1, text="下载目录").pack(anchor="w")
        e_dir = ttk.Entry(tab1)
        e_dir.insert(0, self.cfg.get("download_dir", ""))
        e_dir.pack(fill="x", pady=(4, 4))
        ttk.Button(tab1, text="选择…", command=lambda: self._pick_dir_into(e_dir)).pack(anchor="w")

        # --- 大模型 ---
        tab2 = ttk.Frame(nb, padding=14)
        nb.add(tab2, text="大模型 API")
        llm = self.cfg.get("llm") or {}
        ttk.Label(tab2, text="接口地址（OpenAI 兼容）").pack(anchor="w")
        e_base = ttk.Entry(tab2, font=("Consolas", 10))
        e_base.insert(0, llm.get("base") or "https://api.deepseek.com/v1")
        e_base.pack(fill="x", pady=(4, 10))

        ttk.Label(tab2, text="模型名").pack(anchor="w")
        e_model = ttk.Entry(tab2, font=("Consolas", 10))
        e_model.insert(0, llm.get("model") or "deepseek-chat")
        e_model.pack(fill="x", pady=(4, 10))

        ttk.Label(tab2, text="API Key").pack(anchor="w")
        e_key = ttk.Entry(tab2, show="*", font=("Consolas", 10))
        e_key.insert(0, llm.get("key") or "")
        e_key.pack(fill="x", pady=(4, 10))

        ttk.Label(tab2, text="用于：生成采集点描述、任务描述、SOP 步骤",
                  foreground="#8a97a8").pack(anchor="w", pady=(0, 8))

        out = ttk.Label(tab2, text="", foreground="#1f7a3d", wraplength=480, justify="left")
        out.pack(anchor="w", pady=(4, 0))

        def test_llm():
            base = e_base.get().strip().rstrip("/")
            model = e_model.get().strip()
            key = e_key.get().strip()
            if not key:
                out.config(text="先填 API Key", foreground="#b3261e")
                return
            out.config(text="测试中…", foreground="#8a97a8")

            def run():
                try:
                    import json as _j
                    import urllib.request as _u
                    payload = _j.dumps({
                        "model": model,
                        "messages": [{"role": "user", "content": "只回复两个字：可用"}],
                        "max_tokens": 16,
                    }).encode()
                    req = _u.Request(base + "/chat/completions", data=payload, method="POST")
                    req.add_header("Content-Type", "application/json")
                    req.add_header("Authorization", "Bearer " + key)
                    with _u.urlopen(req, timeout=30) as r:
                        data = _j.loads(r.read().decode())
                    text = data["choices"][0]["message"]["content"].strip()
                    self.ui(out.config, text="✓ 连接成功，模型回复：%s" % text, foreground="#1f7a3d")
                except Exception as e:
                    self.ui(out.config, text="✗ 失败：%s" % e, foreground="#b3261e")

            import threading as _t
            _t.Thread(target=run, daemon=True).start()

        ttk.Button(tab2, text="测试连接", command=test_llm).pack(anchor="w", pady=(6, 0))

        def save_all():
            self.cfg["server"] = e_server.get().strip()
            self.cfg["name"] = e_name.get().strip()
            self.cfg["download_dir"] = e_dir.get().strip()
            self.cfg["llm"] = {
                "base": e_base.get().strip(),
                "model": e_model.get().strip(),
                "key": e_key.get().strip(),
            }
            save_config(self.cfg)
            self.ent_server.delete(0, "end")
            self.ent_server.insert(0, self.cfg["server"])
            self.ent_name.delete(0, "end")
            self.ent_name.insert(0, self.cfg["name"])
            win.destroy()
            messagebox.showinfo(APP_NAME, "已保存")

        bar = ttk.Frame(win)
        bar.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(bar, text="保存", style="Primary.TButton", command=save_all).pack(side="right")
        ttk.Button(bar, text="取消", command=win.destroy).pack(side="right", padx=8)

    def _pick_dir_into(self, entry):
        d = filedialog.askdirectory(title="选择下载目录")
        if d:
            entry.delete(0, "end")
            entry.insert(0, d)

'''
s = s[:start] + new_build + s[end:]

# 样式：加 Primary / Danger / Group
s = s.replace('''        s.configure("Title.TLabel", font=("Microsoft YaHei UI", 13, "bold"))''',
'''        s.configure("Title.TLabel", font=("Microsoft YaHei UI", 12, "bold"))
        s.configure("Group.TLabel", font=("Microsoft YaHei UI", 10, "bold"), foreground="#6b7a90", width=6)
        s.configure("Primary.TButton", font=("Microsoft YaHei UI", 10, "bold"))
        s.configure("Danger.TButton", font=("Microsoft YaHei UI", 10), foreground="#b3261e")''')

io.open(p, 'w', encoding='utf-8').write(s)
print('viewer redesigned')
