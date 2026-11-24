"""打开指定草稿的任务详情，截图看 SOP 是不是一行一条。"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")
OUT = os.path.abspath("docs/egoops-sop-rows.png")
TARGET = sys.argv[1] if len(sys.argv) > 1 else "方法"

data = json.load(open(AUTH, encoding="utf-8"))
storage = data.get("storage") or {}
seed = {"local": storage.get("local") or {}, "session": storage.get("session") or {}}
script = """
(() => { const seed = %s;
  try { for (const [k,v] of Object.entries(seed.local||{})) localStorage.setItem(k,v);
        for (const [k,v] of Object.entries(seed.session||{})) sessionStorage.setItem(k,v); } catch(e) {}
})();""" % json.dumps(seed, ensure_ascii=False)

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": 1500, "height": 1000})
    ctx.add_cookies(data.get("cookies") or [])
    ctx.add_init_script(script)
    pg = ctx.new_page()
    pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    pg.get_by_text("申报", exact=False).first.click()
    pg.wait_for_timeout(1800)
    pg.get_by_text("草稿", exact=True).first.click()
    pg.wait_for_timeout(2500)
    box = pg.get_by_placeholder("搜索采集点 / 任务包名称或任务名称").first
    box.fill(TARGET)
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_role("button", name="编辑").first.click(timeout=8000)
        pg.wait_for_timeout(4000)
        pg.screenshot(path=OUT)
        print("已截图(编辑态):", OUT)
        body = pg.inner_text("body")
        print("含任务名:", "核验工位展示机运行状态" in body)
    except Exception as e:
        print("打开编辑失败:", e)
        pg.screenshot(path=OUT)
    b.close()
