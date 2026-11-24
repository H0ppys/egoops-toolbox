"""按索引填表（EgoOps 弹窗里的 input/textarea 顺序固定），再保存草稿。"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

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


def dump_fields(pg):
    return pg.evaluate("""() => {
        const dlg = document.querySelector('[role="dialog"]') || document.body;
        const els = [...dlg.querySelectorAll('input,textarea')].filter(e => {
            const r = e.getBoundingClientRect(); return r.width > 0;
        });
        return els.map((e, i) => ({ i, tag: e.tagName.toLowerCase(), type: e.type,
            ph: e.placeholder || '', val: (e.value || '').slice(0, 20) }));
    }""")


def set_val(pg, idx, value):
    """按索引设置值，并触发 React 的 onChange"""
    ok = pg.evaluate("""([idx, value]) => {
        const dlg = document.querySelector('[role="dialog"]') || document.body;
        const els = [...dlg.querySelectorAll('input,textarea')].filter(e => {
            const r = e.getBoundingClientRect(); return r.width > 0;
        });
        const el = els[idx];
        if (!el) return false;
        const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(el, value);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }""", [idx, value])
    return ok


def main():
    site = json.load(open(sys.argv[1], encoding="utf-8"))
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

        log("字段布局:", json.dumps(dump_fields(pg), ensure_ascii=False))

        # 0 名称 / 1 街道 / 2 任务名称 / 3 预计时长 ...
        set_val(pg, 0, site.get("name") or "")
        set_val(pg, 1, "人民大道88号")
        texts = [i for i, f in enumerate(dump_fields(pg)) if f["tag"] == "textarea"]
        log("textarea 索引:", texts)
        if texts:
            set_val(pg, texts[0], desc)          # 采集点描述
        if len(texts) > 1:
            set_val(pg, texts[1], content["desc"])  # 任务描述
        log("✓ 名称/街道/描述")

        # 时长：找 type=number 或 label 附近的 input
        fields = dump_fields(pg)
        num_idx = None
        for f in fields:
            if f["type"] == "number":
                num_idx = f["i"]
                break
        if num_idx is None:
            cands = [f["i"] for f in fields if f["tag"] == "input" and f["ph"] == "" and f["i"] > 1]
            num_idx = cands[0] if cands else None
        if num_idx is not None:
            set_val(pg, num_idx, str(content["hours"]))
            log("✓ 时长 @", num_idx, content["hours"])

        shot(pg, "i-1-filled.png")
        log("填完，字段值:", json.dumps(dump_fields(pg), ensure_ascii=False))

        # 保存草稿
        btn = pg.get_by_role("button", name="保存草稿")
        if btn.count():
            btn.first.click()
            log("已点保存草稿")
        pg.wait_for_timeout(5000)
        shot(pg, "i-2-saved.png")
        toasts = [t.strip() for t in pg.locator("[data-sonner-toast]").all_inner_texts() if t.strip()]
        log("提示:", toasts[:3])
        log("弹窗仍在:", "任务名称" in pg.inner_text("body"))


if __name__ == "__main__":
    main()
