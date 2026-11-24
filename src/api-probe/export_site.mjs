import fs from 'node:fs';

const B = 'http://<FILL_ME>/relay';
const login = await (await fetch(B + '/api/auth/login', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '填表' }),
})).json();
const list = await (await fetch(B + '/api/sites', {
  headers: { Authorization: 'Bearer ' + login.token },
})).json();
const s = list.items.find(x => x.name === '美宜佳') || list.items[0];
const d = await (await fetch(B + '/api/sites/' + s.id, {
  headers: { Authorization: 'Bearer ' + login.token },
})).json();
fs.writeFileSync('tmp_site.json', JSON.stringify(d, null, 1));
console.log('导出:', d.name, '| 任务', (d.tasks || []).length, '| 场景', d.scene_label, '| 面积', d.area);
