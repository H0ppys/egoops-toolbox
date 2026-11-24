"""模拟点一次「下载勾选」，看到底卡在哪（不弹目录框，直接注入目标目录）。"""
import os
import sys
import time
import tkinter as tk

sys.path.insert(0, "viewer")
os.environ["APPDATA"] = os.path.abspath("viewer/.testappdata")

import app as appmod  # noqa: E402

root = tk.Tk()
root.geometry("1400x880")
a = appmod.App(root, autoconnect=True)
root.update()

print("current_site:", a.current_site)
print("busy:", a.busy)


def step1():
    site = next((s for s in a.tree.get_children() if s in a.site_rows), None)
    if not site:
        print("没有采集点"); root.destroy(); return
    a.tree.item(site, open=True)
    a.on_tree_open(None)
    root.after(2500, lambda: step2(site))


def step2(site):
    a._set_checked(site, True, cascade=True)
    a._sync_ancestors(site)
    a.update_check_label()
    files = a.checked_files()
    print("checked_files:", len(files))
    print("current_site 名称:", (a.current_site or {}).get("name"))

    # 跳过目录选择，直接给一个临时目录
    a.ask_dir = lambda: os.path.abspath("sim/dl_test")
    os.makedirs("sim/dl_test", exist_ok=True)

    try:
        a.download_checked()
        print("download_checked 已调用，busy=", a.busy)
    except Exception as e:
        import traceback
        traceback.print_exc()

    root.after(25000, step3)


def step3():
    d = os.path.abspath("sim/dl_test")
    got = []
    for base, _, names in os.walk(d):
        for n in names:
            got.append(n)
    print("下载到文件:", len(got), got[:5])
    print("busy:", a.busy, "| 状态栏:", a.lbl_task.cget("text"))
    root.destroy()


root.after(2500, step1)
root.mainloop()

