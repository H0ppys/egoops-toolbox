// 只读探查 EgoOps 采集点相关接口的返回结构（GET）
import fs from 'node:fs';

const API = 'https://mrobo.uav.meituan.com/egoops';
const tok = JSON.parse(fs.readFileSync('egoops_token.json', 'utf8')).access_token;

async function get(path) {
  const res = await fetch(API + path, {
    headers: {
      Authorization: `Bearer ${tok}`,
      Accept: 'application/json, text/plain, */*',
      'Accept-Language': 'zh-CN',
      'User-Agent': 'Mozilla/5.0',
    },
  });
  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = null; }
  return { status: res.status, json, text };
}

const targets = [
  '/api/v1/users/me',
  '/api/v1/tet-snapshots/active',
  '/api/v1/task-sets?work_mode=site_organization&review_status=draft,submitted,rejected,approved&page=1&size=2',
  '/api/v1/collection-sites/' + 'invalid/overview',
];

const out = {};
for (const t of targets) {
  const r = await get(t);
  out[t] = r.status;
  const s = r.json ? JSON.stringify(r.json) : r.text.slice(0, 500);
  console.log(`\n### ${t} -> ${r.status} (${s.length} chars)`);
  console.log(s.slice(0, 3000));
}
