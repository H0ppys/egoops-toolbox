"""修当前崩溃（var_* 未初始化 / Entry 插入重复），并加：启动即检查 EgoOps 登录态，掉了立刻提示登录。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) __init__：变量 + 去掉旧的 insert ----------
old = '''        self._style()
        self._apply_theme()
        self._build()
        self._poll()

        server = self.cfg.get("server") or DEFAULT_SERVER
        self.ent_server.insert(0, server)
        self.ent_name.insert(0, self.cfg.get("name", ""))
        self.ent_invite.insert(0, self.cfg.get("invite", ""))

        if autoconnect and self.ent_name.get():
            self.do_connect()'''

new = '''        self.var_server = tk.StringVar(value=self.cfg.get("server") or DEFAULT_SERVER)
        self.var_name = tk.StringVar(value=self.cfg.get("name", ""))
        self.var_search = tk.StringVar(value="")
        self.var_range = tk.StringVar(value="全部")
        self.var_vendor = tk.StringVar(value="全部")
        self.login_ok = None
        self.login_who = ""

        self._style()
        self._apply_theme()
        self._build()
        self._poll()

        if autoconnect and self.var_name.get():
            self.do_connect()

        self.root.after(600, self.check_egoops_login)'''

assert old in s
s = s.replace(old, new)

# ---------- 2) 登录态检查 + 提示 ----------
if 'check_egoops_login' not in s:
    s = s.replace('''    # ---------------------------------------------------------------- 样式''', '''    # ---------------------------------------------------------------- EgoOps 登录态

    def _load_egoops_auth_mod(self):
        import importlib.util
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "egoops_auth.py")
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egoops_auth.py")
        spec = importlib.util.spec_from_file_location("egoops_auth", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def check_egoops_login(self):
        """启动时查一次；掉了就马上让用户登录"""
        self.lbl_egoops.config(text="EgoOps：检查中…", foreground="#64748B")

        def work():
            try:
                mod = self._load_egoops_auth_mod()
                tok = mod.token_of()
                ok, who = mod.alive(tok)
            except Exception as e:
                ok, who = False, str(e)
            self.ui(self._after_login_check, ok, who)

        threading.Thread(target=work, daemon=True).start()

    def _after_login_check(self, ok, who):
        self.login_ok = ok
        self.login_who = who
        if ok:
            self.lbl_egoops.config(text="EgoOps：已登录 %s" % who, foreground="#15803D")
        else:
            self.lbl_egoops.config(text="EgoOps：登录已失效", foreground="#B91C1C")
            self.prompt_login(who)

    def prompt_login(self, why=""):
        msg = "EgoOps 登录态已失效%s。\\n\\n现在登录吗？登录时会弹出一个浏览器窗口，用手机验证码登一次就好。\\n" % (
            ("（%s）" % why) if why else "")
        if messagebox.askyesno(APP_NAME, msg):
            self.do_login()

    def do_login(self):
        self.lbl_egoops.config(text="EgoOps：正在打开登录窗口…", foreground="#B45309")
        self.lbl_task.config(text="请在弹出的窗口里登录 EgoOps")

        def work():
            try:
                mod = self._load_egoops_auth_mod()
                ok, info = mod.refresh(log=lambda m: self.ui(self.lbl_task.config, text=str(m)))
            except Exception as e:
                ok, info = False, str(e)
            self.ui(self._after_login, ok, info)

        threading.Thread(target=work, daemon=True).start()

    def _after_login(self, ok, info):
        if ok:
            self.lbl_egoops.config(text="EgoOps：已登录", foreground="#15803D")
            self.lbl_task.config(text=str(info))
            messagebox.showinfo(APP_NAME, str(info))
            self.check_egoops_login()
        else:
            self.lbl_egoops.config(text="EgoOps：未登录", foreground="#B91C1C")
            self.lbl_task.config(text=str(info))
            messagebox.showwarning(APP_NAME, str(info))

    # ---------------------------------------------------------------- 样式''')

# ---------- 3) 顶栏加状态标签 ----------
s = s.replace('''        self.lbl_status = ttk.Label(head, text="未连接", style="Status.TLabel")
        self.lbl_status.pack(side="right")''',
'''        self.lbl_status = ttk.Label(head, text="未连接", style="Status.TLabel")
        self.lbl_status.pack(side="right")

        self.lbl_egoops = tk.Label(head, text="EgoOps：检查中…", font=("Microsoft YaHei UI", 9),
                                   bg="#F1F5F9", fg="#64748B", cursor="hand2")
        self.lbl_egoops.pack(side="right", padx=(0, 16))
        self.lbl_egoops.bind("<Button-1>", lambda e: self.do_login())''')

# ---------- 4) 菜单加「立即登录 EgoOps」 ----------
s = s.replace('''        m_mt.add_command(label="刷新 EgoOps 登录态", command=self.refresh_login_state)''',
'''        m_mt.add_command(label="立即登录 EgoOps（手机验证码）", command=self.do_login)
        m_mt.add_command(label="检查登录态", command=self.check_egoops_login)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('登录态检查已加')
