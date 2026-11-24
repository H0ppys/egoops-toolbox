import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 修 'NoneType' object is not subscriptable：占位子节点也以 site: 开头 ----------
old = '''    def on_tree_open(self, event):
        iid = self.tree.focus()
        if not iid.startswith("site:") or iid in self.loaded_sites:
            return
        self.loaded_sites.add(iid)
        site = self.site_rows.get(iid)'''
new = '''    def on_tree_open(self, event):
        iid = self.tree.focus()
        if iid not in self.site_rows or iid in self.loaded_sites:
            return
        self.loaded_sites.add(iid)
        site = self.site_rows.get(iid)
        if not site:
            return'''
assert old in s
s = s.replace(old, new)

# ---------- 2) 列宽 + 横向滚动条，内容不再被挤掉 ----------
old2 = '''        cols = ("sel", "name", "detail", "who", "time", "size")
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
        vsb.pack(side="right", fill="y")'''
new2 = '''        cols = ("sel", "name", "detail", "who", "time", "size")
        self.tree = ttk.Treeview(treeWrap, columns=cols, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=28, minwidth=28, stretch=False)
        widths = {"sel": 34, "name": 260, "detail": 380, "who": 110, "time": 125, "size": 75}
        titles = {"sel": "选", "name": "名称 / 文件", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小"}
        for c in cols:
            self.tree.heading(c, text=titles[c])
            self.tree.column(c, width=widths[c], minwidth=widths[c],
                             stretch=(c in ("name", "detail")),
                             anchor="w" if c in ("name", "detail") else "center")

        vsb = ttk.Scrollbar(treeWrap, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(treeWrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        treeWrap.rowconfigure(0, weight=1)
        treeWrap.columnconfigure(0, weight=1)'''
assert old2 in s
s = s.replace(old2, new2)

# ---------- 3) 界面异常写日志，方便定位 ----------
s = s.replace('''                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.set_status("界面出错：%s" % e, "#b3261e")''',
'''                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    try:
                        log_dir = os.path.join(os.environ.get("APPDATA") or ".", "egoops-viewer")
                        os.makedirs(log_dir, exist_ok=True)
                        with open(os.path.join(log_dir, "error.log"), "a", encoding="utf-8") as fh:
                            fh.write("\\n=== %s ===\\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
                            fh.write(traceback.format_exc())
                    except Exception:
                        pass
                    self.set_status("界面出错：%s" % e, "#b3261e")''')

io.open(p, 'w', encoding='utf-8').write(s)
print('tree fixed')
