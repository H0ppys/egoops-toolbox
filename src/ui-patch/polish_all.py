"""整体收尾打磨：
   1) 版本号进标题与状态栏（v16）
   2) 删除采集点：逐个进度 + 最终汇总 + 一定刷新
   3) 长任务结束时一定清掉「正在…」文字（异常也清）
"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

VER = 'v16'
s = re.sub(r'APP_VER = "[^"]*"', 'APP_VER = "%s"' % VER, s, count=1)

# 1) 统一的删除采集点（带进度）
if 'def _delete_sites(self, sites):' in s:
    start = s.index('    def _delete_sites(self, sites):')
    nxt = re.search(r'^    def ', s[start + 10:], re.M)
    end = start + 10 + nxt.start() if nxt else len(s)
    new = '''    def _delete_sites(self, sites):
        total = len(sites)
        self.lbl_task.config(text="正在删除 0/%d…" % total)

        def work():
            ok = fail = 0
            errs = []
            for i, site in enumerate(sites, 1):
                self.ui(self.lbl_task.config, text="正在删除 %d/%d：%s" % (i, total, site.get("name", "")))
                try:
                    self.api.delete_site(site["id"])
                    ok += 1
                except Exception as e:
                    fail += 1
                    errs.append("%s：%s" % (site.get("name", ""), e))
            self.ui(self._after_delete_sites, ok, fail, errs)

        threading.Thread(target=work, daemon=True).start()

    def _after_delete_sites(self, ok, fail, errs=None):
        msg = "已删除 %d 个采集点" % ok
        if fail:
            msg += "，失败 %d 个" % fail
        self.lbl_task.config(text=msg)
        self.set_status(msg, "#1f7a3d" if not fail else "#b3261e")
        if errs:
            messagebox.showwarning(APP_NAME, msg + "\\n\\n" + "\\n".join(errs[:8]))
        self.do_refresh()

'''
    s = s[:start] + new + s[end:]

# 2) delete_checked_sites 走统一实现
old = '''        def work():
            ok = fail = 0
            for site in sites:
                try:
                    self.api.delete_site(site["id"])
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_sites, ok, fail)

        self.lbl_task.config(text="正在删除…")
        threading.Thread(target=work, daemon=True).start()'''
if old in s:
    s = s.replace(old, '''        self._delete_sites(sites)''')
    print('delete_checked_sites 复用统一实现')

# 3) 空结果分支也走 _delete_sites（已如此），确认存在
if 'self._delete_sites(empty_sites)' not in s and 'self._delete_sites(empty)' not in s:
    print('警告：空采集点分支没走统一删除')

# 4) 状态栏显示版本
s = s.replace('''        self.set_status("已连接 · 采集点 %d 个 · %s" % (len(items), time.strftime("%H:%M:%S")), "#1f7a3d")''',
'''        self.set_status("已连接 · 采集点 %d 个 · %s · %s" % (len(items), APP_VER, time.strftime("%H:%M:%S")), "#1f7a3d")''')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('打磨完成，版本', VER)
