import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")'''
new = '''        treeWrap = ttk.Frame(body)
        treeWrap.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(treeWrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(in_=treeWrap, side="left", fill="both", expand=True)
        vsb.pack(in_=treeWrap, side="right", fill="y")'''

assert old in s
s = s.replace(old, new)

s = s.replace('root.geometry("1440x820")', 'root.geometry("1440x880")')
io.open(p, 'w', encoding='utf-8').write(s)
print('preview layout fixed')
