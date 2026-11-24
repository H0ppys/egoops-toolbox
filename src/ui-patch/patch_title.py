import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('APP_TITLE = "EgoOps 执行者数据 → 飞书表格"',
              'APP_TITLE = "EgoOps 任务合格率 → 飞书表格（任务 × 执行者）"')
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
