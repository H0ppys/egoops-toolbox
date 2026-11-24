"""真机操作：用本机 Edge 配置打开 EgoOps，填「申请采集点」并点【保存草稿】（不提交审核）。

前置：Edge 必须先关闭。
"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

EDGE_DEFAULT = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data", "Default")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def shot(pg, name):
    try:
        pg.screenshot(path=os.path.join(OUT, name))
        log("截图:", name)
    except Exception:
        pass


def fill_label(pg, labels, value, tag):
    for lb in labels:
        try:
            box = pg.get_by_label(lb, exact=False)
            if box.count():
                box.first.fill(str(value))
                log("✓ %s = %r" % (tag, value))
                return True
        except Exception:
            pass
    log("✗ 没找到 %s" % tag)
    return False


def main():
    site = json.load(open(sys.argv[1], encoding="utf-8"))

    desc, dsrc = generate_description(site)
    log("采集点描述来源:", dsrc)
    tasks = []
    for t in site.get("tasks") or []:
        c, src = generate_task_content(site, t)
        tasks.append({"area": t.get("area") or "", "name": t.get("name") or "", **c, "src": src})
    log("任务数:", len(tasks))

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=EDGE_DEFAULT, channel="msedge", headless=False, no_viewport=True,
            args=["--start-maximized"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        log("URL:", pg.url)
        if "login" in pg.url:
            log("未登录，等待手动登录（最多 5 分钟）")
            pg.wait_for_url(lambda u: "login" not in u, timeout=300000)
            pg.wait_for_timeout(8000)

        pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
        pg.wait_for_timeout(4000)
        log("已打开弹窗")
        shot(pg, "live-0-open.png")

        fill_label(pg, ["采集点名称"], site.get("name") or "", "采集点名称")
        fill_label(pg, ["采集点描述"], desc, "采集点描述")
        pg.wait_for_timeout(600)

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
                log("✓ SOP %d = %s" % (i + 1, step))
            except Exception as e:
                log("SOP %d 失败: %s" % (i + 1, e))
                break

        pg.wait_for_timeout(800)
        shot(pg, "live-1-filled.png")

        # 保存草稿（不提交审核）
        try:
            pg.get_by_role("button", name="保存草稿").first.click(timeout=8000)
            log("已点击【保存草稿】")
        except Exception:
            try:
                pg.get_by_text("保存草稿", exact=True).first.click(timeout=8000)
                log("已点击【保存草稿】(by text)")
            except Exception as e:
                log("点保存草稿失败:", e)
        pg.wait_for_timeout(4000)
        shot(pg, "live-2-saved.png")

        try:
            toast = pg.locator("[data-sonner-toast], .toast, [role='status']").all_inner_texts()
            if toast:
                log("提示：", " | ".join(t.strip() for t in toast if t.strip())[:300])
        except Exception:
            pass

        body = pg.inner_text("body")
        log("弹窗是否还在:", "申请采集点" in body)
        log("窗口保持 120 秒，你可以看结果")
        pg.wait_for_timeout(120000)
        ctx.close()


if __name__ == "__main__":
    main()
