"""用存下来的登录态直接开浏览器，验证是否免登录。"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

AUTH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "egoops_auth.json")
AUTH = os.path.abspath(AUTH)


def main():
    data = json.load(open(AUTH, encoding="utf-8"))
    storage = data.get("storage") or {}
    seed = {
        "local": storage.get("local") or {},
        "session": storage.get("session") or {},
    }
    script = """
    (() => {
      const seed = %s;
      try {
        for (const [k, v] of Object.entries(seed.local || {})) localStorage.setItem(k, v);
        for (const [k, v] of Object.entries(seed.session || {})) sessionStorage.setItem(k, v);
      } catch (e) {}
    })();
    """ % json.dumps(seed, ensure_ascii=False)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context()
        try:
            ctx.add_cookies(data.get("cookies") or [])
        except Exception as e:
            print("cookie 注入失败:", e)
        ctx.add_init_script(script)
        pg = ctx.new_page()
        pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(9000)
        print("URL:", pg.url)
        body = pg.inner_text("body")[:300].replace("\n", " | ")
        print("片段:", body)
        print("RESULT:", "免登录 OK" if "login" not in pg.url else "仍需登录")
        browser.close()


if __name__ == "__main__":
    main()
