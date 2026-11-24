import sys
import time

sys.path.insert(0, r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace")
import egoops_gui as g

print("APP_DIR:", g.APP_DIR)
print("浏览器:", g.find_browser())
print("专用配置目录:", g.BROWSER_PROFILE, "存在:", __import__("os").path.isdir(g.BROWSER_PROFILE))

proc = g.launch_browser(headless=False)
print("已启动浏览器 pid:", proc.pid)
time.sleep(6)
print("扫码/登录页应已打开；当前进程存活:", proc.poll() is None)
tok = g.scan_token_from_profile()
print("此刻能读到令牌:", bool(tok))
try:
    proc.terminate()
    time.sleep(1)
    proc.kill()
except Exception:
    pass
print("已关闭")
