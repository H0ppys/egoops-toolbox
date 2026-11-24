"""删除/下载支持「勾任务行」：
   树上的任务行 iid 形如 site:<id>:task:<taskId>。
   勾了任务但没展开时，也能按任务去服务器取文件。
"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()


def method_span(text, name):
    m = re.search(r'^    def ' + re.escape(name) + r'\(', text, re.M)
    if not m:
        return None
    nxt = re.search(r'^    def ', text[m.end():], re.M)
    return m.start(), (m.end() + nxt.start() if nxt else len(text))


# 1) 新增：把勾选项解析成「采集点 + 任务集合」
if 'def _checked_targets' not in s:
    anchor = '    def _checked_sites(self):'
    block = '''    def _checked_targets(self):
        """把勾选解析成 [{site, tasks:set|None}]；支持勾采集点或勾任务"""
        by_site = {}
        for iid in list(self.checked):
            iid = str(iid)
            if iid in self.site_rows:
                by_site[iid] = None                      # 整个采集点
                continue
            if ":task:" in iid:
                site_iid, _, task_id = iid.rpartition(":task:")
                if site_iid not in self.site_rows:
                    continue
                if by_site.get(site_iid, "missing") is None:
                    continue                              # 已有整站勾选
                if site_iid not in by_site:
                    by_site[site_iid] = set()
                if by_site[site_iid] is not None:
                    by_site[site_iid].add(task_id)
        out = []
        for site_iid, tasks in by_site.items():
            out.append({"site": self.site_rows[site_iid], "tasks": tasks})
        return out

    def collect_files_for_targets(self, targets):
        """按勾选目标去服务器取文件"""
        got = []
        for tg in targets:
            site = tg["site"]
            try:
                detail = self.api.site(site["id"])
            except Exception:
                continue
            want = tg["tasks"]
            for t in detail.get("tasks") or []:
                if want is not None and str(t.get("id")) not in want:
                    continue
                got += (t.get("photos") or []) + (t.get("videos") or [])
        return got

'''
    s = s.replace(anchor, block + anchor, 1)
    print('_checked_targets 已加')

# 2) 删除：用 targets
span = method_span(s, 'delete_checked_files')
if span:
    new_del = '''    def delete_checked_files(self):
        files = self.checked_files()
        if files:
            self._confirm_delete_files(files)
            return

        targets = self._checked_targets()
        if not targets:
            messagebox.showinfo(APP_NAME, "先勾选采集点、任务或文件（点最左边的方框）")
            return

        self.lbl_task.config(text="正在读取勾选目标的文件…")

        def fetch():
            got = self.collect_files_for_targets(targets)
            self.ui(self._confirm_delete_files, got)

        threading.Thread(target=fetch, daemon=True).start()

'''
    s = s[:span[0]] + new_del + s[span[1]:]
    print('delete_checked_files 支持任务勾选')

# 3) 下载：同样支持
span2 = method_span(s, 'download_checked')
if span2:
    new_dl = '''    def download_checked(self):
        files = self.checked_files()
        if files:
            self.download_files(files)
            return

        targets = self._checked_targets()
        if not targets:
            messagebox.showinfo(APP_NAME, "先勾选采集点、任务或文件（点最左边的方框）")
            return

        self.lbl_task.config(text="读取勾选目标的文件…")

        def work():
            got = self.collect_files_for_targets(targets)
            if not got:
                self.ui(messagebox.showinfo, APP_NAME, "勾选的目标里没有文件")
                return
            self.ui(self.download_files, got, False)

        threading.Thread(target=work, daemon=True).start()

'''
    s = s[:span2[0]] + new_dl + s[span2[1]:]
    print('download_checked 支持任务勾选')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('语法 OK')
