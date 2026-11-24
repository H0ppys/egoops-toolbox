"""checked_files 加固：占位行(…:loading)可能已被删除，直接访问会抛 TclError，
   导致「删除勾选/下载勾选」整段静默失败。全部 try 包住并跳过占位行。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    def checked_files(self):')
end = s.index('    def download_checked_sites(self):')

new = '''    def checked_files(self):
        """勾选的文件 + 勾选采集点下的所有文件（对占位行做了容错）"""
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
            if not iid.startswith("site:") or iid.endswith(":loading"):
                continue
            try:
                tasks = self.tree.get_children(iid)
            except Exception:
                continue
            for task_iid in tasks:
                if task_iid.endswith(":loading"):
                    continue
                try:
                    files = self.tree.get_children(task_iid)
                except Exception:
                    continue
                for f_iid in files:
                    add(self.file_rows.get(f_iid))
        return out

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('checked_files 已加固')
