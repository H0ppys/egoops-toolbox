import os
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)
    print("URL:", pg.url)
    body = pg.inner_text("body")
    print("弹窗在:", "任务名称" in body)
    print("片段:", body[:160].replace("\n", " | "))
    pg.screenshot(path=os.path.join(OUT, "state-now.png"))
    print("截图 state-now.png")
