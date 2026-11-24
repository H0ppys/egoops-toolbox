"""收尾：右栏加宽、表头/列宽、登录提示缩短，避免文字被切。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 右栏宽一点、窗口宽一点
s = s.replace('side = ttk.Frame(body, width=330, padding=(16, 0, 0, 0))',
              'side = ttk.Frame(body, width=360, padding=(16, 0, 0, 0))')
s = s.replace('root.geometry("1500x900")', 'root.geometry("1560x900")')

# 2) 列宽：地址/时间收一点，名字宽一点
s = s.replace('''        spec = [("sel", "选", 44, "center"), ("name", "门店 / 文件", 230, "w"),
                ("address", "现场地址", 300, "w"), ("vendor", "厂商", 110, "center"),
                ("time", "采集时间", 140, "center"), ("draft", "EgoOps", 110, "center")]''',
'''        spec = [("sel", "选", 46, "center"), ("name", "门店 / 文件", 210, "w"),
                ("address", "现场地址", 250, "w"), ("vendor", "厂商", 96, "center"),
                ("time", "采集时间", 118, "center"), ("draft", "EgoOps", 96, "center")]''')

# 3) 登录提示按钮文字短一点
s = s.replace('self.btn_login.config(text="EgoOps 登录已失效，点这里登录", style="Danger.TButton")',
              'self.btn_login.config(text="点击登录 EgoOps", style="Danger.TButton")')

# 4) 引导文字换行宽度跟着右栏
s = s.replace('wraplength=280, justify="left")', 'wraplength=310, justify="left")')

# 5) 状态文字精简
s = s.replace('self.lbl_egoops.config(text="EgoOps：已登录 %s" % who, foreground="#15803D")',
              'self.lbl_egoops.config(text="EgoOps 已登录（%s）" % who, foreground="#15803D")')
s = s.replace('self.lbl_egoops.config(text="EgoOps：登录已失效", foreground="#B91C1C")',
              'self.lbl_egoops.config(text="EgoOps 登录已失效", foreground="#B91C1C")')
s = s.replace('self.lbl_egoops.config(text="EgoOps：检查中…", foreground="#64748B")',
              'self.lbl_egoops.config(text="EgoOps 检查中…", foreground="#64748B")')
s = s.replace('self.lbl_egoops.config(text="EgoOps：正在打开登录窗口…", foreground="#B45309")',
              'self.lbl_egoops.config(text="正在打开登录窗口…", foreground="#B45309")')
s = s.replace('text="EgoOps：检查中…"', 'text="EgoOps 检查中…"')

io.open(p, 'w', encoding='utf-8').write(s)
print('收尾调整完成')
