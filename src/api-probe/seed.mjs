// 造测试数据：采集点 + 2 个任务，每个任务传照片/视频（不删除）
const BASE = (process.argv[2] || 'http://127.0.0.1:18090').replace(/\/+$/, '');
let token = '';

async function api(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const t = await res.text();
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status} ${t}`);
  return JSON.parse(t || '{}');
}

async function put(uploadId, i, buf) {
  const r = await fetch(`${BASE}/api/uploads/${uploadId}/${i}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/octet-stream', Authorization: 'Bearer ' + token },
    body: buf,
  });
  if (!r.ok) throw new Error('chunk ' + i + ' -> ' + r.status);
}

async function upload(siteId, taskId, filename, buf, kind, contentType) {
  const body = { filename, content_type: contentType, size: buf.length, kind };
  if (taskId) body.task_id = taskId;
  const init = await api('POST', `/api/sites/${siteId}/uploads`, body);
  for (let i = 0; i < init.total; i++) {
    await put(init.upload_id, i, buf.subarray(i * init.chunk_size, Math.min((i + 1) * init.chunk_size, buf.length)));
  }
  return api('POST', `/api/uploads/${init.upload_id}/complete`, {});
}

const login = await api('POST', '/api/auth/login', { name: '张三', phone: '', invite: '' });
token = login.token;

const created = await api('POST', '/api/sites', {
  name: '湛江盛宴超市（示例）-' + Date.now(),
  address: '广东省湛江市赤坎区人民大道 88 号',
  note: '演示数据：两个任务',
  tasks: [{ name: '任务1-门头与全景' }, { name: '任务2-操作台与动作' }],
});
const site = created.site;
const t1 = site.tasks[0].id;
const t2 = site.tasks[1].id;

const pad = (n) => Buffer.alloc(n, 0x5a);
await upload(site.id, t1, 'IMG_door.jpg', pad(320 * 1024), 'photo', 'image/jpeg');
await upload(site.id, t1, 'VID_site.mp4', pad(2 * 1024 * 1024), 'video', 'video/mp4');
await upload(site.id, t2, 'IMG_counter.jpg', pad(480 * 1024), 'photo', 'image/jpeg');
await upload(site.id, t2, 'VID_action.mp4', pad(3 * 1024 * 1024), 'video', 'video/mp4');

const detail = await api('GET', '/api/sites/' + site.id);
console.log('site:', detail.name, '| 任务', detail.tasks.length, '| 文件', detail.file_count, '| 字节', detail.bytes);
for (const t of detail.tasks) console.log('  -', t.name, '照片', t.photos.length, '视频', t.videos.length);
