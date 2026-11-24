import io
import re

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

start = s.index("    def do_login():")
end = s.index('    ttk.Button(btns, text="登录 / 更新令牌", command=do_login)')

new = '''    def do_login():
        top = tk.Toplevel(root)
        top.title("登录 egoops")
        top.geometry("760x460")
        proc_box = {"proc": None}

        ttk.Label(top, text="方式一（推荐）：用专用浏览器登录一次，之后自动续期",
                  font=("Microsoft YaHei UI", 9, "bold"), padding=(8, 8, 8, 0)).pack(anchor="w")

        row = ttk.Frame(top)
        row.pack(fill="x", padx=10, pady=6)

        def open_login():
            try:
                proc_box["proc"] = launch_browser(headless=False)
            except Exception as e:
                q.put(("log", f"启动浏览器失败：{e}"))
                return
            q.put(("log", "已打开浏览器，请在窗口里完成 egoops 登录，然后点『读取令牌』"))

        def read_after_login():
            proc = proc_box["proc"]
            if proc:
                try:
                    proc.terminate()
                    time.sleep(1.5)
                    proc.kill()
                except Exception:
                    pass
            tok = scan_token_from_profile()
            if not tok:
                q.put(("log", "没读到令牌：请确认浏览器里已登录到 egoops 的 /recordings 页面"))
                return
            save_token({"access_token": tok["token"], "exp": tok["exp"], "payload": tok["payload"]},
                       os.path.join(APP_DIR, "egoops_token.json"))
            q.put(("log", f"✔ 登录成功：{tok['payload'].get('name', '?')}，"
                          f"到期 {datetime.fromtimestamp(tok['exp']):%Y-%m-%d %H:%M}"))
            top.destroy()

        ttk.Button(row, text="① 打开浏览器登录", command=open_login).pack(side="left")
        ttk.Button(row, text="② 我已完成登录，读取令牌", command=read_after_login).pack(side="left", padx=8)

        ttk.Separator(top).pack(fill="x", padx=10, pady=8)
        ttk.Label(top, text="方式二：直接粘贴（F12 → Network → 任意 /api/v1 请求 → Copy as cURL）").pack(anchor="w", padx=10)
        txt = tk.Text(top, height=8, font=("Consolas", 9))
        txt.pack(fill="both", expand=True, padx=10, pady=6)

        def apply():
            info = save_pasted_token(txt.get("1.0", "end"), os.path.join(APP_DIR, "egoops_token.json"))
            if not info:
                q.put(("log", "解析失败：请确认粘贴的是 cURL 或包含 Bearer 的请求头"))
                return
            q.put(("log", f"令牌已保存：{info['payload'].get('name', '?')}，"
                          f"到期 {datetime.fromtimestamp(info['exp']):%Y-%m-%d %H:%M}"))
            top.destroy()

        bar2 = ttk.Frame(top)
        bar2.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bar2, text="保存粘贴的令牌", command=apply).pack(side="left")
        ttk.Button(bar2, text="关闭", command=top.destroy).pack(side="left", padx=8)

'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
