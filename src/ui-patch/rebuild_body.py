import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('        # ---------- 主体：一个树形表 ----------')
end = s.index('        # ---------- 底部操作区 ----------')

new = '''        # ---------- 主体：一个树形表 ----------
        body = ttk.Frame(self.root, padding=(14, 0, 14, 0))
        body.pack(fill="both", expand=True, pady=(0, 6))

        self.lbl_site = ttk.Label(body, text="采集点（点开左侧三角展开任务和文件）", style="Title.TLabel")
        self.lbl_site.pack(anchor="w", pady=(0, 6))

        treeWrap = ttk.Frame(body)
        treeWrap.pack(fill="both", expand=True)

        cols = ("sel", "name", "detail", "who", "time", "size")
        self.tree = ttk.Treeview(treeWrap, columns=cols, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=30, stretch=False)
        for c, t, w in zip(cols, ("选", "名称 / 文件", "地址 / 区域·任务 / 类型", "采集员 / 数量", "时间", "大小"),
                           (36, 210, 330, 120, 130, 80)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w" if c in ("name", "detail") else "center")

        vsb = ttk.Scrollbar(treeWrap, orient="vertical", command=self.tree.yview)
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
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('body rebuilt')
