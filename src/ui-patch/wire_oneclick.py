import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    def fill_egoops(self):')
end = s.index('    # ---------------------------------------------------------------- 线程通信')

new = '''    def fill_egoops(self):
        """一条龙：建草稿 + 填字段 + 转码上传素材 + 写 SOP，不提交审核"""
        iid = self.tree.focus()
        site = self.site_rows.get(iid)
        if not site:
            messagebox.showinfo(APP_NAME, "先在树里选中一个采集点")
            return

        labels = [
            ("name", "采集点名称", site.get("name", "")),
            ("address", "现场地址", site.get("address", "")),
            ("scene", "采集场景分类", site.get("scene_label") or site.get("scene") or ""),
            ("desc", "采集点描述（模型生成）", "自动"),
            ("sop", "任务描述 + SOP（模型生成）", "自动"),
            ("media", "任务照片/视频（视频自动转 H.264）", "自动"),
        ]
        saved = self.cfg.get("fill_fields")
        if not isinstance(saved, list):
            saved = [k for k, _, _ in labels]

        win = tk.Toplevel(self.root)
        win.title("申请采集点 · 一条龙")
        win.geometry("460x360")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        ttk.Label(win, text="勾选要自动处理的内容，没勾的留空、你去 EgoOps 里手动补",
                  font=("Microsoft YaHei UI", 10)).pack(anchor="w", padx=16, pady=(14, 8))

        vars_ = {}
        for key, label, value in labels:
            v = tk.BooleanVar(value=(key in saved))
            vars_[key] = v
            row = ttk.Frame(win)
            row.pack(fill="x", padx=16, pady=2)
            ttk.Checkbutton(row, text=label, variable=v).pack(side="left")

        ttk.Label(win, text="只生成草稿，不会提交审核；地址取自采集数据，缺了就留空。",
                  foreground="#8a97a8", wraplength=420).pack(anchor="w", padx=16, pady=(10, 0))

        def go():
            chosen = [k for k, v in vars_.items() if v.get()]
            if not chosen:
                messagebox.showinfo(APP_NAME, "至少勾一项", parent=win)
                return
            self.cfg["fill_fields"] = chosen
            save_config(self.cfg)
            win.destroy()
            self._start_draft(site, chosen)

        btns = ttk.Frame(win)
        btns.pack(pady=16)
        ttk.Button(btns, text="开始", style="Big.TButton", command=go).pack(side="left", padx=6)
        ttk.Button(btns, text="取消", command=win.destroy).pack(side="left", padx=6)

    def _start_draft(self, site, fields):
        self.btn_fill.config(state="disabled")
        self.progress["value"] = 0
        self.lbl_task.config(text="准备中…")

        def log(msg):
            self.ui(self.lbl_task.config, text=str(msg))

        def progress(pct, text):
            self.ui(self._set_progress, pct, text)

        def work():
            try:
                # 取完整详情（含任务与文件）
                detail = self.api.site(site["id"])
                for t in detail.get("tasks") or []:
                    for f in (t.get("photos") or []) + (t.get("videos") or []):
                        f["url"] = self.cfg.get("server", "").rstrip("/") + "/files/" + f["id"]
                if "name" not in fields:
                    pass
                import importlib.util
                import sys as _sys
                base = getattr(_sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(base, "egoops_draft.py")
                if not os.path.exists(path):
                    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egoops_draft.py")
                spec = importlib.util.spec_from_file_location("egoops_draft", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                payload = dict(detail)
                if "address" not in fields:
                    payload["address"] = ""
                res = mod.create_draft(payload, log=log, progress=progress)
                self.ui(self._draft_done, res)
            except Exception as e:
                self.ui(self._draft_failed, e)
            finally:
                self.ui(lambda: self.btn_fill.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

    def _set_progress(self, pct, text):
        self.progress["value"] = pct
        self.lbl_task.config(text=text)

    def _draft_done(self, res):
        self.progress["value"] = 100
        self.lbl_task.config(text="草稿已建：%s" % res["task_set_id"])
        lines = [
            "草稿已建好（未提交审核）",
            "",
            "采集点：%s" % res["name"],
            "草稿 ID：%s" % res["task_set_id"],
            "现场地址：%s" % (res["address"] or "（空，需在页面上选）"),
            "素材：照片 %d 张，视频 %d 个" % (res["photos"], res["videos"]),
            "时长：%s 小时，SOP %d 步" % (res["hours"], len(res["sop"])),
            "",
            "去 EgoOps「申报 → 草稿」里核对，没问题再点提交审核。",
        ]
        if messagebox.askyesno(APP_NAME, "\\n".join(lines) + "\\n\\n现在打开 EgoOps 看吗？"):
            import webbrowser
            webbrowser.open("https://egoops.meituan.com/assignment")

    def _draft_failed(self, err):
        self.lbl_task.config(text="失败：%s" % err)
        messagebox.showerror(APP_NAME, "建草稿失败：\\n\\n%s" % err)

'''
s = s[:start] + new + s[end:]

# 按钮文案
s = s.replace('text="申请采集点（自动填表）"', 'text="申请采集点（一键建草稿）"')
s = s.replace('text="用保存的登录态打开 EgoOps，只建草稿、不提交审核"',
              'text="建草稿 + 传素材（视频转 H.264）+ 写 SOP，只存草稿不提交"')

io.open(p, 'w', encoding='utf-8').write(s)
print('one-click wired')
