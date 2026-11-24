"""最终演示：按索引填表 + 搜索选场景 + 直接塞文件 + 保存草稿。"""
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
    except Exception:
        pass


def set_field(pg, idx, value):
    return pg.evaluate("""([idx, value]) => {
        const dlg = document.querySelector('[role="dialog"]') || document.body;
        const els = [...dlg.querySelectorAll('input,textarea')].filter(e => e.getBoundingClientRect().width > 0);
        const el = els[idx]; if (!el) return false;
        const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }""", [idx, value])


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

        # 1) 文本字段（顺序固定：0名称 1街道 2采集点描述 3任务名称 4任务描述 5时长 6..SOP）
        set_field(pg, 0, site.get("name") or "")
        set_field(pg, 1, "人民大道88号")
        set_field(pg, 2, desc)
        set_field(pg, 3, tk.get("name") or "")
        set_field(pg, 4, content["desc"])
        set_field(pg, 5, str(content["hours"]))
        for i, step in enumerate(content["sop"]):
            set_field(pg, 6 + i, step)
        log("✓ 文本字段（名称/街道/描述/任务名/任务描述/时长/SOP）")

        # 2) 场景：用弹层里的搜索框
        pg.get_by_text("请选择一级和二级分类", exact=False).first.click()
        pg.wait_for_timeout(1200)
        try:
            search = pg.get_by_placeholder("搜索采集场景分类").first
            search.fill("餐厅")
            pg.wait_for_timeout(1200)
            cand = pg.get_by_text("餐厅", exact=True)
            log("搜索结果数:", cand.count())
            cand.first.click()
            pg.wait_for_timeout(800)
            log("✓ 场景 餐厅")
        except Exception as e:
            log("场景失败:", e)
        shot(pg, "f-1-scene.png")

        # 3) 地址
        parts = parse_addr("广东省湛江市赤坎区人民大道88号")
        pg.get_by_text("请选择省、市、区（县）", exact=False).first.click()
        pg.wait_for_timeout(1000)
        for nm in (parts["province"], parts["city"], parts["district"]):
            loc = pg.get_by_role("button", name=nm, exact=True)
            if loc.count():
                loc.first.click()
                pg.wait_for_timeout(700)
                log("✓ 地址", nm)
        shot(pg, "f-2-addr.png")

        # 4) 媒体：直接塞隐藏的 file input
        try:
            pg.locator("input[type=file][accept*='image']").first.set_input_files(photo)
            log("✓ 照片已塞入")
            pg.wait_for_timeout(8000)
        except Exception as e:
            log("照片失败:", e)
        try:
            pg.locator("input[type=file][accept*='video']").first.set_input_files(video)
            log("✓ 视频已塞入")
            pg.wait_for_timeout(10000)
        except Exception as e:
            log("视频失败:", e)
        shot(pg, "f-3-media.png")

        # 5) 保存草稿
        btn = pg.get_by_role("button", name="保存草稿")
        if btn.count():
            btn.first.click()
            log("已点【保存草稿】")
        pg.wait_for_timeout(6000)
        shot(pg, "f-4-saved.png")
        toasts = [t.strip() for t in pg.locator("[data-sonner-toast]").all_inner_texts() if t.strip()]
        log("提示:", toasts[:3])
        log("弹窗仍在:", "任务名称" in pg.inner_text("body"))


if __name__ == "__main__":
    main()
