import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

s = s.replace(
    "db.prepare('INSERT INTO tasks (id, site_id, idx, name, note, created_at) VALUES (?,?,?,?,?,?)')\n      .run(id, siteId, 0, '任务1', '', now());",
    "db.prepare('INSERT INTO tasks (id, site_id, idx, name, area, note, created_at) VALUES (?,?,?,?,?,?,?)')\n      .run(id, siteId, 0, '任务1', '', '', now());")

s = s.replace("""        const tname = String(t && t.name || '').trim() || `任务${i + 1}`;
        db.prepare('INSERT INTO tasks (id, site_id, idx, name, note, created_at) VALUES (?,?,?,?,?,?)')
          .run(uuid(), id, i, tname, String(t && t.note || '').trim(), now());""",
              """        const tname = String(t && t.name || '').trim() || `任务${i + 1}`;
        const tarea = String(t && t.area || '').trim();
        db.prepare('INSERT INTO tasks (id, site_id, idx, name, area, note, created_at) VALUES (?,?,?,?,?,?,?)')
          .run(uuid(), id, i, tname, tarea, String(t && t.note || '').trim(), now());""")

s = s.replace("""      const name = String(b.name || '').trim() || `任务${idx + 1}`;
      db.prepare('INSERT INTO tasks (id, site_id, idx, name, note, created_at) VALUES (?,?,?,?,?,?)')
        .run(id, site.id, idx, name, String(b.note || '').trim(), now());""",
              """      const name = String(b.name || '').trim() || `任务${idx + 1}`;
      const area = String(b.area || '').trim();
      db.prepare('INSERT INTO tasks (id, site_id, idx, name, area, note, created_at) VALUES (?,?,?,?,?,?,?)')
        .run(id, site.id, idx, name, area, String(b.note || '').trim(), now());""")

io.open(p, 'w', encoding='utf-8').write(s)
print('server patched')
