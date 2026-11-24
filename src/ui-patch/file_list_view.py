"""去掉图片预览，素材改成清单表格（勾选 + 文件名 + 类型 + 大小 + 时间）。"""

import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

# 1) 布局：把 Canvas 缩略图墙换成 Treeview 清单
old_wall = '''        # 素材缩略图墙
        wall = ttk.Frame(right)
        wall.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wall, bg="#F8FAFC", highlightthickness=0)
        vs = ttk.Scrollbar(wall, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vs.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.grid_frame = tk.Frame(self.canvas, bg="#F8FAFC")
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>",
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))'''
new_wall = '''        # 素材清单
        wall = ttk.Frame(right)
        wall.pack(fill="both", expand=True)
        cols = ("pick", "name", "kind", "size", "time")
        self.tv_files = ttk.Treeview(wall, columns=cols, show="headings",
                                     style="Big.Treeview", selectmode="browse")
        for c, t, w, anchor in (("pick", "选", 44, "center"), ("name", "文件名", 300, "w"),
                                ("kind", "类型", 70, "center"), ("size", "大小", 90, "center"),
                                ("time", "时间", 140, "center")):
            self.tv_files.heading(c, text=t)
            self.tv_files.column(c, width=w, anchor=anchor, stretch=(c == "name"))
        vs = ttk.Scrollbar(wall, orient="vertical", command=self.tv_files.yview)
        self.tv_files.configure(yscrollcommand=vs.set)
        self.tv_files.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.tv_files.bind("<Button-1>", self._on_file_click)
        self.tv_files.bind("<space>", lambda e: self._toggle_focus_file())'''
assert old_wall in s
s = s.replace(old_wall, new_wall)

# 2) render_files 改成填表格
start = s.index('    def render_files(self):')
end = s.index('    def load_thumb(self, f, label):')
new_render = '''    def render_files(self):
        self.tv_files.delete(*self.tv_files.get_children())
        if not self.files:
            self.tv_files.insert("", "end", iid="__empty", values=("", "这个任务还没有素材", "", "", ""))
            self.update_sel_state()
            return
        for f in self.files:
            fid = f["id"]
            self.tv_files.insert("", "end", iid=fid, values=(
                "☑" if fid in self.selected else "☐",
                f.get("filename") or fid,
                "照片" if f.get("kind") == "photo" else "视频",
                human_size(f.get("size")),
                (f.get("created_at") or "")[:16].replace("T", " "),
            ))
        self.update_sel_state()

    def _on_file_click(self, event):
        if self.tv_files.identify_region(event.x, event.y) != "cell":
            return
        if self.tv_files.identify_column(event.x) != "#1":
            return
        iid = self.tv_files.identify_row(event.y)
        if iid and iid != "__empty":
            self._toggle_file(iid)
            return "break"

    def _toggle_focus_file(self):
        iid = self.tv_files.focus()
        if iid and iid != "__empty":
            self._toggle_file(iid)

    def _toggle_file(self, fid):
        if fid in self.selected:
            self.selected.discard(fid)
            self.tv_files.set(fid, "pick", "☐")
        else:
            self.selected.add(fid)
            self.tv_files.set(fid, "pick", "☑")
        self.update_sel_state()

'''
s = s[:start] + new_render + s[end:]

# 3) 删掉 load_thumb 整个方法
start2 = s.index('    def load_thumb(self, f, label):')
end2 = s.index('    def update_sel_state(self):')
s = s[:start2] + s[end2:]

# 4) select_all / select_none 用新渲染
s = s.replace('''    def select_all(self):
        self.selected = {f["id"] for f in self.files}
        self.render_files()''',
'''    def select_all(self):
        self.selected = {f["id"] for f in self.files if f["id"]}
        self.render_files()''')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('素材清单已替换，语法 OK')
