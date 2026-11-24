import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

# 1) 建采集点时写入厂商（来自采集员的邀请码）
old = '''      db.prepare('INSERT INTO sites (id, site_key, name, address, note, created_by, created_at, scene, scene_label, area) VALUES (?,?,?,?,?,?,?,?,?,?)')
        .run(id, key, name, address, String(b.note || '').trim(), collector.name, now(),
          String(b.scene || '').trim(), String(b.scene_label || '').trim(),
          b.area === undefined || b.area === null || b.area === '' ? null : Number(b.area));'''
new = '''      db.prepare('INSERT INTO sites (id, site_key, name, address, note, created_by, created_at, scene, scene_label, area, vendor) VALUES (?,?,?,?,?,?,?,?,?,?,?)')
        .run(id, key, name, address, String(b.note || '').trim(), collector.name, now(),
          String(b.scene || '').trim(), String(b.scene_label || '').trim(),
          b.area === undefined || b.area === null || b.area === '' ? null : Number(b.area),
          String(collector.vendor || b.vendor || '').trim());'''
assert old in s
s = s.replace(old, new)

# 2) 采集点列表支持按厂商过滤
old2 = '''    if (req.method === 'GET' && p === '/api/sites') {
      const rows = db.prepare('SELECT * FROM sites ORDER BY created_at DESC LIMIT 300').all();
      return send(res, 200, { items: rows.map(s => siteView(s)) });
    }'''
new2 = '''    if (req.method === 'GET' && p === '/api/sites') {
      const vendor = (u.searchParams.get('vendor') || '').trim();
      const rows = vendor
        ? db.prepare('SELECT * FROM sites WHERE vendor = ? ORDER BY created_at DESC LIMIT 300').all(vendor)
        : db.prepare('SELECT * FROM sites ORDER BY created_at DESC LIMIT 300').all();
      return send(res, 200, { items: rows.map(s => siteView(s)) });
    }

    // 厂商列表（查看器用来做筛选下拉）
    if (req.method === 'GET' && p === '/api/vendors') {
      const rows = db.prepare("SELECT vendor, COUNT(*) c FROM sites WHERE vendor IS NOT NULL AND vendor <> '' GROUP BY vendor ORDER BY c DESC").all();
      return send(res, 200, { items: rows.map(r => ({ vendor: r.vendor, sites: r.c })) });
    }'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('site vendor wired')
