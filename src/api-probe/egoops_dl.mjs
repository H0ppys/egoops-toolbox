// 下载 EgoOps 前端静态资源（用于接口逆向）
import fs from 'node:fs';
import path from 'node:path';

const BASE = 'https://s3.meituan.net/static-prod01/ws-assets/com.sankuai.mrobo.egoops.web/Z8cz8AQFmuE21mTkoKIWF/assets/';
const OUT = path.join(process.cwd(), 'egoops_web');
fs.mkdirSync(OUT, { recursive: true });

const names = process.argv.slice(2);
for (const n of names) {
  const url = BASE + n;
  const res = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0' } });
  if (!res.ok) { console.log('FAIL', res.status, n); continue; }
  const text = await res.text();
  fs.writeFileSync(path.join(OUT, n), text, 'utf8');
  console.log('OK', String(text.length).padStart(8), n);
}
