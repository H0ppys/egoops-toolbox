import io

p = 'tools/demo_save_draft.py'
s = io.open(p, encoding='utf-8').read()

# Escape 会关掉弹窗 —— 去掉
s = s.replace('''        pg.keyboard.press("Escape")
        pg.wait_for_timeout(400)
''', '')

# 打开弹窗的判断改成更稳的写法，并在关闭时重开
s = s.replace('''        if "任务名称" not in pg.inner_text("body"):
            pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
            pg.wait_for_timeout(3500)
        dlg = pg.get_by_role("dialog")''',
'''        def ensure_dialog():
            if "任务名称" in pg.inner_text("body"):
                return True
            pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
            pg.wait_for_timeout(3500)
            return "任务名称" in pg.inner_text("body")

        ensure_dialog()
        dlg = pg.get_by_role("dialog")''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
