"""1) 表格加横向滚动条并让列宽自适应，避免文字被切
2) 不再自动弹登录（只有点了才登录）
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 横向滚动条 + grid 布局
old = '''        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")'''
new = '''        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)'''
assert old in s
s = s.replace(old, new)

# 2) 列宽再收一点，保证默认窗口下能看到时间列
s = s.replace('''        spec = [("sel", "选", 46, "center"), ("name", "门店 / 文件", 210, "w"),
                ("address", "现场地址", 250, "w"), ("vendor", "厂商", 96, "center"),
                ("time", "采集时间", 118, "center"), ("draft", "EgoOps", 96, "center")]''',
'''        spec = [("sel", "选", 44, "center"), ("name", "门店 / 文件", 190, "w"),
                ("address", "现场地址", 230, "w"), ("vendor", "厂商", 90, "center"),
                ("time", "采集时间", 130, "center"), ("draft", "EgoOps", 96, "center")]''')

# 3) 顶部状态标签不再绑定点击登录（避免误触弹窗）
s = s.replace('''        self.lbl_egoops.bind("<Button-1>", lambda e: self.do_login())''', '''''')

io.open(p, 'w', encoding='utf-8').write(s)
print('表格滚动 + 列宽 已修')
