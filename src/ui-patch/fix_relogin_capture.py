"""登录抓取修正：
   · 只有拿到有效 token 才覆盖保存（避免把好数据冲掉）
   · 等 login 页面真正结束 + sessionStorage 里出现 oidc.user 才算成功
"""

import io

p = 'viewer/egoops_auth.py'
s = io.open(p, encoding='utf-8').read()

old = '''        log("请在弹出的浏览器窗口里登录 EgoOps（手机验证码），最多等 %d 秒…" % wait_seconds)
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if "egoops.meituan.com" in page.url and "login" not in page.url:
                break
            time.sleep(3)
        if "login" in page.url:
            return False, "没有完成登录"

        page.wait_for_timeout(4000)
        storage = page.evaluate("""() => {
            const dump = s => { const o = {}; for (let i = 0; i < s.length; i++) { const k = s.key(i); o[k] = s.getItem(k); } return o; };
            return { local: dump(localStorage), session: dump(sessionStorage) };
        }""")'''

new = '''        log("请在弹出的浏览器窗口里登录 EgoOps（手机验证码），最多等 %d 秒…" % wait_seconds)
        deadline = time.time() + wait_seconds
        storage = {"local": {}, "session": {}}
        while time.time() < deadline:
            try:
                for pg in ctx.pages:
                    if "egoops.meituan.com" not in pg.url:
                        continue
                    st = pg.evaluate("""() => {
                        const dump = s => { const o = {}; for (let i = 0; i < s.length; i++) { const k = s.key(i); o[k] = s.getItem(k); } return o; };
                        return { local: dump(localStorage), session: dump(sessionStorage) };
                    }""")
                    has_token = any("oidc.user" in k for k in (st.get("session") or {})) or \\
                                any("oidc.user" in k for k in (st.get("local") or {}))
                    if has_token:
                        storage = st
                        page = pg
                        break
                else:
                    time.sleep(3)
                    continue
                break
            except Exception:
                time.sleep(3)
        else:
            return False, "等待超时，没拿到登录态（登录窗口还开着，可以再点一次登录）"

        if not storage.get("session") and not storage.get("local"):
            return False, "没拿到登录态"

        page.wait_for_timeout(1500)'''

assert old in s
s = s.replace(old, new)

# 保存前先校验；无效就不覆盖
old2 = '''        os.makedirs(os.path.dirname(AUTH), exist_ok=True)
        with open(AUTH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        ok, who = alive(token_of(data))
        return (True, "已保存登录态（%s）" % who) if ok else (False, "抓到了但校验失败")'''
new2 = '''        ok, who = alive(token_of(data))
        if not ok:
            return False, "抓到的登录态校验失败（%s），没有覆盖原文件" % who

        os.makedirs(os.path.dirname(AUTH), exist_ok=True)
        with open(AUTH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        return True, "已保存登录态（%s）" % who'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('登录抓取逻辑已修')
