"""打开设置窗口并截图，验证底部按钮和三个页签。"""
import os
import sys
import time

sys.path.insert(0, "viewer")
os.environ["APPDATA"] = os.path.abspath("viewer/.testappdata")

import tkinter as tk  # noqa: E402
from app import App  # noqa: E402
from PIL import ImageGrab  # noqa: E402

root = tk.Tk()
app = App(root, autoconnect=False)


def shoot():
    app.open_settings()
    root.update()
    time.sleep(1.2)
    win = None
    for w in root.winfo_children():
        if isinstance(w, tk.Toplevel) and w.title() == "设置":
            win = w
    if win:
        win.lift()
        win.focus_force()
        root.update()
        time.sleep(0.8)
        x, y = win.winfo_rootx(), win.winfo_rooty()
        w, h = win.winfo_width(), win.winfo_height()
        ImageGrab.grab(bbox=(x - 8, y - 40, x + w + 8, y + h + 8)).save("docs/settings-shot.png")
        print("截图完成", w, "x", h)
    else:
        print("没找到设置窗口")
    root.destroy()


root.after(800, shoot)
root.mainloop()
