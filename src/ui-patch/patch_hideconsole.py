import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

helper = '''
def hide_console():
    """GUI 模式下隐藏控制台窗口（打包为 console 版时用）。"""
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def run_gui():
'''

if "def hide_console()" not in s:
    s = s.replace("\ndef run_gui():\n", helper, 1)
    s = s.replace('''    import tkinter as tk
    from tkinter import ttk, scrolledtext

    cfg = load_cfg()''', '''    import tkinter as tk
    from tkinter import ttk, scrolledtext

    hide_console()
    cfg = load_cfg()''')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
