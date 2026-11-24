import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('        # ---------- 底部操作区 ----------')
end = s.index('    # ---------------------------------------------------------------- 设置（服务器 / 大模型）')

new = '''        # ---------- 底部：只留最常用的三个 ----------
        bottom = ttk.Frame(self.root, padding=(14, 4, 14, 12))
        bottom.pack(side="bottom", fill="x", before=body)

        self.btn_dl_checked = ttk.Button(bottom, text="下载勾选（0）", style="Primary.TButton",
                                         command=self.download_checked)
        self.btn_dl_checked.pack(side="left")

        self.btn_del_files = ttk.Button(bottom, text="删除勾选", style="Danger.TButton",
                                        command=self.delete_checked_files)
        self.btn_del_files.pack(side="left", padx=(6, 0))

        self.btn_fill = ttk.Button(bottom, text="一键建草稿", style="Primary.TButton", command=self.fill_egoops)
        self.btn_fill.pack(side="left", padx=(18, 0))

        self.progress = ttk.Progressbar(bottom, mode="determinate", length=220)
        self.progress.pack(side="left", padx=(18, 10))
        self.lbl_task = ttk.Label(bottom, text="", foreground="#8a97a8")
        self.lbl_task.pack(side="left")

        # 兼容旧代码引用的控件（不再显示，功能移到菜单）
        self.btn_dl_sites = self.btn_dl_checked
        self.btn_check_all = ttk.Button(bottom)
        self.btn_check_sites = self.btn_check_all
        self.btn_del_sites = self.btn_del_files
        self.btn_dl = self.btn_dl_checked
        self.btn_dl_all = self.btn_dl_checked
        self.btn_open = ttk.Button(bottom)
        self.btn_draft = ttk.Button(bottom)
        self.btn_batch = ttk.Button(bottom)
        self.btn_qc = ttk.Button(bottom)
        self.btn_export = ttk.Button(bottom)

        # ---------- 菜单栏 ----------
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
        m_mt.add_command(label="刷新 EgoOps 登录态", command=self.refresh_login_state)
        menubar.add_cascade(label="美团", menu=m_mt)

        m_set = tk.Menu(menubar, tearoff=0)
        m_set.add_command(label="设置…", command=self.open_settings)
        menubar.add_cascade(label="设置", menu=m_set)

        self.root.config(menu=menubar)

        # ---------- 右键菜单 ----------
        self.ctx = tk.Menu(self.root, tearoff=0)
        self.ctx.add_command(label="下载", command=self.download_checked)
        self.ctx.add_command(label="质检", command=self.qc_site)
        self.ctx.add_command(label="生成草稿", command=self.show_draft)
        self.ctx.add_command(label="一键建草稿", command=self.fill_egoops)
        self.ctx.add_separator()
        self.ctx.add_command(label="删除", command=self.delete_checked_files)
        self.tree.bind("<Button-3>", self._show_ctx)

        # Ctrl+A 全选
        self.root.bind("<Control-a>", lambda e: self.toggle_all_checks())

'''
s = s[:start] + new + s[end:]

# 右键菜单辅助 + 登录态刷新入口
s = s.replace('''    def draft_text(self, site):''', '''    def _show_ctx(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.focus(iid)
            self.tree.selection_set(iid)
        try:
            self.ctx.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx.grab_release()

    def refresh_login_state(self):
        self.open_settings()

    def draft_text(self, site):''')

io.open(p, 'w', encoding='utf-8').write(s)
print('底部按钮精简为 3 个 + 菜单栏 + 右键菜单')
