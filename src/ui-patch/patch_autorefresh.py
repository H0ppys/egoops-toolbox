import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

# ---------- 1) 自动静默续期：用专用配置起无头浏览器，再读 sessionStorage ----------
auto = '''
def auto_refresh_from_profile(log=None):
    """用专用浏览器配置静默完成 SSO 登录并读取新令牌。"""
    if not os.path.isdir(BROWSER_PROFILE):
        return None
    try:
        proc = launch_browser(headless=True)
    except Exception as e:
        if log:
            log(f"启动浏览器失败：{e}")
        return None
    try:
        for _ in range(15):
            time.sleep(2)
            tok = scan_token_from_profile()
            if tok and tok["exp"] - time.time() > 600:
                return tok
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        time.sleep(1)
        try:
            proc.kill()
        except Exception:
            pass
    return scan_token_from_profile()

'''
s = s.replace("\ndef launch_browser(", auto + "\ndef launch_browser(", 1)

# ---------- 2) sync 里先用缓存 → 再从专用配置静默续期 ----------
s = s.replace('''        log("缓存登录态不可用/即将过期，从 Edge 读取…")
        tok = extract_token_from_edge(log)''',
'''        log("缓存登录态不可用/即将过期，先尝试用专用浏览器配置静默续期…")
        tok = auto_refresh_from_profile(log)
        if tok:
            save_token({"access_token": tok["token"], "exp": tok["exp"], "payload": tok["payload"]}, token_file)
            log(f"静默续期成功：{tok['payload'].get('name', '?')}（{datetime.fromtimestamp(tok['exp']):%m-%d %H:%M} 到期）")
    if not tok:
        log("再从 Edge 现有会话读取…")
        tok = extract_token_from_edge(log)''')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
