import io

p = 'tools/demo_save_draft.py'
s = io.open(p, encoding='utf-8').read()

# 弹层（下拉选项）渲染在 dialog 之外，必须用 page 级定位
s = s.replace('''        # 采集场景分类
        dlg.get_by_text("请选择一级和二级分类", exact=False).first.click()
        pg.wait_for_timeout(900)
        dlg.get_by_role("button", name="餐饮", exact=True).first.click()
        pg.wait_for_timeout(700)
        dlg.get_by_role("button", name="餐厅", exact=True).first.click()
        pg.wait_for_timeout(600)''',
'''        # 采集场景分类（下拉弹层在 dialog 之外的 portal 里，必须用 page 级定位）
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(400)
        pg.get_by_text("请选择一级和二级分类", exact=False).first.click()
        pg.wait_for_timeout(1000)
        pg.get_by_role("button", name="餐饮", exact=True).first.click()
        pg.wait_for_timeout(900)
        pg.get_by_role("button", name="餐厅", exact=True).first.click()
        pg.wait_for_timeout(700)''')

s = s.replace('''        dlg.get_by_text("请选择省、市、区（县）", exact=False).first.click()
        pg.wait_for_timeout(900)
        for nm in (parts["province"], parts["city"], parts["district"]):
            dlg.get_by_role("button", name=nm, exact=True).first.click()
            pg.wait_for_timeout(700)''',
'''        pg.get_by_text("请选择省、市、区（县）", exact=False).first.click()
        pg.wait_for_timeout(1000)
        for nm in (parts["province"], parts["city"], parts["district"]):
            pg.get_by_role("button", name=nm, exact=True).first.click()
            pg.wait_for_timeout(800)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched demo')
