import io

p = 'relay/db.mjs'
s = io.open(p, encoding='utf-8').read()
if '["collectors", "invite"' not in s:
    s = s.replace('''    ["collectors", "vendor", "ALTER TABLE collectors ADD COLUMN vendor TEXT"],''',
'''    ["collectors", "vendor", "ALTER TABLE collectors ADD COLUMN vendor TEXT"],
    ["collectors", "invite", "ALTER TABLE collectors ADD COLUMN invite TEXT"],''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('db: collectors.invite 已加')

p2 = 'relay/server.mjs'
t = io.open(p2, encoding='utf-8').read()
old = '''      db.prepare('INSERT INTO collectors (id, name, phone, token, created_at, vendor) VALUES (?,?,?,?,?,?)')
        .run(id, name, String(b.phone || ''), token, now(), vendor);'''
new = '''      db.prepare('INSERT INTO collectors (id, name, phone, token, created_at, vendor, invite) VALUES (?,?,?,?,?,?,?)')
        .run(id, name, String(b.phone || ''), token, now(), vendor, String(b.invite || '').trim().toUpperCase());'''
assert old in t
t = t.replace(old, new)
io.open(p2, 'w', encoding='utf-8').write(t)
print('server: 登录记录邀请码')
