import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

old = '''    v_dry = tk.BooleanVar(value=False)
    ttk.Checkbutton(top, text="只预览（导出 CSV，不写表）", variable=v_dry).grid(row=2, column=1, sticky="w")'''
new = '''    ttk.Label(top, text="App ID：").grid(row=2, column=0, sticky="w", pady=3)
    v_appid = tk.StringVar(value=cfg.get("feishuAppId", ""))
    ttk.Entry(top, textvariable=v_appid, width=26).grid(row=2, column=1, sticky="w")
    ttk.Label(top, text="App Secret：").grid(row=2, column=2, sticky="e", padx=6)
    v_secret = tk.StringVar(value=cfg.get("feishuAppSecret", ""))
    ttk.Entry(top, textvariable=v_secret, width=34, show="*").grid(row=2, column=3, sticky="w")
    ttk.Label(top, text="（填了 App ID/Secret 就不再依赖 lark-cli，换电脑只带 exe 即可）",
              foreground="#666").grid(row=3, column=0, columnspan=4, sticky="w")

    v_dry = tk.BooleanVar(value=False)
    ttk.Checkbutton(top, text="只预览（导出 CSV，不写表）", variable=v_dry).grid(row=4, column=1, sticky="w")'''
if old not in s:
    raise SystemExit("布局锚点未找到")
s = s.replace(old, new)

old2 = '''    def pull_cfg():
        cfg["baseToken"] = v_base.get().strip()
        cfg["tableId"] = v_table.get().strip()
        cfg["full"] = bool(v_full.get())'''
new2 = '''    def pull_cfg():
        cfg["baseToken"] = v_base.get().strip()
        cfg["tableId"] = v_table.get().strip()
        cfg["feishuAppId"] = v_appid.get().strip()
        cfg["feishuAppSecret"] = v_secret.get().strip()
        cfg["full"] = bool(v_full.get())'''
if old2 not in s:
    raise SystemExit("pull_cfg 锚点未找到")
s = s.replace(old2, new2)

io.open(p, "w", encoding="utf-8").write(s)
print("patched gui")
