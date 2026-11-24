import os
import sys

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    pg = None
    for page in ctx.pages:
        if "egoops.meituan.com" in page.url:
            pg = page
            break
    if pg is None:
        print("no egoops page")
        sys.exit(0)
    print("URL:", pg.url)
    toasts = []
    try:
        toasts = pg.locator("[data-sonner-toast]").all_inner_texts()
    except Exception:
        pass
    print("toast:", [t.strip() for t in toasts if t.strip()][:5])
    body = pg.inner_text("body")
    print("弹窗还在:", "申请采集点" in body and "保存草稿" in body)
    idx = body.find("申请采集点")
    print("片段:", body[idx:idx + 120].replace("\n", " | ") if idx >= 0 else "")
