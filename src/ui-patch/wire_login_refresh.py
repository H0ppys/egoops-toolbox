import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 设置-服务器页加「刷新 EgoOps 登录态」
s = s.replace('''        ttk.Button(tab1, text="选择…", command=lambda: self._pick_dir_into(e_dir)).pack(anchor="w")''',
'''        ttk.Button(tab1, text="选择…", command=lambda: self._pick_dir_into(e_dir)).pack(anchor="w")

        ttk.Separator(tab1, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(tab1, text="EgoOps 登录态").pack(anchor="w")
        login_state = ttk.Label(tab1, text="", foreground="#8a97a8")
        login_state.pack(anchor="w", pady=(2, 6))

        def show_state():
            path = os.path.join(os.environ.get("APPDATA") or ".", "egoops-viewer", "egoops_auth.json")
            if not os.path.exists(path):
                login_state.config(text="没有登录态文件，先点下面按钮登录一次", foreground="#b3261e")
                return
            try:
                import json as _json
                d = _json.load(open(path, encoding="utf-8"))
                login_state.config(text="上次保存：%s" % d.get("saved_at", "未知"), foreground="#1f7a3d")
            except Exception:
                login_state.config(text="登录态文件损坏", foreground="#b3261e")

        def refresh_login():
            login_state.config(text="正在打开浏览器校验…", foreground="#8a97a8")

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
                    ok, info = mod.refresh()
                    self.ui(lambda: login_state.config(
                        text=("✓ " if ok else "✗ ") + info,
                        foreground="#1f7a3d" if ok else "#b3261e"))
                except Exception as e:
                    self.ui(lambda: login_state.config(text="✗ 失败：%s" % e, foreground="#b3261e"))

            threading.Thread(target=work, daemon=True).start()

        bar2 = ttk.Frame(tab1)
        bar2.pack(anchor="w")
        ttk.Button(bar2, text="刷新登录态", command=refresh_login).pack(side="left")
        ttk.Button(bar2, text="查看状态", command=show_state).pack(side="left", padx=6)
        show_state()''')

io.open(p, 'w', encoding='utf-8').write(s)
print('登录态刷新按钮已加')
