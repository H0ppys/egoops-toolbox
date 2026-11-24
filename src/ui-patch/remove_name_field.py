import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

line = '        ttk.Entry(bar, textvariable=self.var_name, width=8).pack(side="left", padx=(8, 8))\n'
if line in s:
    s = s.replace(line, '')
    print('姓名输入框已删')

s = s.replace('        name = self.var_name.get().strip() or "查看者"',
              '        name = self.cfg.get("name") or "查看者"')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('OK，var_name 引用次数：', s.count('var_name'))
