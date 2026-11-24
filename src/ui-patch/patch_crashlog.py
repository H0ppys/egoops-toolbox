import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

old = '''def main():
    if "--hidden" in sys.argv:
        hide_console()
    if "--cli" in sys.argv:
        sys.exit(run_cli(sys.argv))
    run_gui()'''
new = '''def main():
    if "--hidden" in sys.argv:
        hide_console()
    if "--cli" in sys.argv:
        sys.exit(run_cli(sys.argv))
    try:
        run_gui()
    except Exception:
        detail = traceback.format_exc()
        try:
            with open(os.path.join(APP_DIR, "egoops_crash.log"), "a", encoding="utf-8") as f:
                f.write(f"\\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\\n{detail}\\n")
        except Exception:
            pass
        raise'''
if old not in s:
    raise SystemExit("main() 结构不符")
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
