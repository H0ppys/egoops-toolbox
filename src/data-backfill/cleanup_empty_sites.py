"""空采集点处理：
   · 删除勾选时，如果勾的采集点里一个文件都没有 → 提示并可直接删除这些空采集点
   · 菜单「采集点 → 清理空采集点（0 文件）」一键清掉所有空壳
"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()


def span(text, name):
    m = re.search(r'^    def ' + re.escape(name) + r'\(', text, re.M)
    if not m:
        return None
    nxt = re.search(r'^    def ', text[m.end():], re.M)
    return m.start(), (m.end() + nxt.start() if nxt else len(text))


# 1) 空结果时，允许直接删掉空采集点
old = '''        if not files:
            lines = ["  %s：%d 个文件" % (n, c) for n, c in (report.get("detail") or [])]
            messagebox.showinfo(
                APP_NAME,
                "这些采集点里没有文件（可能素材之前已经被删掉了）。\\n\\n"
                + ("\\n".join(lines) if lines else "（没有勾选到采集点/任务/文件）"))
            self.lbl_task.config(text="没有可删除的文件")
            return'''
new = '''        if not files:
            lines = ["  %s：%d 个文件" % (n, c) for n, c in (report.get("detail") or [])]
            empty_sites = [tg for tg in report.get("site_objs") or []]
            msg = ("这些采集点里没有文件（可能素材之前已经被删掉了）。\\n\\n"
                   + ("\\n".join(lines) if lines else "（没有勾选到采集点/任务/文件）"))
            if empty_sites:
                names = "、".join(x.get("name") or "" for x in empty_sites[:6])
                if messagebox.askyesno(
                        APP_NAME,
                        msg + "\\n\\n要把这些「空采集点」直接删掉吗？\\n（%s）\\n\\n"
                              "会同时删除它们名下的任务记录，不可恢复。" % names):
                    self._delete_sites(empty_sites)
                    return
            else:
                messagebox.showinfo(APP_NAME, msg)
            self.lbl_task.config(text="没有可删除的文件")
            return'''
assert old in s, '空结果分支没找到'
s = s.replace(old, new)

# 2) 报告里带上采集点对象
s = s.replace('''report = {"sites": 0, "tasks": 0, "files": 0, "errors": [], "detail": []}''',
              '''report = {"sites": 0, "tasks": 0, "files": 0, "errors": [], "detail": [], "site_objs": []}''')
s = s.replace('''            report["detail"].append((site.get("name") or site.get("id"), cnt))''',
'''            report["detail"].append((site.get("name") or site.get("id"), cnt))
            report["site_objs"].append(site)''')

# 3) 批量删采集点
if 'def _delete_sites' not in s:
    anchor = '    def delete_checked_sites(self):'
    block = '''    def _delete_sites(self, sites):
        self.lbl_task.config(text="正在删除采集点…")

        def work():
            ok = fail = 0
            for site in sites:
                try:
                    self.api.delete_site(site["id"])
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.set_status, "已删除 %d 个采集点，失败 %d" % (ok, fail), "#1f7a3d")
            self.ui(self.do_refresh)

        threading.Thread(target=work, daemon=True).start()

    def cleanup_empty_sites(self):
        self.lbl_task.config(text="正在查找空采集点…")

        def work():
            try:
                items = self.api.sites()
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "读取失败：%s" % e)
                return
            empty = [x for x in items if not x.get("file_count")]
            if not empty:
                self.ui(messagebox.showinfo, APP_NAME, "没有空采集点")
                return
            names = "\\n".join("· %s（%s）" % (x.get("name"), x.get("created_at", "")[:10]) for x in empty[:15])
            self.ui(self._confirm_cleanup_empty, empty, names)

        threading.Thread(target=work, daemon=True).start()

    def _confirm_cleanup_empty(self, empty, names):
        if messagebox.askyesno(APP_NAME,
                               "找到 %d 个没有任何文件的采集点：\\n\\n%s\\n\\n全部删除吗？不可恢复。"
                               % (len(empty), names)):
            self._delete_sites(empty)

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

# 4) 菜单项
s = s.replace('        m_site.add_command(label="删除勾选的采集点", command=self.delete_checked_sites)',
              '        m_site.add_command(label="删除勾选的采集点", command=self.delete_checked_sites)\n'
              '        m_site.add_command(label="清理空采集点（0 文件）", command=self.cleanup_empty_sites)')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('空采集点清理已加，语法 OK')
