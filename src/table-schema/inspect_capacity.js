'use strict';
const { execFileSync } = require('node:child_process');
const L = '/usr/local/bin/lark-cli';
const BASE = "<FILL_ME>";

function run(args) {
  try {
    const out = execFileSync(L, args, {
      encoding: 'utf8', timeout: 90000,
      env: { ...process.env, HOME: '/root' }, stdio: ['ignore', 'pipe', 'pipe'],
    });
    return JSON.parse(out);
  } catch (e) {
    const buf = e.stderr || e.message || e;
    return { ok: false, err: String(Buffer.isBuffer(buf) ? buf.toString('utf8') : buf).slice(0, 300) };
  }
}

const tables = [
  ['KWQX-广州-设备产能统计', 'tblorr4LiWR9nlBZ'],
  ['KWQX-海南-设备产能统计', 'tblkIvPEw3MFI6oP'],
  ['ZBL-广州-设备产能统计', 'tblkkXbmtJWBc5MQ'],
  ['MT-SY-设备产能统计', 'tblf0wwdCou84MBw'],
  ['具采项目产能汇总', 'tbljA6GP9vi9zXYI'],
  ['项目汇总', 'tblQWzPcIuZ7VfoR'],
];

function flat(v) {
  if (v == null) return '';
  if (Array.isArray(v)) return v.map(x => (x && typeof x === 'object') ? (x.name || x.text || x.value || '') : String(x)).filter(Boolean).join('/');
  if (typeof v === 'object') { if (v.value != null) return flat(v.value); return v.name || v.text || ''; }
  return String(v);
}

for (const [label, table] of tables) {
  const r = run(['base', '+record-list', '--base-token', BASE, '--table-id', table, '--limit', '200', '--format', 'json', '--as', 'bot']);
  if (!r.ok) { console.log(`\n## ${label}: 失败 ${r.err}`); continue; }
  const names = r.data.fields || [];
  const rows = r.data.data || [];
  const di = (() => { let i = names.indexOf('作业日期'); if (i < 0) i = names.findIndex(n => n.includes('日期')); return i; })();
  const dates = [...new Set(rows.map(x => flat(x[di]).slice(0, 10)).filter(Boolean))].sort();
  console.log(`\n## ${label} [${table}] 行数=${rows.length}`);
  console.log('   字段:', names.join('、'));
  console.log('   日期:', dates.length ? `${dates[0]} ~ ${dates[dates.length - 1]}（${dates.length} 个日期，最近: ${dates.slice(-4).join(',')}）` : '无日期字段/无数据');
  for (const row of rows.slice(0, 2)) {
    const o = {};
    names.forEach((n, i) => { const v = flat(row[i]); if (v !== '') o[n] = v; });
    console.log('   样例:', JSON.stringify(o).slice(0, 420));
  }
}
