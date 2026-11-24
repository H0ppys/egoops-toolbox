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
    let msg = '';
    if (e.stderr) msg = Buffer.isBuffer(e.stderr) ? e.stderr.toString('utf8') : String(e.stderr);
    else msg = String(e.message || e);
    return { ok: false, err: msg.slice(0, 500) };
  }
}

const targets = [
  ['每日开机播报', "<FILL_ME>", 'tblHjAuEdhi901vN'],
  ['项目生产与日报', "<FILL_ME>", 'tblnGVVPt6RYmnVV'],
  ['MT区域有效开机率', "<FILL_ME>", 'tble92dif1M6t0HU'],
];

for (const [label, base, table] of targets) {
  console.log('\n##', label);
  const r = run(['base', '+record-list', '--base-token', base, '--table-id', table, '--limit', '3', '--format', 'json']);
  if (!r.ok) {
    console.log('  失败:', r.err || JSON.stringify(r).slice(0, 500));
    continue;
  }
  const names = r.data.fields || [];
  console.log('  字段:', names.join('、'));
  for (const row of (r.data.data || [])) {
    const o = {};
    names.forEach((n, i) => {
      let v = row[i];
      if (v && typeof v === 'object' && Array.isArray(v.value)) v = v.value.join('/');
      if (v !== '' && v != null) o[n] = v;
    });
    console.log('  样例:', JSON.stringify(o).slice(0, 500));
  }
}
