"""在 EgoOps 上完整走一次「申请采集点 → 保存草稿」，只动弹窗内元素。"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402
from address_parse import parse as parse_addr  # noqa: E402

CDP = "http://127.0.0.1:9222"
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))
MEDIA = os.path.join(OUT, "media")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def shot(pg, name):
    try:
        pg.screenshot(path=os.path.join(OUT, name))
        log("截图", name)
    except Exception as e:
        log("截图失败", e)


def main():
    site = json.load(open(sys.argv[1], encoding="utf-8"))
    photo = sys.argv[2]
    video = sys.argv[3]
    desc, _ = generate_description(site)
    tk = site["tasks"][1] if len(site.get("tasks") or []) > 1 else site["tasks"][0]
    content, _ = generate_task_content(site, tk)

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        ctx = b.contexts[0]
        pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)
        log("页面:", pg.url)

        def ensure_dialog():
            if "任务名称" in pg.inner_text("body"):
                return True
            pg.get_by_text("申请采集点", exact=True).first.click(timeout=10000)
            pg.wait_for_timeout(3500)
            return "任务名称" in pg.inner_text("body")

        ensure_dialog()
        dlg = pg.get_by_role("dialog")
        log("弹窗已就绪")
        shot(pg, "d-0-open.png")

        # 采集点名称 / 描述
        dlg.get_by_label("采集点名称").first.fill(site.get("name") or "")
        dlg.get_by_label("采集点描述").first.fill(desc)
        log("✓ 名称/描述")

        # 采集场景分类（下拉弹层在 dialog 之外的 portal 里，必须用 page 级定位）
        pg.get_by_text("请选择一级和二级分类", exact=False).first.click()
        pg.wait_for_timeout(1000)
        pg.get_by_role("button", name="餐饮", exact=True).first.click()
        pg.wait_for_timeout(900)
        pg.get_by_role("button", name="餐厅", exact=True).first.click()
        pg.wait_for_timeout(700)
        log("✓ 场景 餐饮/餐厅")

        # 现场地址
        parts = parse_addr("广东省湛江市赤坎区人民大道88号")
        pg.get_by_text("请选择省、市、区（县）", exact=False).first.click()
        pg.wait_for_timeout(1000)
        for nm in (parts["province"], parts["city"], parts["district"]):
            pg.get_by_role("button", name=nm, exact=True).first.click()
            pg.wait_for_timeout(800)
        dlg.get_by_placeholder("街道、门牌号、园区或楼栋").first.fill(parts["street"])
        log("✓ 地址", parts["province"], parts["city"], parts["district"], parts["street"])
        shot(pg, "d-1-site.png")

        # 任务 1（第一个任务卡片就是默认那个）
        dlg.get_by_label("任务名称").first.fill(tk.get("name") or "")
        dlg.get_by_label("任务描述").first.fill(content["desc"])
        dlg.get_by_label("预计时长").first.fill(str(content["hours"]))
        for i, step in enumerate(content["sop"]):
            boxes = dlg.get_by_placeholder("请输入操作步骤")
            if i == 0:
                boxes.first.fill(step)
            else:
                dlg.get_by_text("添加步骤", exact=False).first.click()
                pg.wait_for_timeout(400)
                dlg.get_by_placeholder("请输入操作步骤").nth(i).fill(step)
        log("✓ 任务字段 + SOP", len(content["sop"]))

        # 任务照片：点第一个加号，塞文件
        try:
            with pg.expect_file_chooser(timeout=8000) as fc:
                dlg.locator("text=任务照片").locator("xpath=following::button[1]").first.click()
            fc.value.set_files(photo)
            pg.wait_for_timeout(6000)
            log("✓ 任务照片已选", os.path.basename(photo))
        except Exception as e:
            log("照片选择失败:", e)
        shot(pg, "d-2-photo.png")

        # 任务视频
        try:
            with pg.expect_file_chooser(timeout=8000) as fc:
                dlg.locator("text=任务视频").locator("xpath=following::button[1]").first.click()
            fc.value.set_files(video)
            pg.wait_for_timeout(8000)
            log("✓ 任务视频已选", os.path.basename(video))
        except Exception as e:
            log("视频选择失败:", e)
        shot(pg, "d-3-video.png")

        # 保存草稿
        dlg.get_by_role("button", name="保存草稿").first.click()
        log("已点【保存草稿】")
        pg.wait_for_timeout(6000)
        shot(pg, "d-4-after-save.png")
        try:
            toasts = pg.locator("[data-sonner-toast]").all_inner_texts()
            log("提示:", [t.strip() for t in toasts if t.strip()][:3])
        except Exception:
            pass
        body = pg.inner_text("body")
        log("弹窗还开着:", "任务名称" in body)


if __name__ == "__main__":
    main()
