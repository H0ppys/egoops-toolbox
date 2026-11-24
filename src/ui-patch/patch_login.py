import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

# 1) 解析用户粘贴的 token / cURL
helper = '''
def parse_token_input(text):
    """从粘贴内容中提取 access_token：支持纯 JWT、Authorization 头、整段 cURL。"""
    import re
    if not text:
        return None
    text = text.strip().strip('"').strip("'")
    m = re.search(r"[Bb]earer\\s+([A-Za-z0-9_\\-\\.]{60,})", text)
    if m:
        return m.group(1)
    m = re.search(r"eyJ[A-Za-z0-9_\\-]+\\.[A-Za-z0-9_\\-]+\\.[A-Za-z0-9_\\-]+", text)
    if m:
        return m.group(0)
    if text.count(".") == 2 and len(text) > 100 and " " not in text:
        return text
    return None


def save_pasted_token(text, path):
    tok = parse_token_input(text)
    if not tok:
        return None
    pl = jwt_payload(tok)
    save_token({"access_token": tok, "exp": pl.get("exp") or 0, "payload": pl}, path)
    return {"token": tok, "exp": pl.get("exp") or 0, "payload": pl}


def open_login_page():
    try:
        os.startfile("https://egoops.meituan.com/recordings")
    except Exception:
        pass


'''
s = s.replace("\ndef hide_console():", helper + "def hide_console():", 1)

# 2) CLI 支持 --set-token
s = s.replace('''def run_cli(argv):
    cfg = load_cfg()''',
'''def run_cli(argv):
    cfg = load_cfg()
    token_file = os.path.join(APP_DIR, "egoops_token.json")
    if "--set-token" in argv:
        i = argv.index("--set-token")
        raw = argv[i + 1] if i + 1 < len(argv) else ""
        info = save_pasted_token(raw, token_file)
        if not info:
            print("未能从内容中解析出 token")
            return 2
        print(f"token 已保存：{info['payload'].get('name', '?')}，"
              f"到期 {datetime.fromtimestamp(info['exp']):%Y-%m-%d %H:%M}")
        if "--only-save" in argv:
            return 0''')

# 3) GUI：加「登录/更新令牌」按钮 + 对话框
s = s.replace('''    ttk.Button(btns, text="开始刷新（自动覆盖）", command=do_refresh).pack(side="left")''',
'''    def do_login():
        top = tk.Toplevel(root)
        top.title("设置登录令牌")
        top.geometry("760x360")
        ttk.Label(top, text="① 点下面按钮打开 egoops（或自己打开），确保已登录", padding=8).pack(anchor="w")
        ttk.Button(top, text="打开 egoops 页面", command=open_login_page).pack(anchor="w", padx=10)
        ttk.Label(top, text="② F12 → Network → 点任意 /api/v1 请求 → 右键 Copy as cURL → 粘贴到下面", padding=8).pack(anchor="w")
        txt = tk.Text(top, height=10, font=("Consolas", 9))
        txt.pack(fill="both", expand=True, padx=10)

        def apply():
            info = save_pasted_token(txt.get("1.0", "end"), os.path.join(APP_DIR, "egoops_token.json"))
            if not info:
                q.put(("log", "解析失败：请确认粘贴的是 cURL 或包含 Bearer 的请求头"))
                return
            q.put(("log", f"登录令牌已保存：{info['payload'].get('name', '?')}，"
                          f"到期 {datetime.fromtimestamp(info['exp']):%Y-%m-%d %H:%M}"))
            top.destroy()

        bar2 = ttk.Frame(top)
        bar2.pack(fill="x", padx=10, pady=8)
        ttk.Button(bar2, text="保存令牌", command=apply).pack(side="left")
        ttk.Button(bar2, text="取消", command=top.destroy).pack(side="left", padx=8)

    ttk.Button(btns, text="登录 / 更新令牌", command=do_login).pack(side="left", padx=(0, 8))
    ttk.Button(btns, text="开始刷新（自动覆盖）", command=do_refresh).pack(side="left")''')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
