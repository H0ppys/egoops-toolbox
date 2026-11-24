"""用保存的登录态打开 EgoOps，定位到指定草稿并截图（只读，不提交）。"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))
TARGET = sys.argv[1] if len(sys.argv) > 1 else ""


def main():
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
        ctx = b.new_context(viewport={"width": 1600, "height": 950})
        ctx.add_cookies(data.get("cookies") or [])
        ctx.add_init_script(script)
        pg = ctx.new_page()
        pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(9000)
        print("URL:", pg.url)
        if "login" in pg.url:
            print("登录态失效")
            return
        # 申报 tab
        pg.get_by_text("申报", exact=False).first.click()
        pg.wait_for_timeout(2500)
        # 搜索
        try:
            box = pg.get_by_placeholder("搜索采集点 / 任务包名称或任务名称").first
            box.fill("美宜佳")
            pg.wait_for_timeout(3000)
        except Exception as e:
            print("搜索失败", e)
        pg.screenshot(path=os.path.join(OUT, "demo-list.png"))
        body = pg.inner_text("body")
        print("列表含目标 id:", TARGET in body, "| 含美宜佳:", "美宜佳" in body)

        # 打开第一条详情
        try:
            pg.get_by_role("button", name="详情").first.click(timeout=8000)
            pg.wait_for_timeout(3500)
            pg.screenshot(path=os.path.join(OUT, "demo-detail.png"))
            print("已打开详情")
        except Exception as e:
            print("打开详情失败", e)
        b.close()


if __name__ == "__main__":
    main()
