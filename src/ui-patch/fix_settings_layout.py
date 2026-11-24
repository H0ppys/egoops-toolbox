import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 底部按钮条提前 pack（否则被 Notebook 的 expand 挤成一条缝，按钮文字看起来是空的）
old = '''        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=12, pady=12)'''
new = '''        bar = ttk.Frame(win)
        bar.pack(side="bottom", fill="x", padx=12, pady=(0, 12))

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=12, pady=12)'''
assert old in s
s = s.replace(old, new)

# 去掉后面重复创建 bar 的那两行
s = s.replace('''        bar = ttk.Frame(win)
        bar.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(bar, text="保存", style="Primary.TButton", command=save_all).pack(side="right")''',
'''        ttk.Button(bar, text="保存", style="Primary.TButton", command=save_all).pack(side="right")''')

# 2) 窗口高一点，内容不被压
s = s.replace('win.geometry("620x520")', 'win.geometry("640x600")')

# 3) 老的 http 地址自动升级到 https（服务器已开 443）
s = s.replace('''    def __init__(self, root, autoconnect=True):''', '''    def _upgrade_server_url(self):
        srv = (self.cfg.get("server") or "").strip()
        if srv.startswith("http://<FILL_ME>/relay"):
            self.cfg["server"] = srv.replace("http://", "https://", 1)
            try:
                save_config(self.cfg)
            except Exception:
                pass

    def __init__(self, root, autoconnect=True):''')

io.open(p, 'w', encoding='utf-8').write(s)
print('设置窗按钮 + 地址升级 已改')
