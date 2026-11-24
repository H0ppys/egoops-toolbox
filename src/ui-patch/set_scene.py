"""在当前打开的弹窗里，把采集场景分类选上（餐饮 / 餐厅）。"""
import os
import sys

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))

ALIAS = {"餐馆": "餐饮", "餐厅": "餐饮"}

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)
    print("URL:", pg.url)

    # 收起刚才展开的下拉（点空白）
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(500)

    combo = pg.get_by_text("请选择一级和二级分类", exact=False).first
    combo.click()
    pg.wait_for_timeout(1200)

    cat = ALIAS.get("餐馆", "餐馆")
    picked = False
    for name in ("餐馆", "餐饮"):
        try:
            btn = pg.get_by_role("button", name=name, exact=True)
            if btn.count():
                btn.first.click()
                print("✓ 一级分类:", name)
                picked = True
                break
        except Exception as e:
            print("一级失败", name, e)
    if not picked:
        print("✗ 没找到一级分类")
        sys.exit(0)

    pg.wait_for_timeout(1200)
    pg.screenshot(path=os.path.join(OUT, "scene-1-l1.png"))

    ok2 = False
    for name in ("餐厅", "餐馆"):
        try:
            btn = pg.get_by_role("button", name=name, exact=True)
            if btn.count():
                btn.first.click()
                print("✓ 二级分类:", name)
                ok2 = True
                break
        except Exception as e:
            print("二级失败", name, e)

    pg.wait_for_timeout(1000)
    pg.screenshot(path=os.path.join(OUT, "scene-2-l2.png"))
    body = pg.inner_text("body")
    print("弹窗里是否出现『餐饮 / 餐厅』:", "餐饮 / 餐厅" in body or "餐厅" in body)
