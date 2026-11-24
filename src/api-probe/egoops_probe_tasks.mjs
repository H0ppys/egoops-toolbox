// 深挖 申请采集点 相关契约：任务结构 + 媒体业务类型
import fs from 'node:fs';

const API = 'https://mrobo.uav.meituan.com/egoops';
const tok = JSON.parse(fs.readFileSync('egoops_token.json', 'utf8')).access_token;
const H = { Authorization: `Bearer ${tok}`, Accept: 'application/json, text/plain, */*', 'Accept-Language': 'zh-CN' };

async function get(p) {
  const r = await fetch(API + p, { headers: H });
  const t = await r.text();
  try { return { s: r.status, j: JSON.parse(t) }; } catch { return { s: r.status, t }; }
}

// 1) 取一个 draft/submitted 的采集点，看其任务结构
const list = await get('/api/v1/task-sets?work_mode=site_organization&review_status=draft,submitted&page=1&size=1');
console.log('LIST', list.s, JSON.stringify(list.j?.records?.[0] ?? list.j).slice(0, 800));
const site = list.j?.records?.[0];
if (site) {
  const ts = await get(`/api/v1/task-sets/${site.task_set_id}`);
  console.log('\nTASK-SET', ts.s, JSON.stringify(ts.j).slice(0, 1500));
  const tasks = await get(`/api/v1/task-sets/${site.task_set_id}/tasks?include_stats=false&include_assignments=false`);
  console.log('\nTASKS', tasks.s, JSON.stringify(tasks.j).slice(0, 2500));
  const t0 = tasks.j?.records?.[0];
  if (t0) {
    const td = await get(`/api/v1/tasks/${t0.task_id}?include_stats=true`);
    console.log('\nTASK-DETAIL', td.s, JSON.stringify(td.j).slice(0, 2500));
  }
}

// 2) 采集点概览接口（前端 detail 页用）
const sample = await get('/api/v1/task-sets?work_mode=site_organization&review_status=approved&page=1&size=1');
const sid = sample.j?.records?.[0]?.task_set_id;
if (sid) {
  const ov = await get(`/api/v1/collection-sites/${sid}/overview`);
  console.log('\nOVERVIEW', ov.s, JSON.stringify(ov.j).slice(0, 1500));
}
