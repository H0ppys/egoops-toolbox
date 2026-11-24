"""服务器加「存储体检 + 清理」接口；查看器加菜单入口。"""

import io

# ---------------- 服务器 ----------------
p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

if '/api/storage' not in s:
    anchor = "    // 删除一个文件"
    block = '''    // 存储体检：数据库记录 vs 磁盘
    if (req.method === 'GET' && p === '/api/storage') {
      const rows = db.prepare('SELECT id, path, size FROM files').all();
      const known = new Set(rows.map(r => path.resolve(HERE, r.path)));
      let diskBytes = 0, orphanBytes = 0, orphanCount = 0;
      const walk = (dir) => {
        let ents = [];
        try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch (_) { return; }
        for (const e of ents) {
          const full = path.join(dir, e.name);
          if (e.isDirectory()) { walk(full); continue; }
          let st; try { st = fs.statSync(full); } catch (_) { continue; }
          diskBytes += st.size;
          if (!known.has(full)) { orphanCount++; orphanBytes += st.size; }
        }
      };
      walk(DATA);
      let tmpBytes = 0;
      try {
        for (const e of fs.readdirSync(TMP, { withFileTypes: true })) {
          if (!e.isDirectory()) continue;
          const d = path.join(TMP, e.name);
          for (const f2 of fs.readdirSync(d)) {
            try { tmpBytes += fs.statSync(path.join(d, f2)).size; } catch (_) {}
          }
        }
      } catch (_) {}
      return send(res, 200, {
        db_files: rows.length,
        db_bytes: rows.reduce((n, r) => n + (r.size || 0), 0),
        disk_bytes: diskBytes,
        orphan_files: orphanCount,
        orphan_bytes: orphanBytes,
        tmp_bytes: tmpBytes,
      });
    }

    // 清理：删掉磁盘上没有数据库记录的残留文件 + 超过 1 天的上传分片
    if (req.method === 'POST' && p === '/api/storage/cleanup') {
      const rows = db.prepare('SELECT path FROM files').all();
      const known = new Set(rows.map(r => path.resolve(HERE, r.path)));
      let freed = 0, removed = 0;
      const walk = (dir) => {
        let ents = [];
        try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch (_) { return; }
        for (const e of ents) {
          const full = path.join(dir, e.name);
          if (e.isDirectory()) { walk(full); continue; }
          if (known.has(full)) continue;
          try {
            const sz = fs.statSync(full).size;
            fs.unlinkSync(full);
            freed += sz; removed++;
          } catch (_) {}
        }
      };
      walk(DATA);

      // 过期分片
      const cutoff = Date.now() - 24 * 3600 * 1000;
      try {
        for (const e of fs.readdirSync(TMP, { withFileTypes: true })) {
          if (!e.isDirectory()) continue;
          const d = path.join(TMP, e.name);
          let mt = 0;
          try { mt = fs.statSync(d).mtimeMs; } catch (_) {}
          if (mt && mt > cutoff) continue;
          try { fs.rmSync(d, { recursive: true, force: true }); } catch (_) {}
        }
      } catch (_) {}

      return send(res, 200, { removed_files: removed, freed_bytes: freed });
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('server: /api/storage 已加')

# ---------------- 查看器 ----------------
p2 = 'viewer/app.py'
t = io.open(p2, encoding='utf-8').read()

if 'storage_dialog' not in t:
    anchor2 = '    def open_settings(self):'
    block2 = '''    def storage_dialog(self):
        self.lbl_task.config(text="正在检查服务器存储…")

        def work():
            try:
                st = self.api._request("GET", "/api/storage", timeout=30)
            except Exception as e:
                self.ui(messagebox.showerror, APP_NAME, "检查失败：%s" % e)
                return
            self.ui(self._show_storage, st)

        threading.Thread(target=work, daemon=True).start()

    def _show_storage(self, st):
        def human(n):
            n = float(n or 0)
            for unit in ("B", "KB", "MB", "GB"):
                if n < 1024:
                    return "%.1f %s" % (n, unit)
                n /= 1024
            return "%.1f TB" % n

        msg = (
            "数据库记录：%d 个文件，%s\\n"
            "磁盘实际：%s\\n"
            "无记录的残留文件：%d 个，%s\\n"
            "未完成的上传分片：%s\\n"
        ) % (st.get("db_files", 0), human(st.get("db_bytes")),
             human(st.get("disk_bytes")),
             st.get("orphan_files", 0), human(st.get("orphan_bytes")),
             human(st.get("tmp_bytes")))

        if st.get("db_bytes") == st.get("disk_bytes") and not st.get("orphan_files"):
            msg += "\\n✓ 数据库与磁盘一致，没有多余备份。"

        if messagebox.askyesno(APP_NAME, msg + "\\n\\n要清理残留文件吗？"):
            self.lbl_task.config(text="正在清理…")

            def run():
                try:
                    r = self.api._request("POST", "/api/storage/cleanup", {}, timeout=60)
                except Exception as e:
                    self.ui(messagebox.showerror, APP_NAME, "清理失败：%s" % e)
                    return
                self.ui(messagebox.showinfo, APP_NAME,
                        "已清理 %d 个残留文件，释放 %s"
                        % (r.get("removed_files", 0), human(r.get("freed_bytes"))))
                self.ui(self.do_refresh)

            threading.Thread(target=run, daemon=True).start()

'''
    assert anchor2 in t
    t = t.replace(anchor2, block2 + anchor2, 1)

    # 菜单项
    t = t.replace('        m_set.add_command(label="设置…", command=self.open_settings)',
                  '        m_set.add_command(label="服务器空间 / 清理…", command=self.storage_dialog)\n'
                  '        m_set.add_command(label="设置…", command=self.open_settings)')

    io.open(p2, 'w', encoding='utf-8').write(t)
    print('查看器: 存储体检菜单已加')
