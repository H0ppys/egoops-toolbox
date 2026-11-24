"""连上服务器、展开第一个采集点，截整窗，检查列对齐。"""
import os
import sys
import time
import tkinter as tk

sys.path.insert(0, "viewer")
os.environ["APPDATA"] = os.path.abspath("viewer/.testappdata")

from app import App  # noqa: E402
from PIL import ImageGrab  # noqa: E402

root = tk.Tk()
root.geometry("1440x880+40+40")
app = App(root, autoconnect=True)
root.update()


def step1():
    kids = app.tree.get_children()
    print("顶层行:", [(k, app.tree.item(k, "values")[:3]) for k in kids][:5])
    for k in kids:
        if k in app.site_rows:
            app.tree.item(k, open=True)
            app.on_tree_open(None)
            break
    root.after(2000, step2)


def step2():
    x, y = root.winfo_rootx(), root.winfo_rooty()
    w, h = root.winfo_width(), root.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save("docs/tree-check.png")
    for c in app.tree["columns"]:
        print("  列 %-7s width=%s stretch=%s" % (c, app.tree.column(c, "width"), app.tree.column(c, "stretch")))
    print("  #0 width=%s" % app.tree.column("#0", "width"))
    root.destroy()


root.after(2500, step1)
root.mainloop()
