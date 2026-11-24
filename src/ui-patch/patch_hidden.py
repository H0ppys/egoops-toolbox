import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

# main(): --hidden 时隐藏控制台窗口（供定时任务静默运行）
old = '''def main():
    if "--cli" in sys.argv:
        sys.exit(run_cli(sys.argv))
    run_gui()'''
new = '''def main():
    if "--hidden" in sys.argv:
        hide_console()
    if "--cli" in sys.argv:
        sys.exit(run_cli(sys.argv))
    run_gui()'''
if old in s:
    s = s.replace(old, new)
else:
    raise SystemExit("main() 未找到预期结构")

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
