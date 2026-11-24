"""每次刷新列表，自动核对草稿是否还在：
   · 还在 → 显示「草稿/待审核/已通过」+ 号
   · 已被删（404）→ 清掉本地记录，显示「未建」
   · 登录态失效 → 静默跳过，不打扰
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) do_refresh 之后触发同步
old = '''                self.ui(self.fill_sites, items)'''
new = '''                self.ui(self.fill_sites, items)
                self.root.after(300, self.auto_sync_drafts)'''
assert old in s
s = s.replace(old, new, 1)

# 2) 同步实现
if 'def auto_sync_drafts' not in s:
    anchor = '    # ---------------------------------------------------------------- 树形列表'
    block = '''    def auto_sync_drafts(self):
        """自动核对草稿：不在了就标成「未建」"""
        import time as _t
        if not getattr(self, "api", None):
            return
        drafts = extras.load_drafts()
        if not drafts:
            return
        now = _t.time()
        if now - getattr(self, "_last_draft_sync", 0) < 60:
            return
        self._last_draft_sync = now

        def work():
            try:
                mod = self._load_status_mod()
                tok = mod.egoops_auth.token_of()
                ok, _ = mod.egoops_auth.alive(tok)
                if not ok:
                    return
            except Exception:
                return

            alive, gone = {}, []
            for site_id, info in list(drafts.items()):
                tsid = info.get("task_set_id")
                if not tsid:
                    continue
                try:
                    r = mod.fetch_one(tsid, tok)
                except PermissionError:
                    return
                except Exception:
                    continue
                if r is None:
                    gone.append(site_id)
                else:
                    alive[site_id] = r

            def apply():
                d = extras.load_drafts()
                for site_id in gone:
                    d.pop(site_id, None)
                for site_id, r in alive.items():
                    if site_id in d:
                        d[site_id]["status"] = r.get("status")
                        d[site_id]["status_text"] = r.get("text")
                        d[site_id]["status_at"] = r.get("at")
                extras.save_drafts(d)
                if gone:
                    self.lbl_task.config(text="%d 个草稿在 EgoOps 已被删除，标记为未建" % len(gone))
                self.fill_sites(self.sites)

            self.ui(apply)

        threading.Thread(target=work, daemon=True).start()

    def _load_status_mod(self):
        import importlib.util
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "egoops_status.py")
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egoops_status.py")
        spec = importlib.util.spec_from_file_location("egoops_status_auto", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('自动同步草稿已加')
