"""完整演示：申请采集点 → 填表（含场景/地址/媒体）→ 保存草稿。只动弹窗内元素。"""
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


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def shot(pg, name):
    try:
        pg.screenshot(path=os.path.join(OUT, name))
        log("截图", name)
    except Exception as e:
        log("截图失败", e)


def role_buttons(pg, maxlen=8):
    try:
        texts = [t.strip() for t in pg.get_by_role("button").all_inner_texts()]
    except Exception:
        return []
    return [t for t in texts if t and len(t) <= maxlen]


def click_role(pg, name, timeout=6000):
    loc = pg.get_by_role("button", name=name, exact=True)
    if loc.count():
        loc.first.click(timeout=timeout)
        return True
    return False


def main():
    site = json.load(open(sys.argv[1], encoding="utf-8"))
    photo, video = sys.argv[2], sys.argv[3]
    desc, _ = generate_description(site)
    tk = (site.get("tasks") or [{}])[0]
    content, _ = generate_task_content(site, tk)

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        ctx = b.contexts[0]
        pg = next(x for x in ctx.pages if "egoops.meituan.com" in x.url)

        if "任务名称" not in pg.inner_text("body"):
            pg.get_by_text("申请采集点", exact=True).first.click()
            pg.wait_for_timeout(4500)
        log("弹窗就绪")

        pg.get_by_label("采集点名称").first.fill(site.get("name") or "")
        pg.get_by_label("采集点描述").first.fill(desc)
        log("✓ 名称/描述")
        shot(pg, "s-1-site.png")

        # 场景
        pg.get_by_text("请选择一级和二级分类", exact=False).first.click()
        pg.wait_for_timeout(1200)
        log("一级候选:", role_buttons(pg, 6)[:20])
        if click_role(pg, "餐饮"):
            log("✓ 一级 餐饮")
            pg.wait_for_timeout(1200)
            log("二级候选:", role_buttons(pg, 8)[:25])
            if click_role(pg, "餐厅"):
                log("✓ 二级 餐厅")
        pg.wait_for_timeout(800)
        shot(pg, "s-2-scene.png")

        # 地址
        parts = parse_addr("广东省湛江市赤坎区人民大道88号")
        pg.get_by_text("请选择省、市、区（县）", exact=False).first.click()
        pg.wait_for_timeout(1000)
        for nm in (parts["province"], parts["city"], parts["district"]):
            ok = click_role(pg, nm)
            log(("✓ " if ok else "✗ ") + "地址 " + nm)
            pg.wait_for_timeout(800)
        try:
            pg.get_by_placeholder("街道、门牌号、园区或楼栋").first.fill(parts["street"])
            log("✓ 街道", parts["street"])
        except Exception as e:
            log("街道失败", e)
        shot(pg, "s-3-addr.png")

        # 任务
        pg.get_by_label("任务名称").first.fill(tk.get("name") or "")
        pg.get_by_label("任务描述").first.fill(content["desc"])
        pg.get_by_label("预计时长").first.fill(str(content["hours"]))
        for i, step in enumerate(content["sop"]):
            boxes = pg.get_by_placeholder("请输入操作步骤")
            if i == 0:
                boxes.first.fill(step)
            else:
                click_role(pg, "添加步骤")
                pg.wait_for_timeout(400)
                pg.get_by_placeholder("请输入操作步骤").nth(i).fill(step)
        log("✓ 任务字段 + SOP", len(content["sop"]))
        shot(pg, "s-4-task.png")

        # 媒体：任务照片 / 任务视频 下的第一个加号
        def upload(label_text, path):
            try:
                box = pg.get_by_text(label_text, exact=False).first
                btn = box.locator("xpath=ancestor::*[self::div][1]//following::div[@role='button'][1]")
                with pg.expect_file_chooser(timeout=6000) as fc:
                    btn.first.click()
                fc.value.set_files(path)
                pg.wait_for_timeout(7000)
                log("✓ 上传", os.path.basename(path))
                return True
            except Exception as e:
                log("上传失败", label_text, e)
                return False

        upload("任务照片", photo)
        shot(pg, "s-5-photo.png")
        upload("任务视频", video)
        shot(pg, "s-6-video.png")

        # 保存草稿
        if click_role(pg, "保存草稿"):
            log("已点【保存草稿】")
        else:
            log("找不到保存草稿按钮")
        pg.wait_for_timeout(6000)
        shot(pg, "s-7-saved.png")
        try:
            toasts = [t.strip() for t in pg.locator("[data-sonner-toast]").all_inner_texts() if t.strip()]
            log("提示:", toasts[:3])
        except Exception:
            pass
        log("弹窗仍在:", "任务名称" in pg.inner_text("body"))


if __name__ == "__main__":
    main()
