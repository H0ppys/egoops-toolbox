"""谨慎地改三处（按缩进定位方法边界，避免切掉别的方法）。"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()


def method_span(text, name):
    """返回 (start, end) —— 方法从定义行到下一个同级 def 之前"""
    m = re.search(r'^    def ' + re.escape(name) + r'\(', text, re.M)
    if not m:
        return None
    start = m.start()
    nxt = re.search(r'^    def ', text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return start, end


# 1) 线程里改 UI
s = s.replace('                self.root.after(300, self.auto_sync_drafts)',
              '                self.ui(self.auto_sync_drafts)')

# 2) checked_files 加固
span = method_span(s, 'checked_files')
if span:
    new_cf = '''    def checked_files(self):
        """勾选的文件 + 勾选采集点下的所有文件（占位行已删除时也不会崩）"""
        out, seen = [], set()

        def add(f):
            if f and f.get("id") not in seen:
                seen.add(f.get("id"))
                out.append(f)

        for iid in list(self.checked):
            f = self.file_rows.get(iid)
            if f:
                add(f)

        for iid in list(self.checked):
            if not str(iid).startswith("site:") or str(iid).endswith(":loading"):
                continue
            try:
                tasks = self.tree.get_children(iid)
            except Exception:
                continue
            for task_iid in tasks:
                if str(task_iid).endswith(":loading"):
                    continue
                try:
                    files = self.tree.get_children(task_iid)
                except Exception:
                    continue
                for f_iid in files:
                    add(self.file_rows.get(f_iid))
        return out

'''
    s = s[:span[0]] + new_cf + s[span[1]:]
    print('checked_files 已加固')

# 3) delete_checked_files：勾了采集点就去服务器取文件
span2 = method_span(s, 'delete_checked_files')
if span2:
    new_del = '''    def delete_checked_files(self):
        files = self.checked_files()
        sites = self._checked_sites()

        if not files and not sites:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return

        if not files and sites:
            self.lbl_task.config(text="正在读取勾选采集点的文件…")

            def fetch():
                got = []
                for site in sites:
                    try:
                        detail = self.api.site(site["id"])
                    except Exception:
                        continue
                    for t in detail.get("tasks") or []:
                        got += (t.get("photos") or []) + (t.get("videos") or [])
                self.ui(self._confirm_delete_files, got)

            threading.Thread(target=fetch, daemon=True).start()
            return

        self._confirm_delete_files(files)

    def _confirm_delete_files(self, files):
        if not files:
            self.lbl_task.config(text="勾选的采集点里没有文件")
            messagebox.showinfo(APP_NAME, "勾选的采集点里没有文件")
            return

        names = [f.get("filename", "") for f in files]
        preview = "\\n".join("· " + n for n in names[:12])
        if not messagebox.askyesno("确认删除",
                                   "将永久删除 %d 个文件：\\n\\n%s\\n\\n删除后无法恢复，确定吗？"
                                   % (len(names), preview), icon="warning"):
            return

        def work():
            ok = fail = 0
            for f in files:
                try:
                    self.api.delete_file(f["id"])
                    ok += 1
                except Exception:
                    fail += 1
            self.ui(self.after_delete_files, ok, fail)

        threading.Thread(target=work, daemon=True).start()

'''
    s = s[:span2[0]] + new_del + s[span2[1]:]
    print('delete_checked_files 已改')

io.open(p, 'w', encoding='utf-8').write(s)
print('语法检查…')
import ast
ast.parse(s)
print('OK')
