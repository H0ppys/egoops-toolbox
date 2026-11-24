'use strict';
const { execFileSync } = require('node:child_process');
const L = '/usr/local/bin/lark-cli';
const BASE = "<FILL_ME>";

function run(args) {
  try {
    const out = execFileSync(L, args, {
      encoding: 'utf8', timeout: 90000,
      env: { ...process.env, HOME: '/root' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return JSON.parse(out);
  } catch (e) {
    const buf = e.stderr || e.message || e;
    return { ok: false, err: String(Buffer.isBuffer(buf) ? buf.toString('utf8') : buf).slice(0, 400) };
  }
}

for (const [label, table] of [['项目生产与日报', 'tblnGVVPt6RYmnVV'], ['每日开机播报', 'tblHjAuEdhi901vN']]) {
  for (const as of ['bot', 'user']) {
    const r = run(['base', '+record-list', '--base-token', BASE, '--table-id', table,
                   '--limit', '200', '--format', 'json', '--as', as]);
    if (!r.ok) { console.log(`${label} --as ${as}: 失败 ${r.err.slice(0, 150)}`); continue; }
    const names = r.data.fields || [];
    const rows = r.data.data || [];
    const dix = names.findIndex(n => n.includes('日期'));
    const dates = [...new Set(rows.map(x => String(x[dix] ?? '').slice(0, 10)).filter(Boolean))].sort();
    console.log(`${label} --as ${as}: OK 行数=${rows.length} 日期范围=${dates[0] || '-'} ~ ${dates[dates.length - 1] || '-'} 最近3个日期=${dates.slice(-3).join(',')}`);
  }
}
