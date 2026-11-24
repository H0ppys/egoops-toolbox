import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 底部第三行：申请采集点（自动填表）
s = s.replace('''        self.btn_open = ttk.Button(row2, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left", padx=6)''',
'''        self.btn_open = ttk.Button(row2, text="打开下载目录", command=self.open_download_dir)
        self.btn_open.pack(side="left", padx=6)

        row3 = ttk.Frame(bottom)
        row3.pack(fill="x", pady=(8, 0))
        ttk.Label(row3, text="美团：", foreground="#6b7a90").pack(side="left")
        self.btn_fill = ttk.Button(row3, text="申请采集点（自动填表）", style="Big.TButton", command=self.fill_egoops)
        self.btn_fill.pack(side="left")
        ttk.Label(row3, text="用系统 Edge 打开任务分配页，把当前选中采集点的信息填进弹窗",
                  foreground="#6b7a90").pack(side="left", padx=10)''')

# 2) 填表方法
anchor = '    # ---------------------------------------------------------------- 线程通信'
code = '''    # ---------------------------------------------------------------- 申请采集点（自动填表）

    def fill_egoops(self):
        site = self.current_site
        if not site:
            messagebox.showinfo(APP_NAME, "先在左边选一个采集点")
            return
        data = {
            "name": site.get("name", ""),
            "address": site.get("address", ""),
            "area": site.get("area") or "",
            "scene_label": site.get("scene_label") or site.get("scene") or "",
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
                res = mod.run_fill(data, on_log=lambda m: self.ui(self.lbl_task.config, text=m))
                self.ui(self.lbl_task.config, text="填表结束：%s" % res)
            except ImportError:
                self.ui(messagebox.showinfo, APP_NAME,
                        "自动填表需要 playwright：\\n\\n"
                        "1. 打开命令行\\n"
                        "2. 输入：pip install playwright\\n"
                        "3. 装完重启本程序\\n\\n"
                        "（用系统 Edge，不需要下载浏览器内核）")
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "自动填表失败：\\n%s" % e)
            finally:
                self.ui(lambda: self.btn_fill.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

'''
s = s.replace(anchor, code + anchor, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('app patched')
