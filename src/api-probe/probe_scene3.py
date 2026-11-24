"""探测：场景弹层结构 + 文件 input。"""
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

    log("file inputs:", pg.evaluate("""() => [...document.querySelectorAll('input[type=file]')].map(e => ({
        accept: e.accept, multiple: e.multiple, hidden: e.offsetParent === null }))"""))

    pg.get_by_text("请选择一级和二级分类", exact=False).first.click()
    pg.wait_for_timeout(1500)
    log("role=option:", pg.evaluate("""() => [...document.querySelectorAll('[role="option"],[role="menuitem"],[data-radix-collection-item]')]
        .map(e => (e.innerText || '').trim().slice(0, 12)).filter(Boolean).slice(0, 30)"""))
    log("弹出层里的 div:", pg.evaluate("""() => {
        const cands = [...document.querySelectorAll('div')].filter(d => {
            const t = (d.innerText || '').trim();
            const r = d.getBoundingClientRect();
            return r.height > 200 && r.width > 150 && r.width < 400 && t.length > 4 && t.length < 200;
        }).slice(0, 5).map(d => ({ text: (d.innerText || '').slice(0, 60), role: d.getAttribute('role') || '' }));
        return cands;
    }"""))
    pg.screenshot(path="docs/scene-panel.png")
    log("截图 scene-panel.png")
