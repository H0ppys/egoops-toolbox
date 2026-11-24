import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

helper = '''
# ---------------------------------------------------------------- 专用浏览器登录
BROWSER_PROFILE = os.path.join(APP_DIR, "browser_profile")
EGOOPS_URL = "https://egoops.meituan.com/recordings"


def find_browser():
    for p in (
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\\Program Files (x86)"),
                     "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\\Program Files"),
                     "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\\Program Files"),
                     "Google", "Chrome", "Application", "chrome.exe"),
    ):
        if os.path.isfile(p):
            return p
    return None


def scan_token_from_profile():
    """登录后从专用配置的 Session Storage 里读 oidc 令牌（无需 Cookie 数据库）。"""
    markers = ['"access_token":"'.encode("utf-16-le"), b'"access_token":"']
    base = os.path.join(BROWSER_PROFILE, "Default", "Session Storage")
    if not os.path.isdir(base):
        return None
    best = None
    for name in sorted(os.listdir(base)):
        fp = os.path.join(base, name)
        if not os.path.isfile(fp):
            continue
        try:
            data = open(fp, "rb").read()
        except Exception:
            continue
        for mk in markers:
            tok = _utf16_value_after(data, mk)
            if not tok:
                continue
            tok = tok.strip()
            if tok.count(".") != 2 or len(tok) < 100:
                continue
            pl = jwt_payload(tok)
            exp = pl.get("exp") or 0
            if best is None or exp > best["exp"]:
                best = {"token": tok, "exp": exp, "payload": pl}
    return best


def launch_browser(headless=False, wait_close=None):
    exe = find_browser()
    if not exe:
        raise RuntimeError("找不到 Edge/Chrome 浏览器")
    os.makedirs(BROWSER_PROFILE, exist_ok=True)
    args = [
        f"--user-data-dir={BROWSER_PROFILE}",
        "--no-first-run", "--no-default-browser-check",
        "--disable-features=msEdgeSplashScreen",
    ]
    if headless:
        args += ["--headless=new", "--disable-gpu"]
    args.append(EGOOPS_URL)
    import subprocess
    proc = subprocess.Popen([exe] + args, close_fds=True)
    return proc


'''
s = s.replace("\ndef parse_token_input(text):", helper + "def parse_token_input(text):", 1)

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
