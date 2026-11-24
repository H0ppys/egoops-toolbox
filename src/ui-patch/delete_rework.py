"""彻底重做「勾选→删除/下载」：
   · 统一解析：勾采集点 / 勾任务 / 勾文件，三种都支持，一次请求按需拉取
   · 任何异常都弹出来（不再静默）
   · 删除前弹出「预览清单」窗口：列出要删的文件名，确认后才删
   · 窗口标题带版本号，方便确认装的是新版
"""

import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

APP_VER = 'v12'

# 0) 标题带版本
s = re.sub(r'root\.title\(APP_NAME\)', 'root.title(APP_NAME + " " + APP_VER)', s, count=1)
if 'APP_VER = ' not in s:
    s = s.replace('APP_NAME = ', 'APP_VER = "%s"\nAPP_NAME = ' % APP_VER, 1)


def span(text, name):
    m = re.search(r'^    def ' + re.escape(name) + r'\(', text, re.M)
    if not m:
        return None
    nxt = re.search(r'^    def ', text[m.end():], re.M)
    return m.start(), (m.end() + nxt.start() if nxt else len(text))


# 1) 统一解析
if 'def resolve_selected_files' not in s:
    anchor = '    def _checked_sites(self):'
    block = '''    def resolve_selected_files(self):
        """把当前勾选统一解析成文件列表；返回 (files, report)"""
        files, seen = [], set()
        report = {"sites": 0, "tasks": 0, "files": 0, "errors": []}

        def add(f):
            if f and f.get("id") not in seen:
                seen.add(f.get("id"))
                files.append(f)

        # 直接勾的文件
        for iid in list(self.checked):
            f = self.file_rows.get(iid)
            if f:
                add(f)
                report["files"] += 1

        # 采集点 / 任务
        site_tasks = {}      # site_iid -> set(task_id) 或 None
        for iid in list(self.checked):
            iid = str(iid)
            if iid in self.site_rows:
                site_tasks[iid] = None
                report["sites"] += 1
                continue
            if ":task:" in iid:
                site_iid, _, tid = iid.rpartition(":task:")
                if site_iid in self.site_rows:
                    if site_tasks.get(site_iid, "x") is None:
                        continue
                    site_tasks.setdefault(site_iid, set()).add(tid)
                    report["tasks"] += 1

        for site_iid, tids in site_tasks.items():
            site = self.site_rows[site_iid]
            try:
                detail = self.api.site(site["id"])
            except Exception as e:
                report["errors"].append("%s 读取失败：%s" % (site.get("name"), e))
                continue
            for t in detail.get("tasks") or []:
                if tids is not None and str(t.get("id")) not in tids:
                    continue
                for f in (t.get("photos") or []) + (t.get("videos") or []):
                    add(f)
        return files, report

'''
    s = s.replace(anchor, block + anchor, 1)
    print('resolve_selected_files 已加')

# 2) 删除：统一解析 + 清单确认
sp = span(s, 'delete_checked_files')
if sp:
    new = '''    def delete_checked_files(self):
        self.lbl_task.config(text="正在统计要删除的文件…")

        def work():
            try:
                files, report = self.resolve_selected_files()
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "统计失败：%s" % e)
                return
            self.ui(self._delete_preview, files, report)

        threading.Thread(target=work, daemon=True).start()

    def _delete_preview(self, files, report):
        if report["errors"]:
            messagebox.showwarning(APP_NAME, "读取时有问题：\\n" + "\\n".join(report["errors"][:5]))

        if not files:
            messagebox.showinfo(
                APP_NAME,
                "选中范围内没有文件。\\n\\n本次解析结果：\\n"
                "  采集点 %d 个\\n  任务 %d 个\\n  单个文件 %d 个\\n\\n"
                "请勾选采集点、任务或文件后再试。" % (report["sites"], report["tasks"], report["files"]))
            self.lbl_task.config(text="没有可删除的文件")
            return

        win = tk.Toplevel(self.root)
        win.title("确认删除 %d 个文件" % len(files))
        win.geometry("560x460")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="以下文件将被永久删除，确认无误再点删除：",
                  padding=12).pack(anchor="w")

        box = ttk.Frame(win, padding=(12, 0, 12, 8))
        box.pack(fill="both", expand=True)
        tv = ttk.Treeview(box, columns=("name", "kind", "size"), show="headings", height=12)
        for c, t, w in (("name", "文件名", 300), ("kind", "类型", 70), ("size", "大小", 90)):
            tv.heading(c, text=t)
            tv.column(c, width=w, anchor="w")
        for f in files[:300]:
            tv.insert("", "end", values=(f.get("filename", ""),
                                         "照片" if f.get("kind") == "photo" else "视频",
                                         human_size(f.get("size", 0))))
        sb = ttk.Scrollbar(box, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        bar = ttk.Frame(win, padding=12)
        bar.pack(fill="x")

        def do_delete():
            win.destroy()
            self.lbl_task.config(text="正在删除…")

            def run():
                ok = fail = 0
                for f in files:
                    try:
                        self.api.delete_file(f["id"])
                        ok += 1
                    except Exception:
                        fail += 1
                self.ui(self.after_delete_files, ok, fail)

            threading.Thread(target=run, daemon=True).start()

        ttk.Button(bar, text="取消", command=win.destroy).pack(side="right", padx=6)
        ttk.Button(bar, text="确认删除 %d 个" % len(files), style="Accent.TButton",
                   command=do_delete).pack(side="right")

'''
    s = s[:sp[0]] + new + s[sp[1]:]
    print('delete_checked_files 重做')

# 3) 下载也用统一解析
sp2 = span(s, 'download_checked')
if sp2:
    new2 = '''    def download_checked(self):
        files = self.checked_files()
        if files:
            self.download_files(files)
            return

        self.lbl_task.config(text="正在统计要下载的文件…")

        def work():
            try:
                files2, report = self.resolve_selected_files()
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "统计失败：%s" % e)
                return
            if not files2:
                self.ui(messagebox.showinfo, APP_NAME,
                        "选中范围内没有文件（采集点 %d / 任务 %d / 文件 %d）"
                        % (report["sites"], report["tasks"], report["files"]))
                return
            self.ui(self.download_files, files2, False)

        threading.Thread(target=work, daemon=True).start()

'''
    s = s[:sp2[0]] + new2 + s[sp2[1]:]
    print('download_checked 统一解析')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('语法 OK')
