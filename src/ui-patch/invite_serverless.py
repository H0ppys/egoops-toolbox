import io

# ---------- 1) db.mjs：sites 增加 invite 列 ----------
p = 'relay/db.mjs'
s = io.open(p, encoding='utf-8').read()
if '["sites", "invite"' not in s:
    s = s.replace('''    ["sites", "vendor", "ALTER TABLE sites ADD COLUMN vendor TEXT"],''',
'''    ["sites", "vendor", "ALTER TABLE sites ADD COLUMN vendor TEXT"],
    ["sites", "invite", "ALTER TABLE sites ADD COLUMN invite TEXT"],''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('db: sites.invite 已加')

# ---------- 2) server.mjs ----------
p2 = 'relay/server.mjs'
t = io.open(p2, encoding='utf-8').read()

# 2.1 建采集点时存邀请码（不做任何校验，服务器不关心厂商）
old = '''      db.prepare('INSERT INTO sites (id, site_key, name, address, note, created_by, created_at, scene, scene_label, area, vendor) VALUES (?,?,?,?,?,?,?,?,?,?,?)')
        .run(id, key, name, address, String(b.note || '').trim(), collector.name, now(),
          String(b.scene || '').trim(), String(b.scene_label || '').trim(),
          b.area === undefined || b.area === null || b.area === '' ? null : Number(b.area),
          String(collector.vendor || b.vendor || '').trim());'''
new = '''      const inviteCode = String(b.invite || collector.invite || '').trim().toUpperCase();
      db.prepare('INSERT INTO sites (id, site_key, name, address, note, created_by, created_at, scene, scene_label, area, vendor, invite) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)')
        .run(id, key, name, address, String(b.note || '').trim(), collector.name, now(),
          String(b.scene || '').trim(), String(b.scene_label || '').trim(),
          b.area === undefined || b.area === null || b.area === '' ? null : Number(b.area),
          '', inviteCode);'''
assert old in t
t = t.replace(old, new)

# 2.2 登录：不再校验固定码，只把码记下来（兼容旧调用）
old2 = '''      const b = await readJson(req);
      const invite = ensureInvite(b);
      const name = String(b.name || '').trim();
      if (!name) throw bad('请填写姓名');
      const vendor = invite ? invite.vendor : '';'''
new2 = '''      const b = await readJson(req);
      ensureInvite(b);                       // 只有管理员设置了总码才校验；固定码只做记录
      const name = String(b.name || '').trim();
      if (!name) throw bad('请填写姓名');
      const vendor = '';'''
assert old2 in t
t = t.replace(old2, new2)

# 2.3 登录返回里带上邀请码
t = t.replace('''      return send(res, 200, {
        token,
        vendor,
        collector: { id, name, phone: String(b.phone || ''), vendor },
      });''', '''      return send(res, 200, {
        token,
        vendor,
        invite: String(b.invite || '').trim().toUpperCase(),
        collector: { id, name, phone: String(b.phone || ''), vendor },
      });''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('server: 邀请码原样保存')
