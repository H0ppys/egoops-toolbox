"""空结果提示改成逐条列出每个采集点有多少文件；并在解析报告里带上明细。"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 报告里加入每个采集点的文件数
s = s.replace('''        report = {"sites": 0, "tasks": 0, "files": 0, "errors": []}''',
              '''        report = {"sites": 0, "tasks": 0, "files": 0, "errors": [], "detail": []}''')

s = s.replace('''            for t in detail.get("tasks") or []:
                if tids is not None and str(t.get("id")) not in tids:
                    continue
                for f in (t.get("photos") or []) + (t.get("videos") or []):
                    add(f)
        return files, report''',
'''            cnt = 0
            for t in detail.get("tasks") or []:
                if tids is not None and str(t.get("id")) not in tids:
                    continue
                for f in (t.get("photos") or []) + (t.get("videos") or []):
                    add(f)
                    cnt += 1
            report["detail"].append((site.get("name") or site.get("id"), cnt))
        return files, report''')

# 2) 提示文案
old = '''        if not files:
            messagebox.showinfo(
                APP_NAME,
                "选中范围内没有文件。\\n\\n本次解析结果：\\n"
                "  采集点 %d 个\\n  任务 %d 个\\n  单个文件 %d 个\\n\\n"
                "请勾选采集点、任务或文件后再试。" % (report["sites"], report["tasks"], report["files"]))
            self.lbl_task.config(text="没有可删除的文件")
            return'''
new = '''        if not files:
            lines = ["  %s：%d 个文件" % (n, c) for n, c in (report.get("detail") or [])]
            messagebox.showinfo(
                APP_NAME,
                "这些采集点里没有文件（可能素材之前已经被删掉了）。\\n\\n"
                + ("\\n".join(lines) if lines else "（没有勾选到采集点/任务/文件）"))
            self.lbl_task.config(text="没有可删除的文件")
            return'''
assert old in s, '文案没找到'
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('提示文案已改，语法 OK')
