'use strict';
const { execFileSync } = require('node:child_process');
const L = '/usr/local/bin/lark-cli';
const BOT = '<FILL_ME>';

function run(args) {
  try {
    const out = execFileSync(L, args, {
      encoding: 'utf8', timeout: 60000,
      env: { ...process.env, HOME: '/root' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return JSON.parse(out);
  } catch (e) {
    const buf = e.stderr || e.message || e;
    return { ok: false, err: String(Buffer.isBuffer(buf) ? buf.toString('utf8') : buf).slice(0, 300) };
  }
}

const bases = [
  ['当前配置的（3表）采集员作业数据统计管理', "<FILL_ME>"],
  ['具采项目资料与生产管理（内部）14表', "<FILL_ME>"],
  ['具采场景资源管理库 5表', "<FILL_ME>"],
  ['MT_SY 项目数据汇总 13表', "<FILL_ME>"],
  ['KWQX 项目数据汇总 14表', "<FILL_ME>"],
];

for (const [label, tok] of bases) {
  console.log('\n##', label, `[${tok}]`);
  const r = run(['drive', '+member-list', '--token', tok, '--type', 'bitable']);
  if (!r.ok) { console.log('  读取失败:', r.err); continue; }
  const items = r.data.items || r.data.members || [];
  const app = items.find(m => m.member_id === BOT || m.type === 'app' || m.member_type === 'openapp');
  console.log(`  协作者数=${items.length}；CLI 应用${app ? '在列' : '不在列'}`);
  for (const m of items.slice(0, 12)) {
    console.log(`   - ${m.member_type || m.type}/${m.perm || m.permission}: ${m.name || m.member_id}`);
  }
}
