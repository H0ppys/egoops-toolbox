"""探测场景下拉的两级结构（只点下拉，不保存）。"""
import time

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)

    if "任务名称" not in pg.inner_text("body"):
        pg.get_by_text("申请采集点", exact=True).first.click()
        pg.wait_for_timeout(4500)
    log("弹窗:", "任务名称" in pg.inner_text("body"))

    trig = pg.get_by_text("请选择一级和二级分类", exact=False)
    log("触发器数量:", trig.count())
    if trig.count():
        trig.first.click()
        pg.wait_for_timeout(1200)
        texts = [t.strip() for t in pg.locator("button").all_inner_texts() if t.strip()]
        log("一级候选:", [t for t in texts if len(t) <= 6][:25])

        l1 = pg.get_by_role("button", name="餐饮", exact=True)
        log("餐饮按钮:", l1.count())
        if l1.count():
            l1.first.click()
            pg.wait_for_timeout(1500)
            texts2 = [t.strip() for t in pg.locator("button").all_inner_texts() if t.strip()]
            log("二级候选:", [t for t in texts2 if len(t) <= 8][:30])
            pg.screenshot(path="docs/scene-probe.png")

    log("弹窗仍在:", "任务名称" in pg.inner_text("body"))
