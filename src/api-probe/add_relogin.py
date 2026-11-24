import io

p = 'viewer/egoops_auth.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('''def refresh():
    """用保存的态开浏览器，若仍登录就重新抓一遍 cookie/storage 刷新时间戳"""
    if not os.path.exists(AUTH):
        return False, "没有登录态文件，需要先在 Edge 里登录一次 EgoOps（用带调试端口的流程）"
    data = _load()
    tok = token_of(data)
    ok, who = alive(tok)
    if ok:
        data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        data["verified"] = who
        with open(AUTH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        return True, "登录态有效（%s），已刷新时间戳" % who
    return False, "登录态已失效（%s），请重新登录后用「抓取登录态」保存" % who''',
'''EDGE = r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
CDP = "http://127.0.0.1:9222"


def _edge_with_cdp():
    """没有可用 CDP 端口时，起一个带调试端口的 Edge（独立配置，不动日常浏览器）"""
    import subprocess
    import urllib.request
    try:
        urllib.request.urlopen(CDP + "/json/version", timeout=2).read()
        return True
    except Exception:
        pass
    if not os.path.exists(EDGE):
        return False
    prof = os.path.join(os.environ.get("TEMP") or ".", "egoops-edge-prof")
    subprocess.Popen([EDGE, "--remote-debugging-port=9222", "--user-data-dir=" + prof,
                      "--start-maximized", "https://egoops.meituan.com/assignment"])
    for _ in range(40):
        try:
            urllib.request.urlopen(CDP + "/json/version", timeout=2).read()
            return True
        except Exception:
            time.sleep(1)
    return False


def relogin(wait_seconds=300, log=print):
    """打开浏览器让用户登录一次，然后把 cookie/storage 抓下来"""
    from playwright.sync_api import sync_playwright

    if not _edge_with_cdp():
        return False, "起不来带调试端口的 Edge"

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        ctx = b.contexts[0]
        page = None
        for x in ctx.pages:
            if "meituan" in x.url:
                page = x
                break
        if page is None:
            page = ctx.new_page()
        page.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=60000)

        log("请在弹出的浏览器窗口里登录 EgoOps（手机验证码），最多等 %d 秒…" % wait_seconds)
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if "egoops.meituan.com" in page.url and "login" not in page.url:
                break
            time.sleep(3)
        if "login" in page.url:
            return False, "没有完成登录"

        page.wait_for_timeout(4000)
        storage = page.evaluate("""() => {
            const dump = s => { const o = {}; for (let i = 0; i < s.length; i++) { const k = s.key(i); o[k] = s.getItem(k); } return o; };
            return { local: dump(localStorage), session: dump(sessionStorage) };
        }""")
        data = {
            "url": page.url,
            "cookies": ctx.cookies(),
            "storage": storage,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        os.makedirs(os.path.dirname(AUTH), exist_ok=True)
        with open(AUTH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        ok, who = alive(token_of(data))
        return (True, "已保存登录态（%s）" % who) if ok else (False, "抓到了但校验失败")


def refresh(wait_seconds=300, log=print):
    """先看保存的态还活着吗，死了就引导重新登录一次再抓"""
    if os.path.exists(AUTH):
        data = _load()
        ok, who = alive(token_of(data))
        if ok:
            data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            data["verified"] = who
            with open(AUTH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            return True, "登录态有效（%s），已刷新" % who
        log("登录态失效（%s），需要重新登录" % who)
    return relogin(wait_seconds=wait_seconds, log=log)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('relogin 已加入')
