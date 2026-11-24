'use strict';
const { execFileSync } = require('node:child_process');
const L = '/usr/local/bin/lark-cli';

function run(args) {
  try {
    const out = execFileSync(L, args, {
      encoding: 'utf8', timeout: 60000,
      env: { ...process.env, HOME: '/root' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return JSON.parse(out);
  } catch (e) {
    return { ok: false, err: String(e.stderr || e.message || e).slice(0, 200) };
  }
}

const targets = [
  ['具采-每日开机播报', "<FILL_ME>", 'tblHjAuEdhi901vN'],
  ['具采-项目生产与日报', "<FILL_ME>", 'tblnGVVPt6RYmnVV'],
  ['MT_SY-区域有效开机率统计', "<FILL_ME>", 'tble92dif1M6t0HU'],
  ['KWQX-区域有效开机率统计', "<FILL_ME>", 'tblZmZcB7VEYC025'],
];

for (const [label, base, table] of targets) {
  console.log('\n' + '='.repeat(70));
  console.log('##', label, `[${base} / ${table}]`);
  const f = run(['base', '+field-list', '--base-token', base, '--table-id', table]);
  if (!f.ok) { console.log('  字段读取失败:', f.err); continue; }
  console.log('  字段:', (f.data.fields || []).map(x => `${x.name}(${x.type})`).join('、'));

  const r = run(['base', '+record-list', '--base-token', base, '--table-id', table, '--limit', '3']);
  if (!r.ok) { console.log('  记录读取失败:', r.err); continue; }
  const names = r.data.fields || [];
  for (const row of (r.data.data || [])) {
    const o = {};
    names.forEach((n, i) => {
      let v = row[i];
      if (v && typeof v === 'object' && Array.isArray(v.value)) v = v.value.join('/');
      if (v !== '' && v != null) o[n] = v;
    });
    console.log('  样例:', JSON.stringify(o).slice(0, 400));
  }
}
