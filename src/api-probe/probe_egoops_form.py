"""复制 Edge 配置 → 打开 EgoOps → 检查登录态并 dump 申请采集点弹窗结构（不提交）。"""
import os
import shutil
import sys

from playwright.sync_api import sync_playwright

EDGE = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data")
SRC = os.path.join(EDGE, "Default")
DST = os.path.join(os.environ["TEMP"], "edge-egoops-copy")


def copy_profile():
    if os.path.isdir(DST):
        shutil.rmtree(DST, ignore_errors=True)
    os.makedirs(DST, exist_ok=True)
    ls = os.path.join(EDGE, "Local State")
    if os.path.exists(ls):
        shutil.copy2(ls, os.path.join(DST, "Local State"))
    for rel in ["Preferences", "Secure Preferences", "Network", "Local Storage",
                "Session Storage", "IndexedDB"]:
        s = os.path.join(SRC, rel)
        d = os.path.join(DST, rel)
        if not os.path.exists(s):
            continue
        try:
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
        except Exception as e:
            print("skip", rel, e)
    total = 0
    for root, _, files in os.walk(DST):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    print("profile copy: %.1f MB" % (total / 1048576))


def main():
    copy_profile()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=DST, channel="msedge", headless=False, no_viewport=True,
            args=["--start-maximized"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.goto("https://egoops.meituan.com/assignment", wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        print("URL:", pg.url)
        print("标题:", pg.title())
        print("片段:", pg.inner_text("body")[:200].replace("\n", " | "))
        if "login" in pg.url:
            print("RESULT=NOT_LOGGED_IN")
            pg.wait_for_timeout(3000)
            ctx.close()
            return
        print("RESULT=LOGGED_IN")
        try:
            pg.get_by_text("申请采集点", exact=True).first.click(timeout=8000)
            pg.wait_for_timeout(4500)
            print("clicked 申请采集点")
        except Exception as e:
            print("click failed:", e)
        info = pg.evaluate("""() => {
            const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
            return [...document.querySelectorAll('input,textarea,select,button,[role="combobox"]')].filter(vis)
              .map((el, i) => ({
                i, tag: el.tagName.toLowerCase(), type: el.type || '',
                ph: el.placeholder || '',
                label: (el.closest('label')?.innerText || '').trim().slice(0, 40),
                text: (el.innerText || '').trim().slice(0, 30),
              }));
        }""")
        print("控件数:", len(info))
        for x in info:
            print("  [%s] %s type=%s ph=%r label=%r text=%r"
                  % (x["i"], x["tag"], x["type"], x["ph"], x["label"], x["text"]))
        pg.wait_for_timeout(2000)
        ctx.close()


if __name__ == "__main__":
    main()
