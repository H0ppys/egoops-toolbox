import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 列宽收窄，保证 1100px 窗口下所有列都能放下
old = '''        widths = {"sel": 34, "name": 260, "detail": 380, "who": 110, "time": 125, "size": 75}'''
new = '''        widths = {"sel": 30, "name": 175, "detail": 225, "who": 95, "time": 105, "size": 62}'''
assert old in s
s = s.replace(old, new)

# 2) 选中行时，把完整信息显示在上方那一行，避免被列宽截断
old2 = '''        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)'''
new2 = '''        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)'''
assert old2 in s
s = s.replace(old2, new2)

# 3) 加 on_tree_select
old3 = '''    def on_tree_open(self, event):'''
new3 = '''    def on_tree_select(self, event=None):
        iid = self.tree.focus()
        if iid in self.site_rows:
            it = self.site_rows[iid]
            self.lbl_site.config(text="%s · %s · %s 个文件 · %s · 采集员 %s" % (
                it.get("name", ""),
                it.get("address") or "（未填地址）",
                it.get("file_count", 0),
                human_size(it.get("bytes", 0)),
                it.get("created_by", "")))
        elif iid in self.file_rows:
            f = self.file_rows[iid]
            self.lbl_site.config(text="%s · %s · %s" % (
                f.get("filename", ""), human_size(f.get("size", 0)), f.get("kind", "")))
            self.show_photo_file(f)
        else:
            self.lbl_site.config(text="采集点（点开左侧三角展开任务和文件）")

    def show_photo_file(self, f):
        if f.get("kind") != "photo":
            return
        try:
            import importlib.util
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api.py")
            base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, "api.py")
            spec = importlib.util.spec_from_file_location("api_mod", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            a = mod.Api(self.cfg.get("server", ""))
            a.token = self.api.token
            tmp = os.path.join(os.environ.get("TEMP") or ".", "preview_" + f["id"] + ".jpg")
            if not os.path.exists(tmp):
                a.download(f["id"], tmp)
            self.show_photo(tmp)
        except Exception:
            pass

    def on_tree_open(self, event):'''
assert old3 in s
s = s.replace(old3, new3, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('columns + info line patched')
