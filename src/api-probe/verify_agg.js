'use strict';
const { execFileSync } = require('node:child_process');
const L = '/usr/local/bin/lark-cli';
const BASE = "<FILL_ME>";

function run(args) {
  const out = execFileSync(L, args, {
    encoding: 'utf8', timeout: 90000,
    env: { ...process.env, HOME: '/root' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  return JSON.parse(out);
}
function flat(v) {
  if (v == null) return '';
  if (Array.isArray(v)) return v.map(x => (x && typeof x === 'object') ? (x.name || x.text || '') : String(x)).filter(Boolean).join('/');
  if (typeof v === 'object') { if (v.value != null) return flat(v.value); return v.name || v.text || ''; }
  return String(v);
}

const r = run(['base', '+record-list', '--base-token', BASE, '--table-id', 'tblf0wwdCou84MBw',
               '--limit', '200', '--format', 'json', '--as', 'bot']);
const names = r.data.fields;
const rows = r.data.data;
const iDate = names.indexOf('作业日期');
const iEff = names.indexOf('有效开机');
const iDur = names.indexOf('设备采集时长（小时）');

for (const d of ['2026-11-18', '2026-11-17']) {
  const rs = rows.filter(x => flat(x[iDate]).slice(0, 10) === d);
  const sum = rs.reduce((a, x) => a + (Number(flat(x[iDur])) || 0), 0);
  const eff = rs.filter(x => flat(x[iEff]).includes('有效')).length;
  console.log(`${d}: 明细行数=${rs.length} 有效开机=${eff} 时长合计=${sum.toFixed(2)}h 均值=${(sum / (rs.length || 1)).toFixed(2)}h`);
  console.log('   设备:', rs.map(x => flat(x[names.indexOf('开机设备')])).join(','));
}
