import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 用本地映射重写「邀请码」设置页（原来的页会调服务器 /api/invites）
start = s.index('        # --- 邀请码（固定码 → 厂商）---')
end = s.index('        def save_all():')

new = '''        # --- 邀请码（本地：码 → 厂商，只存这台电脑）---
        tab3 = ttk.Frame(nb, padding=12)
        nb.add(tab3, text="邀请码")

        ttk.Label(tab3, text="邀请码和厂商的对应关系只保存在这台电脑，服务器不参与。",
                  foreground="#8a97a8").pack(anchor="w", pady=(0, 8))

        cols3 = ("code", "vendor")
        tv3 = ttk.Treeview(tab3, columns=cols3, show="headings", height=9)
        for c, t, w in zip(cols3, ("邀请码", "厂商"), (140, 320)):
            tv3.heading(c, text=t)
            tv3.column(c, width=w, anchor="w")
        tv3.pack(fill="both", expand=True)

        def refresh_codes():
            for i in tv3.get_children():
                tv3.delete(i)
            for code, vendor in sorted(self.invites_map().items()):
                tv3.insert("", "end", values=(code, vendor))

        row_add = ttk.Frame(tab3)
        row_add.pack(fill="x", pady=(8, 0))
        e_code = ttk.Entry(row_add, width=16)
        e_code.pack(side="left")
        ttk.Label(row_add, text="→").pack(side="left", padx=6)
        e_vendor = ttk.Entry(row_add, width=30)
        e_vendor.pack(side="left")

        def add_code():
            code = e_code.get().strip().upper()
            vendor = e_vendor.get().strip()
            if not code or not vendor:
                messagebox.showinfo(APP_NAME, "邀请码和厂商名都要填", parent=win)
                return
            m = dict(self.invites_map())
            m[code] = vendor
            self.cfg["invites"] = m
            save_config(self.cfg)
            refresh_codes()
            self.load_vendors()
            self.do_refresh()
            e_code.delete(0, "end")
            e_vendor.delete(0, "end")

        def del_code():
            sel = tv3.selection()
            if not sel:
                return
            code = tv3.item(sel[0], "values")[0]
            m = dict(self.invites_map())
            m.pop(code, None)
            self.cfg["invites"] = m
            save_config(self.cfg)
            refresh_codes()
            self.load_vendors()
            self.do_refresh()

        # 选中一行时回填到输入框，方便改
        def fill_inputs(_evt=None):
            sel = tv3.selection()
            if sel:
                vals = tv3.item(sel[0], "values")
                e_code.delete(0, "end")
                e_code.insert(0, vals[0])
                e_vendor.delete(0, "end")
                e_vendor.insert(0, vals[1])

        tv3.bind("<<TreeviewSelect>>", fill_inputs)

        btns3 = ttk.Frame(tab3)
        btns3.pack(fill="x", pady=(8, 0))
        ttk.Button(btns3, text="添加 / 更新", style="Primary.TButton", command=add_code).pack(side="left")
        ttk.Button(btns3, text="删除选中", style="Danger.TButton", command=del_code).pack(side="left", padx=6)

        ttk.Label(tab3, text="采集员在 App 里填这个码，数据上传后这里按码显示厂商。",
                  foreground="#8a97a8").pack(anchor="w", pady=(8, 0))

        refresh_codes()

        def save_all():'''

s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('邀请码页改成本地')
