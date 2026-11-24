"""逐个打开对话框，检查按钮文字/尺寸是否正常（防止再出现空按钮）。"""
import os
import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, "viewer")
os.environ["APPDATA"] = os.path.abspath("viewer/.testappdata")

from app import App  # noqa: E402

root = tk.Tk()
root.geometry("1400x880")
app = App(root, autoconnect=False)
root.update()


def walk(w, depth=0):
    out = []
    for c in w.winfo_children():
        out.append((depth, c))
        out += walk(c, depth + 1)
    return out


def check(win, name):
    root.update()
    root.after(300)
    root.update_idletasks()
    bad = []
    for depth, c in walk(win):
        if isinstance(c, ttk.Button) or isinstance(c, tk.Button):
            txt = c.cget("text")
            h = c.winfo_height()
            w = c.winfo_width()
            if not str(txt).strip():
                bad.append(("空文字", c.winfo_class(), w, h))
            elif h < 18 and c.winfo_ismapped():
                bad.append(("太矮", str(txt), w, h))
    print("  [%s] 按钮检查: %s" % (name, "OK" if not bad else bad))


print("1) 设置窗口")
app.open_settings()
root.update()
tops = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
if tops:
    win = tops[-1]
    print("  尺寸:", win.winfo_width(), "x", win.winfo_height())
    check(win, "设置")
    win.destroy()

print("2) 一键建草稿的字段选择窗")
app.site_rows["site:test"] = {"id": "test", "name": "测试店", "address": "广东省湛江市", "area": 80,
                              "scene_label": "餐馆 / 餐厅"}
app.tree.insert("", "end", iid="site:test", text="", values=("☐", "测试店", "", "", "", "", "", ""))
app.tree.focus("site:test")
app.fill_egoops()
root.update()
tops = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
if tops:
    win = tops[-1]
    print("  尺寸:", win.winfo_width(), "x", win.winfo_height())
    check(win, "字段选择")
    win.destroy()

print("3) 邀请码页（设置里的第三个页签）")
app.open_settings()
root.update()
tops = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
if tops:
    win = tops[-1]
    for depth, c in walk(win):
        if isinstance(c, ttk.Notebook):
            c.select(2)
            root.update()
            break
    check(win, "邀请码页")
    win.destroy()

root.destroy()
print("检查完成")
