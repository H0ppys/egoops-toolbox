import fs from 'node:fs';

const B = 'http://<FILL_ME>/relay';
const login = await (await fetch(B + '/api/auth/login', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '下载素材' }),
})).json();
const h = { Authorization: 'Bearer ' + login.token };
const list = await (await fetch(B + '/api/sites', { headers: h })).json();
const site = list.items.find(x => x.name === '美宜佳') || list.items[0];
const d = await (await fetch(B + '/api/sites/' + site.id, { headers: h })).json();
const photo = (d.tasks[0].photos || [])[0];
const video = (d.tasks[0].videos || [])[0];
fs.mkdirSync('docs/media', { recursive: true });
for (const [f, name] of [[photo, 'photo.jpg'], [video, 'video.mp4']]) {
  if (!f) continue;
  const r = await fetch(B + '/files/' + f.id);
  const buf = Buffer.from(await r.arrayBuffer());
  fs.writeFileSync('docs/media/' + name, buf);
  console.log(name, (buf.length / 1048576).toFixed(2) + 'MB');
}
