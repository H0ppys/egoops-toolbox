import fs from 'node:fs';

const B = 'http://<FILL_ME>/relay';
const name = process.argv[2] || '方法';
const login = await (await fetch(B + '/api/auth/login', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '导出' }),
})).json();
const h = { Authorization: 'Bearer ' + login.token };
const list = await (await fetch(B + '/api/sites', { headers: h })).json();
const s = list.items.find(x => x.name === name);
if (!s) { console.log('找不到', name); process.exit(1); }
const d = await (await fetch(B + '/api/sites/' + s.id, { headers: h })).json();
const out = 'tmp_site_' + name + '.json';
fs.writeFileSync(out, JSON.stringify(d, null, 1));
console.log(out, '| 地址', JSON.stringify(d.address), '| 任务', (d.tasks || []).length);
