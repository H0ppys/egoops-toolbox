"""接上已开的 Edge（CDP 9222）：抓登录态存盘 → 填申请采集点 → 保存草稿。"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

CDP = "http://127.0.0.1:9222"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))
AUTH = os.path.join(OUT, "egoops_auth.json")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def shot(pg, name):
    try:
        pg.screenshot(path=os.path.join(OUT, name))
        log("截图:", name)
    except Exception as e:
        log("截图失败", e)


def app_page(ctx):
    for page in ctx.pages:
        if "egoops.meituan.com" in page.url:
            return page
    return None


def capture(ctx, pg):
    cookies = ctx.cookies()
    storage = pg.evaluate("""() => {
        const dump = s => { const o = {}; for (let i = 0; i < s.length; i++) { const k = s.key(i); o[k] = s.getItem(k); } return o; };
        return { local: dump(localStorage), session: dump(sessionStorage) };
    }""")
    data = {"url": pg.url, "cookies": cookies, "storage": storage, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(AUTH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    toks = []
    for scope in ("local", "session"):
        for k, v in (storage.get(scope) or {}).items():
            if not v:
                continue
            if v.startswith("eyJ") and v.count(".") == 2:
                toks.append("%s/%s (JWT)" % (scope, k))
            elif '"access_token"' in v:
                toks.append("%s/%s (含 access_token)" % (scope, k))
    log("cookie %d 条，storage 键 %d 个" %
        (len(cookies), len(storage.get("local") or {}) + len(storage.get("session") or {})))
    log("token 位置:", toks or "（没找到，可能只靠 cookie）")
    log("已保存:", AUTH)
    return data


def fill_label(pg, labels, value, tag):
    for lb in labels:
        try:
            box = pg.get_by_label(lb, exact=False)
            if box.count():
                box.first.fill(str(value))
                log("✓ %s = %r" % (tag, str(value)[:40]))
                return True
        except Exception:
            pass
    log("✗ 没找到 %s" % tag)
    return False


def main():
    site = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "tmp_site.json", encoding="utf-8"))
    desc, _ = generate_description(site)
    tasks = []
    for t in site.get("tasks") or []:
        c, _ = generate_task_content(site, t)
        tasks.append({"area": t.get("area") or "", "name": t.get("name") or "", **c})

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        pg = app_page(ctx)
        if pg is None:
            log("没找到 egoops 页面，打开一个")
            pg = ctx.new_page()
            pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded")
            pg.wait_for_timeout(8000)
        log("页面:", pg.url)
        if "login" in pg.url:
            log("还是登录页，请先登录")
            return

        data = capture(ctx, pg)
        shot(pg, "live-0-home.png")

        try:
            pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
            log("已点开申请采集点")
        except Exception as e:
            log("点申请采集点失败:", e)
        pg.wait_for_timeout(4000)
        shot(pg, "live-1-open.png")

        fill_label(pg, ["采集点名称"], site.get("name") or "", "采集点名称")
        fill_label(pg, ["采集点描述"], desc, "采集点描述")

        tk = tasks[0]
        fill_label(pg, ["任务名称"], tk["name"], "任务名称")
        fill_label(pg, ["任务描述"], tk["desc"], "任务描述")
        fill_label(pg, ["预计时长"], str(tk["hours"]), "预计时长")

        for i, step in enumerate(tk["sop"]):
            try:
                boxes = pg.get_by_placeholder("请输入操作步骤")
                if i == 0:
                    boxes.first.fill(step)
                else:
                    pg.get_by_text("添加步骤", exact=False).first.click(timeout=4000)
                    pg.wait_for_timeout(400)
                    pg.get_by_placeholder("请输入操作步骤").nth(i).fill(step)
                log("✓ SOP %d" % (i + 1))
            except Exception as e:
                log("SOP %d 失败: %s" % (i + 1, e))
                break

        pg.wait_for_timeout(1000)
        shot(pg, "live-2-filled.png")

        try:
            pg.get_by_role("button", name="保存草稿").first.click(timeout=8000)
            log("已点击【保存草稿】")
        except Exception as e:
            log("点保存草稿失败:", e)
        pg.wait_for_timeout(5000)
        shot(pg, "live-3-saved.png")
        log("完成")


if __name__ == "__main__":
    main()
