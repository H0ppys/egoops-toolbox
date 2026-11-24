import io

# ---------------- 1) db.mjs：邀请码表 + sites.vendor / collectors.vendor ----------------
p = 'relay/db.mjs'
s = io.open(p, encoding='utf-8').read()

if 'CREATE TABLE IF NOT EXISTS invites' not in s:
    s = s.replace('''    CREATE TABLE IF NOT EXISTS settings (''', '''    CREATE TABLE IF NOT EXISTS invites (
      code        TEXT PRIMARY KEY,
      vendor      TEXT NOT NULL,
      note        TEXT,
      created_at  TEXT NOT NULL,
      disabled    INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS settings (''')

# 迁移：sites.vendor / collectors.vendor
if "sites.vendor" not in s:
    s = s.replace('''export function openDb(file) {''', '''function addColumn(db, table, col, type) {
  try {
    const cols = db.prepare(`PRAGMA table_info(${table})`).all().map((c) => c.name);
    if (!cols.includes(col)) db.exec(`ALTER TABLE ${table} ADD COLUMN ${col} ${type}`);
  } catch (_) {}
}

export function openDb(file) {''')

io.open(p, 'w', encoding='utf-8').write(s)
print('db.mjs 表结构已加')

# ---------------- 2) server.mjs ----------------
p2 = 'relay/server.mjs'
t = io.open(p2, encoding='utf-8').read()

# 2.1 邀请码查表工具（替换旧的单一码逻辑）
old = '''function ensureInvite(b) {
  const need = currentInvite().trim();
  if (need && String(b.invite || '').trim() !== need) throw new ApiError(403, 'INVITE_REQUIRED', '邀请码不正确，请向管理员要最新的码');
}'''
new = '''function findInvite(code) {
  const c = String(code || '').trim().toUpperCase();
  if (!c) return null;
  const row = db.prepare('SELECT * FROM invites WHERE UPPER(code) = ? AND disabled = 0').get(c);
  return row || null;
}

function ensureInvite(b) {
  const code = String(b.invite || '').trim();
  const fixed = findInvite(code);
  if (fixed) return fixed;                       // 固定邀请码：直接带上厂商
  const need = currentInvite().trim();
  if (need && code !== need) throw new ApiError(403, 'INVITE_REQUIRED', '邀请码不正确，请向管理员要最新的码');
  return null;
}'''
assert old in t
t = t.replace(old, new)

# 2.2 登录：记录厂商，返回厂商名
old2 = '''      const b = await readJson(req);
      ensureInvite(b);
      const name = String(b.name || '').trim();
      if (!name) throw bad('请填写姓名');
      const token = uuid().replace(/-/g, '');
      const id = uuid();
      db.prepare('INSERT INTO collectors (id, name, phone, token, created_at) VALUES (?,?,?,?,?)')
        .run(id, name, String(b.phone || ''), token, now());
      return send(res, 200, { token, collector: { id, name, phone: String(b.phone || '') } });'''
new2 = '''      const b = await readJson(req);
      const invite = ensureInvite(b);
      const name = String(b.name || '').trim();
      if (!name) throw bad('请填写姓名');
      const vendor = invite ? invite.vendor : '';
      const token = uuid().replace(/-/g, '');
      const id = uuid();
      db.prepare('INSERT INTO collectors (id, name, phone, token, created_at, vendor) VALUES (?,?,?,?,?,?)')
        .run(id, name, String(b.phone || ''), token, now(), vendor);
      return send(res, 200, {
        token,
        vendor,
        collector: { id, name, phone: String(b.phone || ''), vendor },
      });'''
assert old2 in t
t = t.replace(old2, new2)

# 2.3 邀请码管理接口：固定码增删查
old3 = '''    // 邀请码管理（查看器用，需 adminKey）
    if (p === '/api/invite') {'''
new3 = '''    // 校验邀请码（App 用，公开）：返回这个码属于哪个厂商
    if (req.method === 'GET' && p === '/api/invite/check') {
      const code = u.searchParams.get('code') || '';
      const row = findInvite(code);
      if (!row) return send(res, 200, { ok: false, vendor: '' });
      return send(res, 200, { ok: true, vendor: row.vendor, note: row.note || '' });
    }

    // 固定邀请码列表（查看器用，需 adminKey）
    if (p === '/api/invites') {
      if (!adminOk(req)) throw new ApiError(403, 'FORBIDDEN', '管理口令不正确');
      if (req.method === 'GET') {
        const rows = db.prepare('SELECT code, vendor, note, created_at, disabled FROM invites ORDER BY created_at DESC').all();
        return send(res, 200, { items: rows });
      }
      if (req.method === 'POST') {
        const b = await readJson(req);
        const code = String(b.code || '').trim().toUpperCase();
        const vendor = String(b.vendor || '').trim();
        if (!code) throw bad('请填写邀请码');
        if (!vendor) throw bad('请填写厂商名称');
        db.prepare('INSERT INTO invites (code, vendor, note, created_at, disabled) VALUES (?,?,?,?,0) ' +
                   'ON CONFLICT(code) DO UPDATE SET vendor = excluded.vendor, note = excluded.note, disabled = 0')
          .run(code, vendor, String(b.note || ''), now());
        return send(res, 200, { ok: true, code, vendor });
      }
      if (req.method === 'DELETE') {
        const code = String(u.searchParams.get('code') || '').trim().toUpperCase();
        db.prepare('DELETE FROM invites WHERE UPPER(code) = ?').run(code);
        return send(res, 200, { ok: true });
      }
    }

    // 旧的单一邀请码（保留兼容）
    if (p === '/api/invite') {'''
assert old3 in t
t = t.replace(old3, new3)

# 2.4 健康检查里带上固定码数量
t = t.replace("        inviteRequired: !!currentInvite().trim(),",
              "        inviteRequired: !!currentInvite().trim(),\n        inviteCodes: db.prepare('SELECT COUNT(*) c FROM invites WHERE disabled = 0').get().c,")

io.open(p2, 'w', encoding='utf-8').write(t)
print('server.mjs 邀请码接口已加')
