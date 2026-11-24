"""登录态失效时不要弹模态框（打扰），改成右侧红色提示 + 按钮；建草稿时才拦。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 检查完成后不弹窗
s = s.replace('''            self.lbl_egoops.config(text="EgoOps：登录已失效（点这里登录）", foreground="#B91C1C")
            self.prompt_login(who)''',
'''            self.lbl_egoops.config(text="EgoOps：登录已失效", foreground="#B91C1C")
            try:
                self.btn_login.config(text="EgoOps 登录已失效，点这里登录", style="Danger.TButton")
                self.btn_login.pack(fill="x", pady=(0, 8), before=self.lbl_section)
            except Exception:
                pass''')

# 2) 登录成功后隐藏按钮
s = s.replace('''        if ok:
            self.lbl_egoops.config(text="EgoOps：已登录 %s" % who, foreground="#15803D")''',
'''        if ok:
            self.lbl_egoops.config(text="EgoOps：已登录 %s" % who, foreground="#15803D")
            try:
                self.btn_login.pack_forget()
            except Exception:
                pass''')

# 3) 侧栏加登录按钮（默认不显示）
s = s.replace('''        self.lbl_section = ttk.Label(side, text="下一步", style="Section.TLabel")''',
'''        self.btn_login = ttk.Button(side, text="登录 EgoOps", style="Danger.TButton", command=self.do_login)

        self.lbl_section = ttk.Label(side, text="下一步", style="Section.TLabel")''')

# 4) 建草稿前检查登录态
s = s.replace('''        if not self._ensure_meituan(site):
            return''',
'''        if not self._ensure_meituan(site):
            return
        if getattr(self, "login_ok", None) is False:
            if messagebox.askyesno(APP_NAME, "EgoOps 登录已失效，需要先登录才能建草稿。\\n\\n现在登录吗？"):
                self.do_login()
            return''')

# 5) Danger.TButton 补样式
s = s.replace('''        s.configure("Card.TFrame", relief="solid", borderwidth=1)''',
'''        s.configure("Card.TFrame", relief="solid", borderwidth=1)
        try:
            s.configure("Danger.TButton", foreground="#B91C1C")
        except Exception:
            pass''')

io.open(p, 'w', encoding='utf-8').write(s)
print('登录提示改成非打断式')
