"""界面二轮重做：换成现代 ttk 主题（sv-ttk），布局简化成「列表 + 大按钮面板」。

要点：
  · 主题：sv-ttk light（Windows 11 风格），失败自动回退
  · 去掉花哨的四步卡片，改成一条状态条 + 一个大按钮（当前该做的事）
  · 列表：行高 40、字号 10.5，列精简为 选/门店/地址/厂商/时间/EgoOps
  · 点采集点自动展开，省一次双击
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 主题 ----------
if 'sv_ttk' not in s:
    s = s.replace('''    def _style(self):''', '''    def _apply_theme(self):
        try:
            import sv_ttk
            sv_ttk.set_theme("light")
            self.modern = True
        except Exception:
            self.modern = False

    def _style(self):''')

    # 在 __init__ 里、_build 之前应用主题
    s = s.replace('''        self._build()''', '''        self._apply_theme()
        self._build()''', 1)

# ---------- 2) 主体布局重写 ----------
start = s.index('    # ---------------------------------------------------------------- 布局')
end = s.index('    # ---------------------------------------------------------------- 设置（服务器 / 大模型）')

new = '''    # ---------------------------------------------------------------- 布局

    def _build(self):
        # ---------- 顶栏 ----------
        head = ttk.Frame(self.root, padding=(20, 14, 20, 6))
        head.pack(fill="x")

        ttk.Label(head, text="采集数据查看器", style="Title.TLabel").pack(side="left")
        ttk.Label(head, text="美团采集 · 质检 · 建草稿", style="Dim.TLabel").pack(side="left", padx=(12, 0), pady=(4, 0))
        self.lbl_status = ttk.Label(head, text="未连接", style="Status.TLabel")
        self.lbl_status.pack(side="right")

        # ---------- 服务器行 ----------
        bar = ttk.Frame(self.root, padding=(20, 0, 20, 8))
        bar.pack(fill="x")

        ttk.Entry(bar, textvariable=self.var_server, width=30, font=("Consolas", 10)).pack(side="left")
        ttk.Entry(bar, textvariable=self.var_name, width=8).pack(side="left", padx=(8, 8))
        self.btn_connect = ttk.Button(bar, text="连接", style="Accent.TButton", command=self.do_connect)
        self.btn_connect.pack(side="left")
        self.btn_refresh = ttk.Button(bar, text="刷新", command=self.do_refresh)
        self.btn_refresh.pack(side="left", padx=(6, 16))

        ttk.Entry(bar, textvariable=self.var_search, width=18).pack(side="left")
        self.cmb_range = ttk.Combobox(bar, textvariable=self.var_range, width=7, state="readonly",
                                      values=["全部", "今天", "近 7 天", "近 30 天"])
        self.cmb_range.pack(side="left", padx=(6, 6))
        self.cmb_vendor = ttk.Combobox(bar, textvariable=self.var_vendor, width=14, state="readonly", values=["全部"])
        self.cmb_vendor.pack(side="left")

        self.lbl_invite = ttk.Label(bar, text="")
        self.ent_invite = ttk.Entry(bar, width=8, show="*")
        self.cmb_vendor.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())
        self.cmb_range.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())
        self.var_search.trace_add("write", lambda *a: self._on_search_typing())

        # ---------- 主体：左列表 + 右操作 ----------
        body = ttk.Frame(self.root, padding=(20, 0, 20, 0))
        body.pack(fill="both", expand=True)

        # 左：列表
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)

        self.lbl_site = ttk.Label(left, text="采集点", style="Section.TLabel")
        self.lbl_site.pack(anchor="w", pady=(0, 6))

        wrap = ttk.Frame(left)
        wrap.pack(fill="both", expand=True)

        cols = ("sel", "name", "address", "vendor", "time", "draft")
        self.tree = ttk.Treeview(wrap, columns=cols, show="tree headings",
                                 selectmode="browse", style="Big.Treeview")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=34, minwidth=34, stretch=False)
        spec = [("sel", "选", 44, "center"), ("name", "门店 / 文件", 230, "w"),
                ("address", "现场地址", 300, "w"), ("vendor", "厂商", 110, "center"),
                ("time", "采集时间", 140, "center"), ("draft", "EgoOps", 110, "center")]
        for c, t, w, anchor in spec:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, minwidth=w, anchor=anchor,
                             stretch=(c in ("name", "address")))
        self.tree.tag_configure("odd", background="#FBFCFE")
        self.tree.tag_configure("even", background="#FFFFFF")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double)

        # 右：操作面板
        side = ttk.Frame(body, width=330, padding=(16, 0, 0, 0))
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        self.lbl_section = ttk.Label(side, text="下一步", style="Section.TLabel")
        self.lbl_section.pack(anchor="w", pady=(0, 6))

        card = ttk.Frame(side, style="Card.TFrame", padding=16)
        card.pack(fill="x")

        self.lbl_guide = ttk.Label(card, text="点「连接」把采集点拉下来。", style="Guide.TLabel",
                                   wraplength=280, justify="left")
        self.lbl_guide.pack(anchor="w")

        self.btn_step_main = ttk.Button(card, text="连接服务器", style="Accent.TButton",
                                        command=self.do_connect)
        self.btn_step_main.pack(fill="x", pady=(14, 0))

        ttk.Separator(side).pack(fill="x", pady=14)

        ttk.Label(side, text="常用操作", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Button(side, text="下载勾选的素材", command=self.download_checked).pack(fill="x", pady=3)
        ttk.Button(side, text="质检这个采集点", command=self.qc_site).pack(fill="x", pady=3)
        ttk.Button(side, text="预览草稿内容", command=self.show_draft).pack(fill="x", pady=3)
        ttk.Button(side, text="打开 EgoOps 网页", command=self.open_egoops).pack(fill="x", pady=3)
        ttk.Button(side, text="打开下载目录", command=self.open_download_dir).pack(fill="x", pady=3)

        # 兼容旧引用
        self.btn_dl_sites = self.btn_step_main
        self.btn_check_all = ttk.Button(side)
        self.btn_check_sites = self.btn_check_all
        self.btn_del_sites = ttk.Button(side)
        self.btn_dl = self.btn_step_main
        self.btn_dl_all = self.btn_step_main
        self.btn_open = ttk.Button(side)
        self.btn_draft = ttk.Button(side)
        self.btn_batch = ttk.Button(side)
        self.btn_qc = ttk.Button(side)
        self.btn_export = ttk.Button(side)

        # ---------- 预览 ----------
        self.preview = ttk.Label(self.root, text="选中照片会在上面显示", style="Preview.TLabel",
                                 anchor="center")
        self.preview.pack(fill="x", pady=(8, 6), ipady=6)

        # ---------- 底部 ----------
        foot = ttk.Frame(self.root, padding=(20, 8, 20, 14))
        foot.pack(side="bottom", fill="x", before=body)

        self.btn_dl_checked = ttk.Button(foot, text="下载勾选", style="Accent.TButton",
                                         command=self.download_checked)
        self.btn_dl_checked.pack(side="left")

        self.btn_del_files = ttk.Button(foot, text="删除勾选", command=self.delete_checked_files)
        self.btn_del_files.pack(side="left", padx=8)

        self.btn_fill = ttk.Button(foot, text="一键建草稿（美团）", style="Accent.TButton",
                                   command=self.fill_egoops)
        self.btn_fill.pack(side="left", padx=(20, 0))

        self.progress = ttk.Progressbar(foot, mode="determinate", length=220)
        self.progress.pack(side="right")
        self.lbl_task = ttk.Label(foot, text="", style="Dim.TLabel")
        self.lbl_task.pack(side="right", padx=12)

        # ---------- 菜单 ----------
        menubar = tk.Menu(self.root)

        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="打开下载目录", command=self.open_download_dir)
        m_file.add_command(label="导出采集数据表…", command=self.export_table)
        m_file.add_separator()
        m_file.add_command(label="退出", command=self.root.destroy)
        menubar.add_cascade(label="文件", menu=m_file)

        m_site = tk.Menu(menubar, tearoff=0)
        m_site.add_command(label="刷新列表", command=self.do_refresh)
        m_site.add_command(label="全选 / 取消全选", command=self.toggle_all_checks)
        m_site.add_separator()
        m_site.add_command(label="下载这个采集点全部", command=self.download_site)
        m_site.add_command(label="质检这个采集点", command=self.qc_site)
        m_site.add_separator()
        m_site.add_command(label="删除勾选的采集点", command=self.delete_checked_sites)
        menubar.add_cascade(label="采集点", menu=m_site)

        m_mt = tk.Menu(menubar, tearoff=0)
        m_mt.add_command(label="生成草稿（先核对）", command=self.show_draft)
        m_mt.add_command(label="一键建草稿", command=self.fill_egoops)
        m_mt.add_command(label="批量建草稿", command=self.batch_draft)
        m_mt.add_separator()
        m_mt.add_command(label="刷新草稿状态", command=self.refresh_draft_status)
        m_mt.add_command(label="刷新 EgoOps 登录态", command=self.refresh_login_state)
        menubar.add_cascade(label="美团", menu=m_mt)

        m_set = tk.Menu(menubar, tearoff=0)
        m_set.add_command(label="设置…", command=self.open_settings)
        menubar.add_cascade(label="设置", menu=m_set)

        self.root.config(menu=menubar)

        self.ctx = tk.Menu(self.root, tearoff=0)
        self.ctx.add_command(label="下载", command=self.download_checked)
        self.ctx.add_command(label="质检", command=self.qc_site)
        self.ctx.add_command(label="生成草稿", command=self.show_draft)
        self.ctx.add_command(label="一键建草稿", command=self.fill_egoops)
        self.ctx.add_separator()
        self.ctx.add_command(label="删除", command=self.delete_checked_files)
        self.tree.bind("<Button-3>", self._show_ctx)

        self.root.bind("<Control-a>", lambda e: self.toggle_all_checks())

    def open_egoops(self):
        import webbrowser
        webbrowser.open("https://egoops.meituan.com/assignment")

    # ---------------------------------------------------------------- 引导

    def _on_step_click(self, key):
        if key == "connect":
            self.do_connect()

    def set_step(self, active):
        pass

    def update_guide(self):
        if not getattr(self, "api", None):
            self.lbl_guide.config(text="① 先在上面填服务器地址，点「连接」。")
            self.btn_step_main.config(text="连接服务器", command=self.do_connect)
            return

        site, iid = self._target_site()
        if not site:
            n = len(getattr(self, "sites", []) or [])
            self.lbl_guide.config(text="② 已拉到 %d 个采集点。\\n\\n点一行看详情，或点最左边的方框勾选。" % n)
            self.btn_step_main.config(text="刷新列表", command=self.do_refresh)
            return

        d = extras.draft_of(site.get("id"))
        if d:
            st = d.get("status_text") or "草稿"
            self.lbl_guide.config(text="④ 已经建过草稿：%s\\n状态：%s\\n\\n重复建会在 EgoOps 里多出一条。"
                                  % (d.get("task_set_id"), st))
            self.btn_step_main.config(text="再次建草稿", command=self.fill_egoops)
        else:
            self.lbl_guide.config(text="③ 已选中「%s」。\\n\\n先点「质检这个采集点」看有没有坏图；"
                                  "确认没问题再建草稿。" % site.get("name", ""))
            self.btn_step_main.config(text="一键建草稿", command=self.fill_egoops)

    # ---------------------------------------------------------------- 设置（服务器 / 大模型）

'''
s = s[:start] + new + s[end:]

# ---------- 3) 样式 ----------
s = s.replace('''        s.configure("Head.TFrame", background="#FFFFFF")''',
'''        try:
            if getattr(self, "modern", False):
                base = 10
            else:
                base = 9
        except Exception:
            base = 9
        s.configure("Title.TLabel", font=("Microsoft YaHei UI", 18, "bold"))
        s.configure("Section.TLabel", font=("Microsoft YaHei UI", 10, "bold"))
        s.configure("Dim.TLabel", font=("Microsoft YaHei UI", base))
        s.configure("Guide.TLabel", font=("Microsoft YaHei UI", base + 1), foreground="#334155")
        s.configure("Status.TLabel", font=("Microsoft YaHei UI", base))
        s.configure("Preview.TLabel", font=("Microsoft YaHei UI", base), foreground="#64748B")
        s.configure("Card.TFrame", relief="solid", borderwidth=1)
        s.configure("Big.Treeview", rowheight=44, font=("Microsoft YaHei UI", 11))
        s.configure("Big.Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))
        s.configure("Head.TFrame", background="#FFFFFF")''')

# ---------- 4) 变量初始化 ----------
if 'var_server' not in s:
    s = s.replace('''        self._apply_theme()''', '''        self.var_server = tk.StringVar(value=self.cfg.get("server", ""))
        self.var_name = tk.StringVar(value=self.cfg.get("name", ""))
        self.var_search = tk.StringVar(value="")
        self.var_range = tk.StringVar(value="全部")
        self.var_vendor = tk.StringVar(value="全部")
        self._apply_theme()''')

io.open(p, 'w', encoding='utf-8').write(s)
print('界面二轮重做完成')
