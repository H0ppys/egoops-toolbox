"""修：代码里还在用 ent_server/ent_name 这些旧控件，改成 var_server/var_name。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
    ('self.ent_server.get()', 'self.var_server.get()'),
    ('self.ent_server.delete(0, "end")', 'self.var_server.set("")'),
    ('self.ent_server.insert(0, self.cfg["server"])', 'self.var_server.set(self.cfg["server"])'),
    ('self.ent_name.get()', 'self.var_name.get()'),
    ('self.ent_name.delete(0, "end")', 'self.var_name.set("")'),
    ('self.ent_name.insert(0, self.cfg["name"])', 'self.var_name.set(self.cfg["name"])'),
    ('self.ent_invite.get()', 'self.cfg.get("invite", "")'),
    ('self.ent_invite.delete(0, "end")', ''),
    ('self.ent_invite.insert(0, self.cfg.get("invite", ""))', ''),
]

n = 0
for old, new in pairs:
    if old in s:
        s = s.replace(old, new)
        n += 1

io.open(p, 'w', encoding='utf-8').write(s)
print('替换了 %d 类旧引用' % n)

# 看还有没有残留
rest = [l for l in s.splitlines() if 'ent_server' in l or 'ent_name' in l or 'ent_invite' in l]
print('残留行:')
for l in rest[:10]:
    print('  ', l.strip())
