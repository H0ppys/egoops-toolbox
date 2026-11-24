"""让「点击登录」一定能弹出可见的浏览器窗口：
   · 先清掉残留的临时登录窗口
   · 用独立配置 + 调试端口新开一个窗口，并置到最前
"""

import io

p = 'viewer/egoops_auth.py'
s = io.open(p, encoding='utf-8').read()

old_start = s.index('def _edge_with_cdp():')
old_end = s.index('def relogin(')
new = '''def _kill_temp_edge():
    """关掉之前残留的临时登录窗口（只杀用 egoops-edge-prof 的那个）"""
    try:
        import subprocess
        ps = ("Get-CimInstance Win32_Process -Filter \\"Name='msedge.exe'\\" | "
              "Where-Object { $_.CommandLine -like '*egoops-edge-prof*' } | "
              "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=20)
    except Exception:
        pass


def _edge_with_cdp():
    """起一个带调试端口的 Edge（独立配置，不动日常浏览器），并把它置前"""
    import subprocess
    import urllib.request

    # 已经有可用的调试端口就直接用
    try:
        urllib.request.urlopen(CDP + "/json/version", timeout=2).read()
        return True
    except Exception:
        pass

    if not os.path.exists(EDGE):
        return False

    _kill_temp_edge()
    time.sleep(1)

    prof = os.path.join(os.environ.get("TEMP") or ".", "egoops-edge-prof")
    try:
        subprocess.Popen([EDGE,
                          "--remote-debugging-port=9222",
                          "--user-data-dir=" + prof,
                          "--no-first-run",
                          "--no-default-browser-check",
                          "--new-window",
                          "https://egoops.meituan.com/assignment"],
                         close_fds=True)
    except Exception:
        return False

    ok = False
    for _ in range(40):
        try:
            urllib.request.urlopen(CDP + "/json/version", timeout=2).read()
            ok = True
            break
        except Exception:
            time.sleep(1)
    if not ok:
        return False

    # 把窗口提到最前
    try:
        import ctypes
        u = ctypes.windll.user32
        for _ in range(10):
            hwnd = u.FindWindowW(None, "美团 M-EgoOps")
            if not hwnd:
                hwnd = u.FindWindowW(None, "Microsoft\\u200b Edge")
            if hwnd:
                u.ShowWindow(hwnd, 9)
                u.SetForegroundWindow(hwnd)
                break
            time.sleep(0.5)
    except Exception:
        pass

    return True


'''
s = s[:old_start] + new + s[old_end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('登录窗口启动逻辑已改')
