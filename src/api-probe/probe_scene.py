"""看看「采集场景分类」下拉展开后是什么结构。"""
import os
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)
    print("URL:", pg.url)

    # 确保弹窗打开
    if "申请采集点" not in pg.inner_text("body"):
        pg.get_by_text("申请采集点", exact=True).first.click()
        pg.wait_for_timeout(3000)

    combo = pg.get_by_text("请选择一级和二级分类", exact=False).first
    combo.click()
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(OUT, "scene-0-open.png"))
    print("已点开场景下拉")

    html = pg.evaluate("""() => {
        const els = [...document.querySelectorAll('[role="option"],[role="listbox"] li,[data-radix-collection-item],div[class*="popover"] button,div[class*="dropdown"] button')];
        return els.slice(0, 40).map(e => ({tag: e.tagName.toLowerCase(), text: (e.innerText||'').trim().slice(0,20), role: e.getAttribute('role')||''}));
    }""")
    print("候选项:", html)
