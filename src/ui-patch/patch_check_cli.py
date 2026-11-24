import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

old = '''    if "--as-user" in argv:
        cfg["asIdentity"] = "user"'''
new = '''    if "--as-user" in argv:
        cfg["asIdentity"] = "user"
    if "--check" in argv:
        ok1, msg1 = check_egoops(cfg)
        print(f"[1] egoops 登录：{'OK' if ok1 else 'NG'}  {msg1}")
        ok2, msg2, how = check_feishu(cfg)
        print(f"[2] 飞书写入：{'OK' if ok2 else 'NG'}  {msg2}")
        print(f"    写入方式：{how}")
        return 0 if (ok1 and ok2) else 1'''
if old not in s:
    raise SystemExit("run_cli 锚点未找到")
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("patched check")
