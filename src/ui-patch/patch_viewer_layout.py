import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 底部按钮条先占位，避免被上面的列表挤掉
s = s.replace('''        bottom = ttk.Frame(self.root, padding=(12, 8, 12, 12))
        bottom.pack(fill="x")''', '''        bottom = ttk.Frame(self.root, padding=(12, 8, 12, 12))
        bottom.pack(side="bottom", fill="x", before=body)''')

# 2) 预览区不要太高，给按钮留空间
s = s.replace('self.preview.pack(fill="both", expand=False, pady=(8, 0), ipady=60)',
              'self.preview.pack(fill="both", expand=False, pady=(8, 0), ipady=12)')
s = s.replace('self.tv_files = ttk.Treeview(right, columns=cols2, show="headings", height=12)',
              'self.tv_files = ttk.Treeview(right, columns=cols2, show="headings", height=8)')

# 3) 文件列表加「区域」列
s = s.replace('''        cols2 = ("sel", "task", "kind", "name", "size", "time")
        self.tv_files = ttk.Treeview(right, columns=cols2, show="headings", height=8)
        for c, t, w in zip(cols2, ("选", "任务", "类型", "文件名", "大小", "上传时间"), (40, 85, 50, 225, 80, 140)):''',
              '''        cols2 = ("sel", "area", "task", "kind", "name", "size", "time")
        self.tv_files = ttk.Treeview(right, columns=cols2, show="headings", height=8)
        for c, t, w in zip(cols2, ("选", "区域", "任务", "类型", "文件名", "大小", "上传时间"), (36, 85, 95, 45, 195, 70, 125)):''')

# 4) 填充时拆成两列
s = s.replace('''        def task_label(t):
            a = (t.get("area") or "").strip()
            n = (t.get("name") or "").strip()
            return (a + "：" + n) if a else n

        if tasks:
            for t in tasks:
                for f in (t.get("photos") or []) + (t.get("videos") or []):
                    files.append(f)
                    self.tv_files.insert("", "end", iid=f["id"], values=(
                        "☐",
                        task_label(t),''', '''        def area_of(t):
            return (t.get("area") or "").strip() or "-"

        def task_label(t):
            return (t.get("name") or "").strip()

        if tasks:
            for t in tasks:
                for f in (t.get("photos") or []) + (t.get("videos") or []):
                    files.append(f)
                    self.tv_files.insert("", "end", iid=f["id"], values=(
                        "☐",
                        area_of(t),
                        task_label(t),''')

# 5) 老数据分支也要补一列
s = s.replace('''                self.tv_files.insert("", "end", iid=f["id"], values=(
                    "☐",
                    "-",''', '''                self.tv_files.insert("", "end", iid=f["id"], values=(
                    "☐",
                    "-",
                    "-",''')

io.open(p, 'w', encoding='utf-8').write(s)
print('viewer layout patched')
