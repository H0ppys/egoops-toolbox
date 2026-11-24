"""带调试端口启动 Edge，等用户登录后，自动填「申请采集点」并点【保存草稿】。

思路：EgoOps 的登录态在 sessionStorage（关浏览器就丢），所以必须接管**同一个**浏览器窗口，
     不能另开新实例。做法是 Edge 启动时加 --remote-debugging-port，脚本用 CDP 接上去。
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))
CDP = "http://127.0.0.1:9222"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def shot(pg, name):
    try:
        pg.screenshot(path=os.path.join(OUT, name), full_page=False)
        log("截图:", name)
    except Exception as e:
        log("截图失败", e)


def launch_edge():
    subprocess.Popen([EDGE, f"--remote-debugging-port=9222", f"--user-data-dir={PROFILE}",
                      "--start-maximized", "https://egoops.meituan.com/assignment"])
    for _ in range(40):
        try:
            urllib.request.urlopen(CDP + "/json/version", timeout=2).read()
            log("调试端口就绪")
            return True
        except Exception:
            time.sleep(1)
    return False


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
    site = json.load(open(sys.argv[1], encoding="utf-8"))
    desc, _ = generate_description(site)
    tasks = []
    for t in site.get("tasks") or []:
        c, _ = generate_task_content(site, t)
        tasks.append({"area": t.get("area") or "", "name": t.get("name") or "", **c})

    if not launch_edge():
        log("Edge 调试端口没起来")
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        pg = None
        for page in ctx.pages:
            if "meituan" in page.url:
                pg = page
                break
        if pg is None:
            pg = ctx.new_page()
            pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded")

        log("当前页面:", pg.url)
        log("等待登录（请在窗口里用手机验证码登录，最多 6 分钟）…")
        deadline = time.time() + 360
        while time.time() < deadline:
            if "login" not in pg.url:
                break
            time.sleep(3)
        if "login" in pg.url:
            log("仍未登录，退出")
            return
        pg.wait_for_timeout(8000)
        log("已登录:", pg.url)
        shot(pg, "live-0-home.png")

        pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
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

        pg.wait_for_timeout(800)
        shot(pg, "live-2-filled.png")

        try:
            pg.get_by_role("button", name="保存草稿").first.click(timeout=8000)
            log("已点击【保存草稿】")
        except Exception as e:
            log("点保存草稿失败:", e)
        pg.wait_for_timeout(5000)
        shot(pg, "live-3-saved.png")
        log("完成，窗口留给你检查")


if __name__ == "__main__":
    main()
