import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    def fill_egoops(self):')
end = s.index('    # ---------------------------------------------------------------- 线程通信')
new = '''    def fill_egoops(self):
        site = self.current_site
        if not site:
            messagebox.showinfo(APP_NAME, "先在左边选一个采集点")
            return

        labels = [
            ("name", "采集点名称", site.get("name", "")),
            ("address", "现场地址", site.get("address", "")),
            ("area", "场地面积", site.get("area") or ""),
            ("scene", "采集场景分类", site.get("scene_label") or site.get("scene") or ""),
            ("note", "采集点描述", site.get("note") or ""),
        ]
        saved = self.cfg.get("fill_fields")
        if not isinstance(saved, list):
            saved = [k for k, _, _ in labels]

        win = tk.Toplevel(self.root)
        win.title("选择要填哪些字段")
        win.geometry("420x320")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        ttk.Label(win, text="勾选要自动填的字段（不勾的就留空，你手动填）",
                  font=("Microsoft YaHei UI", 10)).pack(anchor="w", padx=16, pady=(14, 8))

        vars_ = {}
        for key, label, value in labels:
            v = tk.BooleanVar(value=(key in saved))
            vars_[key] = v
            row = ttk.Frame(win)
            row.pack(fill="x", padx=16, pady=2)
            ttk.Checkbutton(row, text=label, variable=v).pack(side="left")
            preview = str(value)
            if len(preview) > 22:
                preview = preview[:22] + "…"
            ttk.Label(row, text=("  " + preview) if preview else "  （空）",
                      foreground="#8a97a8").pack(side="left")

        def go():
            chosen = [k for k, v in vars_.items() if v.get()]
            if not chosen:
                messagebox.showinfo(APP_NAME, "至少勾一个字段", parent=win)
                return
            self.cfg["fill_fields"] = chosen
            save_config(self.cfg)
            win.destroy()
            self._start_fill(site, chosen)

        btns = ttk.Frame(win)
        btns.pack(pady=14)
        ttk.Button(btns, text="开始填表", style="Big.TButton", command=go).pack(side="left", padx=6)
        ttk.Button(btns, text="取消", command=win.destroy).pack(side="left", padx=6)

    def _start_fill(self, site, fields):
        data = {
            "name": site.get("name", ""),
            "address": site.get("address", ""),
            "area": site.get("area") or "",
            "scene_label": site.get("scene_label") or site.get("scene") or "",
            "note": site.get("note") or "",
            "tasks": [{"area": t.get("area") or "", "name": t.get("name") or ""}
                      for t in (site.get("tasks") or [])],
        }
        self.lbl_task.config(text="正在打开 Edge…")
        self.btn_fill.config(state="disabled")

        def work():
            try:
                import importlib.util
                import sys as _sys
                base = getattr(_sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(base, "fill_egoops.py")
                spec = importlib.util.spec_from_file_location("fill_egoops", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                res = mod.run_fill(data, fields=fields,
                                   on_log=lambda m: self.ui(self.lbl_task.config, text=m))
                self.ui(self.lbl_task.config, text="填表结束：%s" % res)
            except ImportError:
                self.ui(messagebox.showinfo, APP_NAME,
                        "自动填表需要 playwright：\\n\\n1. 命令行执行：pip install playwright\\n2. 重启本程序")
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "自动填表失败：\\n%s" % e)
            finally:
                self.ui(lambda: self.btn_fill.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('fill dialog patched')
