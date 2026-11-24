import fs from 'node:fs';

const B = 'http://<FILL_ME>/relay';
const login = await (await fetch(B + '/api/auth/login', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '查视频' }),
})).json();
const h = { Authorization: 'Bearer ' + login.token };
const list = await (await fetch(B + '/api/sites', { headers: h })).json();

for (const s of list.items) {
  const d = await (await fetch(B + '/api/sites/' + s.id, { headers: h })).json();
  for (const t of d.tasks || []) {
    for (const v of t.videos || []) {
      const r = await fetch(B + '/files/' + v.id);
      const buf = Buffer.from(await r.arrayBuffer());
      const head = buf.subarray(0, 24).toString('hex');
      const brand = buf.subarray(4, 12).toString('latin1');
      const file = `tmp_video_${v.id.slice(0, 6)}.mp4`;
      fs.writeFileSync(file, buf);
      // 找 moov / mdat
      const hasMoov = buf.includes(Buffer.from('moov'));
      const hasMdat = buf.includes(Buffer.from('mdat'));
      console.log(`${s.name} | ${v.filename} | ${(buf.length / 1048576).toFixed(2)}MB | brand=${JSON.stringify(brand)} | moov=${hasMoov} mdat=${hasMdat} | ${file}`);
    }
  }
}
