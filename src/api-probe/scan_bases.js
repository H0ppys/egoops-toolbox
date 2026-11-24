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
    return { ok: false, err: String(e.stderr || e.message || e).slice(0, 160) };
  }
}

const queries = ['具采', '开机率', '采集', '作业', '生产'];
const cands = new Map();
for (const q of queries) {
  const r = run(['drive', '+search', '--query', q, '--page-size', '20']);
  if (!r.ok) { console.log(`[search ${q}] 失败: ${r.err}`); continue; }
  for (const it of r.data.results || []) {
    const m = it.result_meta || {};
    if (m.doc_types !== 'BITABLE') continue;
    const title = String(it.title_highlighted || '').replace(/<\/?h>/g, '');
    cands.set(m.token, { title, owner: m.owner_name, url: m.url });
  }
}
console.log('候选 Base 数量:', cands.size);

for (const [tok, meta] of cands) {
  const t = run(['base', '+table-list', '--base-token', tok]);
  if (!t.ok) { console.log(`\n## ${meta.title} [${tok}] —— 无权限/失败: ${t.err}`); continue; }
  const tables = t.data.tables || [];
  console.log(`\n## ${meta.title} [${tok}] owner=${meta.owner} 表数=${tables.length}`);
  for (const tb of tables) {
    console.log(`   - ${tb.name}  (${tb.id}, ${tb.records_count} 条)`);
  }
}
