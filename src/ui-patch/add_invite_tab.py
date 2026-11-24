import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

anchor = '''        def save_all():'''
assert anchor in s

tab = '''        # --- 邀请码（固定码 → 厂商）---
        tab3 = ttk.Frame(nb, padding=12)
        nb.add(tab3, text="邀请码")

        ttk.Label(tab3, text="管理口令（服务器 config.json 里的 adminKey）").pack(anchor="w")
        e_admin = ttk.Entry(tab3, show="*", font=("Consolas", 10))
        e_admin.insert(0, self.cfg.get("admin_key") or "")
        e_admin.pack(fill="x", pady=(2, 8))

        cols3 = ("code", "vendor", "note")
        tv3 = ttk.Treeview(tab3, columns=cols3, show="headings", height=8)
        for c, t, w in zip(cols3, ("邀请码", "厂商", "备注"), (110, 200, 130)):
            tv3.heading(c, text=t)
            tv3.column(c, width=w, anchor="w")
        tv3.pack(fill="both", expand=True, pady=4)

        def reload_codes():
            key = e_admin.get().strip()
            if not key:
                messagebox.showinfo(APP_NAME, "先填管理口令", parent=win)
                return

            def work():
                try:
                    items = self.api.invites(key)
                except Exception as e:
                    self.ui(messagebox.showerror, APP_NAME, "读取失败：%s" % e)
                    return
                self.ui(fill_codes, items)

            def fill_codes(items):
                for i in tv3.get_children():
                    tv3.delete(i)
                for it in items:
                    tv3.insert("", "end", values=(it.get("code"), it.get("vendor"), it.get("note") or ""))
                self.cfg["admin_key"] = key
                save_config(self.cfg)

            threading.Thread(target=work, daemon=True).start()

        row_add = ttk.Frame(tab3)
        row_add.pack(fill="x", pady=(4, 0))
        e_code = ttk.Entry(row_add, width=14)
        e_code.pack(side="left")
        ttk.Label(row_add, text="→").pack(side="left", padx=4)
        e_vendor = ttk.Entry(row_add, width=22)
        e_vendor.pack(side="left")
        e_note = ttk.Entry(row_add, width=12)
        e_note.pack(side="left", padx=4)

        def add_code():
            key = e_admin.get().strip()
            code = e_code.get().strip().upper()
            vendor = e_vendor.get().strip()
            if not code or not vendor:
                messagebox.showinfo(APP_NAME, "邀请码和厂商名都要填", parent=win)
                return

            def work():
                try:
                    self.api.add_invite(code, vendor, e_note.get().strip(), key)
                except Exception as e:
                    self.ui(messagebox.showerror, APP_NAME, "添加失败：%s" % e)
                    return
                self.ui(reload_codes)

            threading.Thread(target=work, daemon=True).start()

        def del_code():
            sel = tv3.selection()
            if not sel:
                return
            code = tv3.item(sel[0], "values")[0]
            if not messagebox.askyesno(APP_NAME, "删除邀请码 %s ？" % code, parent=win):
                return
            key = e_admin.get().strip()

            def work():
                try:
                    self.api.del_invite(code, key)
                except Exception as e:
                    self.ui(messagebox.showerror, APP_NAME, "删除失败：%s" % e)
                    return
                self.ui(reload_codes)

            threading.Thread(target=work, daemon=True).start()

        btns3 = ttk.Frame(tab3)
        btns3.pack(fill="x", pady=(6, 0))
        ttk.Button(btns3, text="读取列表", command=reload_codes).pack(side="left")
        ttk.Button(btns3, text="添加 / 更新", style="Primary.TButton", command=add_code).pack(side="left", padx=6)
        ttk.Button(btns3, text="删除选中", style="Danger.TButton", command=del_code).pack(side="left")

        ttk.Label(tab3, text="采集员在 App 里填这个码，服务器就知道这批照片属于哪个厂商。",
                  foreground="#8a97a8", wraplength=480).pack(anchor="w", pady=(6, 0))

        def save_all():'''

s = s.replace(anchor, tab, 1)

# 窗口大一点，塞得下三页
s = s.replace('win.geometry("560x430")', 'win.geometry("620x520")')

io.open(p, 'w', encoding='utf-8').write(s)
print('邀请码设置页已加')
