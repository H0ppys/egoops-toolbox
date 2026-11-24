import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 菜单里的「刷新 EgoOps 登录态」直接执行，不再只是打开设置
s = s.replace('''    def refresh_login_state(self):
        self.open_settings()''', '''    def refresh_login_state(self):
        self.lbl_task.config(text="正在检查 EgoOps 登录态…")

        def work():
            try:
                import importlib.util
                base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(base, "egoops_auth.py")
                if not os.path.exists(path):
                    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egoops_auth.py")
                spec = importlib.util.spec_from_file_location("egoops_auth", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                ok, msg = mod.refresh(log=lambda m: self.ui(self.lbl_task.config, text=str(m)))
            except Exception as e:
                ok, msg = False, "刷新失败：%s" % e
            self.ui(lambda: (self.lbl_task.config(text=msg),
                             messagebox.showinfo(APP_NAME, msg) if ok else messagebox.showerror(APP_NAME, msg)))

        threading.Thread(target=work, daemon=True).start()''')

# 2) 双击采集点行 = 展开/收起
s = s.replace('''    def on_tree_double(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid or not iid.startswith("file:"):
            return''', '''    def on_tree_double(self, event):
        iid = self.tree.identify_row(event.y)
        if iid in self.site_rows:
            opened = self.tree.item(iid, "open")
            self.tree.item(iid, open=not opened)
            if not opened:
                self.on_tree_open(None)
            return
        if not iid or not iid.startswith("file:"):
            return''')

# 3) 空列表给引导
s = s.replace('''        self.set_status("已连接 · 采集点 %d 个" % len(items), "#1f7a3d")''',
'''        if not items:
            self.tree.insert("", "end", iid="empty:hint", text="", values=(
                "", "还没有采集点", "让采集员用手机 App 拍完上传，这里会自动出现", "", "", "", ""))
        self.set_status("已连接 · 采集点 %d 个 · %s" % (len(items), time.strftime("%H:%M:%S")), "#1f7a3d")''')

# 4) 勾选提示带上当前总数
s = s.replace('''    def update_check_label(self):
        self.btn_dl_checked.config(text="下载勾选（%d）" % len(self.checked))
        self.btn_dl_sites.config(text="下载勾选（%d）" % len(self.checked))''',
'''    def update_check_label(self):
        n = len(self.checked)
        text = "下载勾选（%d）" % n if n else "下载勾选"
        try:
            self.btn_dl_checked.config(text=text)
            self.btn_dl_sites.config(text=text)
        except Exception:
            pass''')

io.open(p, 'w', encoding='utf-8').write(s)
print('viewer 打磨完成')
