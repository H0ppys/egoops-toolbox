"""验证勾选级联：勾采集点 → 下级全勾；取消一个文件 → 采集点自动取消。"""
import os
import sys
import tkinter as tk

sys.path.insert(0, "viewer")
os.environ["APPDATA"] = os.path.abspath("viewer/.testappdata")

from app import App  # noqa: E402

root = tk.Tk()
root.geometry("1400x880")
app = App(root, autoconnect=True)
root.update()


def dump(tag):
    print("\n" + tag)
    for site in app.tree.get_children():
        if site not in app.site_rows:
            continue
        print("  采集点 %-6s %s" % (app.tree.set(site, "sel"), app.tree.set(site, "name")))
        for t in app.tree.get_children(site):
            print("   任务 %s  %s" % (app.tree.set(t, "sel"), app.tree.set(t, "name")))
            for f in app.tree.get_children(t):
                print("     文件 %s  %s" % (app.tree.set(f, "sel"), app.tree.set(f, "name")))
    print("  checked 数量:", len(app.checked), "| 勾选文件数:", len(app.checked_files()))


def step1():
    site = next((s for s in app.tree.get_children() if s in app.site_rows), None)
    if not site:
        print("没有采集点"); root.destroy(); return
    app.tree.item(site, open=True)
    app.on_tree_open(None)
    root.after(2500, lambda: step2(site))


def step2(site):
    # 模拟点采集点这一行的勾选框
    app._set_checked(site, True, cascade=True)
    app._sync_ancestors(site)
    app.update_check_label()
    dump("[勾选采集点后]")

    # 取消其中一个文件，上级应自动取消
    task = app.tree.get_children(site)[0]
    files = app.tree.get_children(task)
    if files:
        app._set_checked(files[0], False, cascade=True)
        app._sync_ancestors(files[0])
        app.update_check_label()
        dump("[取消一个文件后]")

    root.destroy()


root.after(2500, step1)
root.mainloop()
