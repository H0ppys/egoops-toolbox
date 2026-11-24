"""查看器：搜索框 + 日期筛选 + 草稿状态回查。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 工具栏：搜索 + 时间范围 ----------
if 'ent_search' not in s:
    s = s.replace('''        ttk.Label(top, text="厂商", foreground="#6b7a90").pack(side="left", padx=(12, 0))''',
'''        ttk.Label(top, text="搜", foreground="#6b7a90").pack(side="left", padx=(12, 0))
        self.ent_search = ttk.Entry(top, width=18)
        self.ent_search.pack(side="left", padx=(4, 8))
        self.ent_search.bind("<Return>", lambda e: self.do_refresh())
        self.ent_search.bind("<KeyRelease>", self._on_search_typing)

        ttk.Label(top, text="时间", foreground="#6b7a90").pack(side="left")
        self.cmb_range = ttk.Combobox(top, width=8, state="readonly",
                                      values=["全部", "今天", "近 7 天", "近 30 天"])
        self.cmb_range.set("全部")
        self.cmb_range.pack(side="left", padx=(4, 8))
        self.cmb_range.bind("<<ComboboxSelected>>", lambda e: self.do_refresh())

        ttk.Label(top, text="厂商", foreground="#6b7a90").pack(side="left", padx=(4, 0))''')

# ---------- 2) 过滤逻辑 ----------
if 'def _apply_filters' not in s:
    s = s.replace('''    def fill_sites(self, items):''', '''    def _on_search_typing(self, event=None):
        # 输入停顿 400ms 再过滤，避免每敲一下就刷
        if getattr(self, "_search_job", None):
            try:
                self.root.after_cancel(self._search_job)
            except Exception:
                pass
        self._search_job = self.root.after(400, self.do_refresh)

    def _apply_filters(self, items):
        import datetime
        kw = ""
        try:
            kw = (self.ent_search.get() or "").strip().lower()
        except Exception:
            pass
        rng = "全部"
        try:
            rng = self.cmb_range.get()
        except Exception:
            pass

        limit = None
        now = datetime.datetime.now()
        if rng == "今天":
            limit = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif rng == "近 7 天":
            limit = now - datetime.timedelta(days=7)
        elif rng == "近 30 天":
            limit = now - datetime.timedelta(days=30)

        out = []
        for it in items:
            if kw:
                blob = " ".join(str(it.get(k) or "") for k in
                                ("name", "address", "created_by", "invite", "scene_label")).lower()
                if kw not in blob:
                    continue
            if limit:
                ts = (it.get("created_at") or "")[:19].replace("T", " ")
                try:
                    dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    if dt < limit:
                        continue
                except Exception:
                    pass
            out.append(it)
        return out

    def fill_sites(self, items):''')

s = s.replace('''    def fill_sites(self, items):
        self.sites = items''', '''    def fill_sites(self, items):
        items = self._apply_filters(items)
        self.sites = items''')

# ---------- 3) 草稿状态：列里显示，菜单里刷新 ----------
s = s.replace('''    def draft_text(self, site):
        d = extras.draft_of(site.get("id"))
        if not d:
            return "未建"
        return "草稿 " + str(d.get("task_set_id"))[-6:]''',
'''    def draft_text(self, site):
        d = extras.draft_of(site.get("id"))
        if not d:
            return "未建"
        st = (d.get("status") or "").strip()
        text = {"draft": "草稿", "submitted": "待审核", "pending": "待审核",
                "approved": "已通过", "rejected": "驳回", "missing": "已删除"}.get(st, "")
        if text:
            return "%s %s" % (text, str(d.get("task_set_id"))[-6:])
        return "草稿 " + str(d.get("task_set_id"))[-6:]''')

if 'def refresh_draft_status' not in s:
    s = s.replace('''    def invites_map(self):''', '''    def refresh_draft_status(self):
        import importlib.util
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "egoops_status.py")
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egoops_status.py")
        spec = importlib.util.spec_from_file_location("egoops_status", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        drafts = extras.load_drafts()
        if not drafts:
            messagebox.showinfo(APP_NAME, "还没有建过草稿")
            return
        self.lbl_task.config(text="正在查 EgoOps 草稿状态…")

        def work():
            try:
                res = mod.refresh_all(drafts, log=lambda m: self.ui(self.lbl_task.config, text=m))
            except PermissionError as e:
                self.ui(messagebox.showerror, APP_NAME, str(e))
                self.ui(self.lbl_task.config, text="查询失败：登录态失效")
                return
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "查询失败：%s" % e)
                return

            def apply():
                d = extras.load_drafts()
                for site_id, info in res.items():
                    if site_id in d:
                        d[site_id]["status"] = info.get("status")
                        d[site_id]["status_text"] = info.get("text")
                        d[site_id]["status_at"] = info.get("at")
                extras.save_drafts(d)
                self.lbl_task.config(text="已更新 %d 条草稿状态" % len(res))
                self.do_refresh()

            self.ui(apply)

        threading.Thread(target=work, daemon=True).start()

    def invites_map(self):''')

# 菜单项
s = s.replace('''        m_mt.add_command(label="刷新 EgoOps 登录态", command=self.refresh_login_state)''',
'''        m_mt.add_command(label="刷新草稿状态（待审核/已通过）", command=self.refresh_draft_status)
        m_mt.add_command(label="刷新 EgoOps 登录态", command=self.refresh_login_state)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('搜索 + 时间筛选 + 草稿状态 已加')
