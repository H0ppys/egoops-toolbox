import io, json, os, shutil

# 1) 登录态存到稳定位置
src = 'docs/egoops_auth.json'
dst_dir = os.path.join(os.environ['APPDATA'], 'egoops-viewer')
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'egoops_auth.json')
shutil.copy2(src, dst)
print('auth ->', dst, os.path.getsize(dst), 'bytes')

# 2) fill_egoops 优先用存下来的登录态
p = 'viewer/fill_egoops.py'
s = io.open(p, encoding='utf-8').read()

anchor = 'def run_fill(site, fields=None,'
helper = '''AUTH_FILE = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"),
                         "egoops-viewer", "egoops_auth.json")


def _seed_script():
    """把保存的 localStorage / sessionStorage 在页面加载前写回去"""
    if not os.path.exists(AUTH_FILE):
        return None, None
    data = json.load(open(AUTH_FILE, encoding="utf-8"))
    storage = data.get("storage") or {}
    seed = {"local": storage.get("local") or {}, "session": storage.get("session") or {}}
    script = """
    (() => {
      const seed = %s;
      try {
        for (const [k, v] of Object.entries(seed.local || {})) localStorage.setItem(k, v);
        for (const [k, v] of Object.entries(seed.session || {})) sessionStorage.setItem(k, v);
      } catch (e) {}
    })();
    """ % json.dumps(seed, ensure_ascii=False)
    return data.get("cookies") or [], script


'''
s = s.replace(anchor, helper + anchor, 1)

old_launch = '''    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=prof,
                channel="msedge",
                headless=headless,
                no_viewport=True,
                args=["--start-maximized"],
            )
        except Exception as e:'''
new_launch = '''    cookies, script = _seed_script()
    with sync_playwright() as p:
        try:
            if cookies is not None:
                browser = p.chromium.launch(channel="msedge", headless=headless)
                ctx = browser.new_context(no_viewport=False)
                try:
                    ctx.add_cookies(cookies)
                except Exception as e:
                    log("注 cookie 失败（继续试）：%s" % e)
                if script:
                    ctx.add_init_script(script)
                log("使用已保存的登录态（免登录）")
            else:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=prof,
                    channel="msedge",
                    headless=headless,
                    no_viewport=True,
                    args=["--start-maximized"],
                )
        except Exception as e:'''
assert old_launch in s
s = s.replace(old_launch, new_launch)

io.open(p, 'w', encoding='utf-8').write(s)
print('fill_egoops patched')
