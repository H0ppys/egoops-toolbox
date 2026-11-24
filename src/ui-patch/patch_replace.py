import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

old = """      const exists = db.prepare('SELECT * FROM sites WHERE site_key = ?').get(key);
      if (exists) return send(res, 200, { site: siteView(exists, true), existing: true });"""

new = """      const exists = db.prepare('SELECT * FROM sites WHERE site_key = ?').get(key);
      if (exists && b.replace === false) {
        return send(res, 200, { site: siteView(exists, true), existing: true, replaced: false });
      }
      if (exists) {
        // 同名同址重复提交 = 覆盖：把旧采集点连同照片视频一起删掉，重新建一个
        const oldFiles = db.prepare('SELECT * FROM files WHERE site_id = ?').all(exists.id);
        for (const f of oldFiles) {
          try { fs.unlinkSync(path.resolve(HERE, f.path)); } catch (_) {}
        }
        db.prepare('DELETE FROM files WHERE site_id = ?').run(exists.id);
        db.prepare('DELETE FROM uploads WHERE site_id = ?').run(exists.id);
        db.prepare('DELETE FROM tasks WHERE site_id = ?').run(exists.id);
        db.prepare('DELETE FROM sites WHERE id = ?').run(exists.id);
        console.log(`[覆盖] ${exists.name} 旧数据 ${oldFiles.length} 个文件已删除`);
      }"""

assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('server replace patched')
