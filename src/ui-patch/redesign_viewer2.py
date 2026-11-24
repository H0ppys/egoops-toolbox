"""查看器界面重做：顶部品牌条 + 四步引导 + 右侧说明面板 + 底部主操作。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    # ---------------------------------------------------------------- 布局')
end = s.index('    # ---------------------------------------------------------------- 设置（服务器 / 大模型）')

new = '''    # ---------------------------------------------------------------- 布局

    def _build(self):
        # ================= 顶部：品牌 + 连接 =================
        head = ttk.Frame(self.root, style="Head.TFrame", padding=(18, 12, 18, 10))
        head.pack(fill="x")

        tk.Label(head, text="采集数据查看器", font=("Microsoft YaHei UI", 16, "bold"),
                 bg="#FFFFFF", fg="#0F172A").pack(side="left")
        tk.Label(head, text="  美团采集数据 · 质检 · 建草稿", font=("Microsoft YaHei UI", 9),
                 bg="#FFFFFF", fg="#94A3B8").pack(side="left", pady=(6, 0))

        self.lbl_status = tk.Label(head, text="● 未连接", font=("Microsoft YaHei UI", 10),
                                   bg="#FFFFFF", fg="#DC2626")
        self.lbl_status.pack(side="right")

        # ================= 服务器行 =================
        bar = ttk.Frame(self.root, style="Head.TFrame", padding=(18, 0, 18, 10))
        bar.pack(fill="x")

        ttk.Label(bar, text="服务器", style="Dim.TLabel").pack(side="left")
        self.ent_server = ttk.Entry(bar, width=30, font=("Consolas", 10))
        self.ent_server.pack(side="left", padx=(6, 12))

        ttk.Label(bar, text="姓名", style="Dim.TLabel").pack(side="left")
        self.ent_name = ttk.Entry(bar, width=9)
        self.ent_name.pack(side="left", padx=(6, 10))

        self.btn_connect = ttk.Button(bar, text="连接", style="Primary.TButton", command=self.do_connect)
        self.btn_connect.pack(side="left")
        self.btn_refresh = ttk.Button(bar, text="刷新", command=self.do_refresh)
        self.btn_refresh.pack(side="left", padx=6)

        self.lbl_invite = ttk.Label(bar, text="邀请码")
        self.ent_invite = ttk.Entry(bar, width=10, show="*")
        self.lbl_invite.pack_forget()
        self.ent_invite.pack_forget()

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12)

        ttk.Label(bar, text="搜", style="Dim.TLabel").pack(side="left")
        self.ent_search = ttk.Entry(bar, width=16)
        self.ent_search.pack(side="left", padx=(4, 10))
        self.ent_search.bind("<Return>", lambda e: self.do_refresh())
        self.ent_search.bind("<KeyRelease>", self._on_search_typing)

        self.cmb_range = ttk.Combobox(bar, width=7, state="readonly",
                                      values=["全部", "今天", "近 7 天", "近 30 天"])
        self.cmb_range.set("全部")
        self.cmb_range.pack(side="left")
        self.cmb_range.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())

        ttk.Label(bar, text="厂商", style="Dim.TLabel").pack(side="left", padx=(10, 0))
        self.cmb_vendor = ttk.Combobox(bar, width=14, state="readonly", values=["全部"])
        self.cmb_vendor.set("全部")
        self.cmb_vendor.pack(side="left", padx=(4, 0))
        self.cmb_vendor.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())

        # ================= 四步引导 =================
        steps = ttk.Frame(self.root, padding=(18, 0, 18, 8))
        steps.pack(fill="x")

        self.step_widgets = {}
        for idx, (key, title, sub) in enumerate([
            ("connect", "① 连接服务器", "填地址点连接"),
            ("pick", "② 选采集点", "点门店或勾方框"),
            ("check", "③ 质检 / 下载", "看看有没有坏图"),
            ("draft", "④ 建草稿", "只建草稿不提交"),
        ]):
            card = tk.Frame(steps, bg="#FFFFFF", highlightbackground="#E2E8F0",
                            highlightthickness=1, cursor="hand2")
            card.pack(side="left", padx=(0, 10), ipadx=14, ipady=8)
            t1 = tk.Label(card, text=title, font=("Microsoft YaHei UI", 10, "bold"),
                          bg="#FFFFFF", fg="#0F172A", cursor="hand2")
            t1.pack(anchor="w")
            t2 = tk.Label(card, text=sub, font=("Microsoft YaHei UI", 8),
                          bg="#FFFFFF", fg="#94A3B8", cursor="hand2")
            t2.pack(anchor="w")
            for w in (card, t1, t2):
                w.bind("<Button-1>", lambda e, k=key: self._on_step_click(k))
            self.step_widgets[key] = (card, t1, t2)

        # ================= 主体：树 + 右侧说明 =================
        body = ttk.Frame(self.root, padding=(18, 0, 18, 0))
        body.pack(fill="both", expand=True, pady=(0, 6))

        left = tk.Frame(body, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True)

        self.lbl_site = tk.Label(left, text="采集点（点开左边的三角看任务和文件）",
                                 font=("Microsoft YaHei UI", 10, "bold"),
                                 bg="#FFFFFF", fg="#0F172A", anchor="w", padx=12, pady=8)
        self.lbl_site.pack(fill="x")

        treeWrap = tk.Frame(left, bg="#FFFFFF")
        treeWrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cols = ("sel", "name", "vendor", "detail", "who", "time", "size", "draft")
        self.tree = ttk.Treeview(treeWrap, columns=cols, show="tree headings",
                                 selectmode="browse", style="Card.Treeview")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=28, minwidth=28, stretch=False)
        widths = {"sel": 30, "name": 150, "vendor": 100, "detail": 200, "who": 100, "time": 105, "size": 62, "draft": 100}
        titles = {"sel": "选", "name": "名称 / 文件", "vendor": "厂商", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小", "draft": "EgoOps"}
        for c in cols:
            self.tree.heading(c, text=titles[c])
            self.tree.column(c, width=widths[c], minwidth=widths[c],
                             stretch=(c in ("name", "detail")),
                             anchor="w" if c in ("name", "detail") else "center")
        self.tree.tag_configure("odd", background="#F8FAFC")
        self.tree.tag_configure("even", background="#FFFFFF")

        vsb = ttk.Scrollbar(treeWrap, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(treeWrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        treeWrap.rowconfigure(0, weight=1)
        treeWrap.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double)

        # 右侧：说明面板
        side = tk.Frame(body, bg="#FFFFFF", width=300, highlightbackground="#E2E8F0", highlightthickness=1)
        side.pack(side="left", fill="y", padx=(10, 0))
        side.pack_propagate(False)

        tk.Label(side, text="下一步做什么", font=("Microsoft YaHei UI", 10, "bold"),
                 bg="#FFFFFF", fg="#0F172A", anchor="w", padx=14, pady=10).pack(fill="x")

        self.lbl_guide = tk.Label(side, text="先点「连接」拉取采集点。", font=("Microsoft YaHei UI", 9),
                                  bg="#FFFFFF", fg="#475569", justify="left", anchor="nw",
                                  wraplength=260, padx=14)
        self.lbl_guide.pack(fill="x")

        self.btn_step_main = ttk.Button(side, text="连接服务器", style="Primary.TButton",
                                        command=self.do_connect)
        self.btn_step_main.pack(fill="x", padx=14, pady=(12, 6))

        ttk.Button(side, text="下载勾选的素材", command=self.download_checked).pack(fill="x", padx=14, pady=(0, 6))
        ttk.Button(side, text="质检当前采集点", command=self.qc_site).pack(fill="x", padx=14, pady=(0, 6))
        ttk.Button(side, text="打开下载目录", command=self.open_download_dir).pack(fill="x", padx=14, pady=(0, 6))

        # 兼容旧代码引用的控件（不显示）
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

        # ================= 预览 =================
        self.preview = tk.Label(self.root, text="选中照片可在这里预览",
                                font=("Microsoft YaHei UI", 9),
                                anchor="center", background="#F1F5F9", foreground="#94A3B8")
        self.preview.pack(fill="both", expand=False, pady=(0, 6), ipady=6)

        # ================= 底部主操作 =================
        foot = tk.Frame(self.root, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        foot.pack(side="bottom", fill="x", before=body)

        inner = tk.Frame(foot, bg="#FFFFFF")
        inner.pack(fill="x", padx=18, pady=10)

        self.btn_dl_checked = ttk.Button(inner, text="下载勾选", style="Primary.TButton",
                                         command=self.download_checked)
        self.btn_dl_checked.pack(side="left")

        self.btn_del_files = ttk.Button(inner, text="删除勾选", command=self.delete_checked_files)
        self.btn_del_files.pack(side="left", padx=8)

        self.btn_fill = ttk.Button(inner, text="一键建草稿（美团）", style="Primary.TButton",
                                   command=self.fill_egoops)
        self.btn_fill.pack(side="left", padx=(18, 0))

        self.lbl_task = tk.Label(inner, text="", font=("Microsoft YaHei UI", 9),
                                 bg="#FFFFFF", fg="#64748B")
        self.lbl_task.pack(side="left", padx=12)

        self.progress = ttk.Progressbar(inner, mode="determinate", length=200)
        self.progress.pack(side="right")

        # ================= 菜单 =================
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
        m_mt.add_command(label="刷新草稿状态（待审核/已通过）", command=self.refresh_draft_status)
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

    # ---------------------------------------------------------------- 引导

    def _on_step_click(self, key):
        if key == "connect":
            self.do_connect()
        elif key == "pick":
            self.lbl_guide.config(text="在左边的列表里点一个采集点，或者勾选它最左边的方框。\\n\\n双击可以展开看任务和文件。")
            self.btn_step_main.config(text="刷新列表", command=self.do_refresh)
        elif key == "check":
            self.qc_site()
        elif key == "draft":
            self.fill_egoops()

    def set_step(self, active):
        order = ["connect", "pick", "check", "draft"]
        for key, (card, t1, t2) in getattr(self, "step_widgets", {}).items():
            if key == active:
                card.config(highlightbackground="#2563EB", highlightthickness=2, bg="#EFF6FF")
                t1.config(bg="#EFF6FF", fg="#1D4ED8")
                t2.config(bg="#EFF6FF", fg="#60A5FA")
            else:
                card.config(highlightbackground="#E2E8F0", highlightthickness=1, bg="#FFFFFF")
                t1.config(bg="#FFFFFF", fg="#0F172A")
                t2.config(bg="#FFFFFF", fg="#94A3B8")

    def update_guide(self):
        if not getattr(self, "api", None):
            self.set_step("connect")
            self.lbl_guide.config(text="① 先填服务器地址，点「连接」把采集点拉下来。")
            self.btn_step_main.config(text="连接服务器", command=self.do_connect)
            return

        site, iid = self._target_site()
        if not site:
            self.set_step("pick")
            n = len(getattr(self, "sites", []) or [])
            self.lbl_guide.config(text="② 已连上，共有 %d 个采集点。\\n\\n点一个采集点看详情，或勾选它的方框做批量操作。" % n)
            self.btn_step_main.config(text="刷新列表", command=self.do_refresh)
            return

        # 有选中：看是否质检过 / 有草稿
        d = extras.draft_of(site.get("id"))
        issues = (getattr(self, "qc_result", {}) or {}).get(site.get("id"))
        if d:
            self.set_step("draft")
            txt = "④ 这个采集点已经建过草稿：%s\\n" % d.get("task_set_id")
            st = d.get("status_text") or ""
            if st:
                txt += "\\n当前状态：%s\\n" % st
            txt += "\\n要重新建一份，先到菜单「美团 → 刷新草稿状态」看下现状。"
            self.lbl_guide.config(text=txt)
            self.btn_step_main.config(text="再次建草稿", command=self.fill_egoops)
        elif issues is None:
            self.set_step("check")
            self.lbl_guide.config(text="③ 已选中「%s」。\\n\\n建议先点一下「质检当前采集点」，"
                                       "检查有没有模糊、过暗或重复的素材。" % site.get("name", ""))
            self.btn_step_main.config(text="质检这个采集点", command=self.qc_site)
        else:
            self.set_step("draft")
            bad = len([x for x in issues if x.get("level") == "error"])
            if bad:
                self.lbl_guide.config(text="⚠ 质检发现 %d 个严重问题。\\n\\n"
                                           "建议先下载素材重拍，再建草稿。" % bad)
            else:
                self.lbl_guide.config(text="✓ 质检通过，可以建草稿了。\\n\\n"
                                           "点下面的按钮，会把采集点 + 每个区域任务写进 EgoOps（只存草稿）。")
            self.btn_step_main.config(text="一键建草稿", command=self.fill_egoops)

    # ---------------------------------------------------------------- 设置（服务器 / 大模型）

'''
s = s[:start] + new + s[end:]

# 样式：加 Head / Dim / Card.Treeview + 行高
s = s.replace('''        s.configure("Title.TLabel", font=("Microsoft YaHei UI", 12, "bold"))''',
'''        s.configure("Head.TFrame", background="#FFFFFF")
        s.configure("Dim.TLabel", foreground="#64748B", background="#FFFFFF", font=("Microsoft YaHei UI", 9))
        s.configure("Card.Treeview", rowheight=28, font=("Microsoft YaHei UI", 9),
                    fieldbackground="#FFFFFF", background="#FFFFFF", borderwidth=0)
        s.configure("Card.Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"), padding=(6, 6))
        s.configure("Title.TLabel", font=("Microsoft YaHei UI", 12, "bold"))''')

# 窗口底色 / 尺寸
s = s.replace('root.geometry("1440x880")', 'root.geometry("1500x900")\n        root.configure(bg="#F1F5F9")')

# 各处状态更新后刷新引导
s = s.replace('''        self.set_status("已连接 · 采集点 %d 个 · %s" % (len(items), time.strftime("%H:%M:%S")), "#1f7a3d")''',
'''        self.set_status("已连接 · 采集点 %d 个 · %s" % (len(items), time.strftime("%H:%M:%S")), "#1f7a3d")
        self.update_guide()''')

s = s.replace('''    def on_tree_select(self, event=None):''', '''    def on_tree_select(self, event=None):
        try:
            self.update_guide()
        except Exception:
            pass''')

s = s.replace('''        self.set_status("已连接 · 采集点 %s 个 · 文件 %s 个" % (health.get("sites", 0), health.get("files", 0)))''',
              '''        self.set_status("已连接 · 采集点 %s 个 · 文件 %s 个" % (health.get("sites", 0), health.get("files", 0)))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('界面已重做')
