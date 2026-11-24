import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old1 = '        self.cmb_range = ttk.Combobox(bar, width=7, state="readonly",'
new1 = '        ttk.Label(bar, text="时间", style="Dim.TLabel").pack(side="left")\n' + old1
if old1 in s and 'text="时间"' not in s.split('def _build')[1][:6000]:
    s = s.replace(old1, new1, 1)

old2 = '        self.preview.pack(fill="both", expand=False, pady=(0, 6), ipady=6)'
new2 = '        self.preview.pack(fill="x", expand=False, pady=(0, 6), ipady=26)'
if old2 in s:
    s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
