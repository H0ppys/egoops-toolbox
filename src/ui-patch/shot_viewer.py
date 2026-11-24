"""启动查看器 → 置前 → 截屏，用于展示界面。"""
import ctypes
import os
import subprocess
import time

from PIL import ImageGrab

EXE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "viewer", "dist-dir", "采集数据查看器", "采集数据查看器.exe"))
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "docs", "viewer-new.png"))

env = dict(os.environ)
env["APPDATA"] = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "..", "viewer", ".testappdata"))

p = subprocess.Popen([EXE], env=env)
time.sleep(22)

user32 = ctypes.windll.user32
hwnd = user32.FindWindowW(None, "采集数据查看器")
print("hwnd:", hwnd)
if hwnd:
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(1.5)

img = ImageGrab.grab()
img.save(OUT)
print("saved", OUT, img.size)
p.terminate()

