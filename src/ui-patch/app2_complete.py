"""app2 补全：缩略图回调防崩、建草稿、质检、导出 CSV。"""

import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

# 1) 缩略图回调防崩
s = s.replace('''                self.thumbs[fid] = tkimg
                self.ui(lambda: label.config(image=tkimg, text=""))''',
'''                self.thumbs[fid] = tkimg

                def show():
                    try:
                        if label.winfo_exists():
                            label.config(image=tkimg, text="")
                    except Exception:
                        pass

                self.ui(show)''')

s = s.replace('''            except Exception as e:
                self.ui(lambda: label.config(text="无预览"))''',
'''            except Exception:
                def nope():
                    try:
                        if label.winfo_exists():
                            label.config(text="无预览")
                    except Exception:
                        pass
                self.ui(nope)''')

# 2) 建草稿：走 egoops_draft.create_draft
old_draft = '''    def make_draft(self):
        if not self.site:
            messagebox.showinfo(APP_NAME, "先选一个采集点")
            return
        if self.login_ok is False:
            messagebox.showwarning(APP_NAME, "EgoOps 未登录，先在「美团」菜单里登录")
            return
        messagebox.showinfo(APP_NAME, "建草稿：当前版本请用主界面（app.py）的一键建草稿")'''
new_draft = '''    def make_draft(self):
        if not self.site:
            messagebox.showinfo(APP_NAME, "先选一个采集点")
            return
        if self.login_ok is False:
            messagebox.showwarning(APP_NAME, "EgoOps 未登录，先在「美团」菜单里登录")
            return

        d = extras.draft_of(self.site["id"])
        if d and not messagebox.askyesno(
                APP_NAME, "这个采集点已经建过草稿（%s），要再建一份吗？" % d.get("task_set_id")):
            return

        code = (self.site.get("invite") or "").strip().upper()
        try:
            systems = self.api.vendor_systems()
        except Exception:
            systems = {}
        if systems.get(code) != "meituan":
            messagebox.showwarning(APP_NAME, "这个采集点的厂商不是美团，EgoOps 流程不适用")
            return

        win = tk.Toplevel(self.root)
        win.title("正在建草稿…")
        win.geometry("520x220")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text="步骤：", style="Sub.TLabel", padding=12).pack(anchor="w")
        logv = tk.StringVar(value="准备中…")
        ttk.Label(win, textvariable=logv, padding=(12, 0), wraplength=480).pack(anchor="w")
        pb = ttk.Progressbar(win, maximum=100, length=460)
        pb.pack(padx=12, pady=12)
        ttk.Button(win, text="关闭", command=win.destroy).pack(pady=(0, 10))

        def ui_log(msg):
            self.ui(lambda: (logv.set(str(msg)), pb.step(2)))

        def work():
            try:
                import egoops_draft as ed
                detail = self.api.site(self.site["id"])
                payload = dict(detail)
                for t in payload.get("tasks") or []:
                    for f in (t.get("photos") or []) + (t.get("videos") or []):
                        f["url"] = "/files/" + f["id"]
                res = ed.create_draft(payload,
                                      relay_files=lambda f: self._local_copy(f),
                                      log=ui_log,
                                      progress=lambda p, t: (self.ui(lambda: pb.configure(value=p)), ui_log(t)))
                extras.remember(self.site["id"], res["task_set_id"], res.get("name", ""))
                self.ui(lambda: (win.destroy(), messagebox.showinfo(
                    APP_NAME, "草稿已建：%s\\n任务 %d 个" % (res["task_set_id"], len(res.get("tasks") or [])))))
                self.ui(self.refresh)
            except Exception as e:
                self.ui(lambda: (logv.set("失败：%s" % e), messagebox.showerror(APP_NAME, "建草稿失败：%s" % e)))

        threading.Thread(target=work, daemon=True).start()

    def _local_copy(self, f):
        """把服务器上的素材下载到临时目录，供建草稿使用"""
        path = os.path.join(HERE, ".cache", f["id"] + os.path.splitext(f.get("filename") or "")[1])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            self.api.download("/files/" + f["id"], path)
        return path'''
assert old_draft in s
s = s.replace(old_draft, new_draft)

# 3) 质检：下载后本地检查
old_qc = '''    def qc_site(self):
        if not self.site:
            messagebox.showinfo(APP_NAME, "先选一个采集点")
            return
        messagebox.showinfo(APP_NAME, "质检：先下载素材后本地检查（现有实现保留在主界面）")'''
new_qc = '''    def qc_site(self):
        if not self.site:
            messagebox.showinfo(APP_NAME, "先选一个采集点")
            return
        self.set_status("质检中…")

        def work():
            try:
                detail = self.api.site(self.site["id"])
                files = []
                for t in detail.get("tasks") or []:
                    files += (t.get("photos") or []) + (t.get("videos") or [])
                issues = []
                for f in files:
                    if not f.get("size"):
                        issues.append("%s：文件为 0 字节" % f.get("filename"))
                if issues:
                    self.ui(messagebox.showwarning, APP_NAME, "发现 %d 个问题：\\n\\n%s"
                            % (len(issues), "\\n".join(issues[:10])))
                else:
                    self.ui(messagebox.showinfo, APP_NAME, "质检通过：%d 个素材都有内容" % len(files))
                self.ui(self.set_status, "质检完成", "#15803D")
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "质检失败：%s" % e)

        threading.Thread(target=work, daemon=True).start()'''
assert old_qc in s
s = s.replace(old_qc, new_qc)

# 4) 导出 CSV
old_exp = '''    def export_csv(self):
        messagebox.showinfo(APP_NAME, "导出功能沿用主界面")'''
new_exp = '''    def export_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")],
                                            initialfile="采集点.csv")
        if not path:
            return
        rows = []
        for s in self.sites:
            rows.append([s.get("name", ""), s.get("address", ""), s.get("file_count", 0),
                         s.get("created_by", ""), (s.get("created_at") or "")[:19], self.draft_text(s)])
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                import csv
                w = csv.writer(f)
                w.writerow(["门店", "地址", "文件数", "采集员", "时间", "EgoOps"])
                w.writerows(rows)
            messagebox.showinfo(APP_NAME, "已导出 %d 条" % len(rows))
        except Exception as e:
            messagebox.showerror(APP_NAME, "导出失败：%s" % e)'''
assert old_exp in s
s = s.replace(old_exp, new_exp)

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('app2 补全完成，语法 OK')
