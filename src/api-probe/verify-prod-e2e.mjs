// 线上主功能端到端校验（自动清理）：登录 → 建点+任务 → 分片上传 → 列表 → 下载 → 删除
const BASE = (process.argv[2] || 'http://<FILL_ME>/relay').replace(/\/+$/, '');
let token = '';
const log = (...a) => console.log('  ', ...a);

async function api(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const t = await res.text();
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status} ${t.slice(0, 200)}`);
  return t ? JSON.parse(t) : {};
}

(async () => {
  console.log(`\n目标：${BASE}\n`);

  console.log('1) 健康检查');
  const h = await fetch(BASE + '/api/health').then(r => r.json());
  log('ok=', h.ok, '| 邀请码', h.inviteRequired ? '开启' : '关闭', '| 采集点', h.sites, '| 文件', h.files);

  console.log('2) 登录（不带邀请码）');
  const l = await api('POST', '/api/auth/login', { name: '验收-' + new Date().toISOString().slice(11, 19) });
  token = l.token;
  log('token 长度', token.length);

  console.log('3) 建采集点 + 2 个任务');
  const created = await api('POST', '/api/sites', {
    name: '【验收】' + Date.now(),
    address: '验收地址',
    note: '自动删除',
    tasks: [{ name: '任务1' }, { name: '任务2' }],
  });
  const site = created.site;
  log('site_id', site.id, '| 任务', site.tasks.length);

  console.log('4) 分片上传（任务1 照片 + 任务2 视频）');
  async function upload(taskId, name, buf, kind, ct) {
    const init = await api('POST', `/api/sites/${site.id}/uploads`, { task_id: taskId, filename: name, content_type: ct, size: buf.length, kind });
    for (let i = 0; i < init.total; i++) {
      const part = buf.subarray(i * init.chunk_size, Math.min((i + 1) * init.chunk_size, buf.length));
      const r = await fetch(`${BASE}/api/uploads/${init.upload_id}/${i}`, {
        method: 'PUT', headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/octet-stream' }, body: part,
      });
      if (!r.ok) throw new Error('chunk ' + i + ' -> ' + r.status);
    }
    return api('POST', `/api/uploads/${init.upload_id}/complete`, {});
  }
  const buf = Buffer.alloc(1024 * 1024, 0x41);
  const f1 = await upload(site.tasks[0].id, 'IMG_test.jpg', buf, 'photo', 'image/jpeg');
  const f2 = await upload(site.tasks[1].id, 'VID_test.mp4', buf, 'video', 'video/mp4');
  log('文件1', f1.file.id.slice(0, 8), f1.file.size, '字节 | 文件2', f2.file.id.slice(0, 8), f2.file.size, '字节');

  console.log('5) 列表 + 详情');
  const list = await api('GET', '/api/sites');
  const mine = list.items.find(s => s.id === site.id);
  log('列表可见:', !!mine, '| 任务数', mine.task_count, '| 文件数', mine.file_count);
  const detail = await api('GET', '/api/sites/' + site.id);
  log('详情任务:', detail.tasks.map(t => `${t.name}(照片${t.photos.length}/视频${t.videos.length})`).join(', '));

  console.log('6) 下载校验');
  const dl = await fetch(BASE + f1.file.url);
  const got = Buffer.from(await dl.arrayBuffer());
  log('下载', got.length, '字节 | 一致', got.equals(buf));

  console.log('7) 清理');
  const del = await api('DELETE', '/api/sites/' + site.id);
  const after = await api('GET', '/api/sites');
  log('删除', del.status, '| 剩余采集点', after.items.length, '| 剩余文件', (await fetch(BASE + '/api/health').then(r => r.json())).files);

  const ok = got.equals(buf) && detail.tasks.length === 2 && !after.items.find(s => s.id === site.id);
  console.log(ok ? '\n✅ 线上主功能正常（已清理测试数据）' : '\n❌ 校验失败');
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error('\n❌ 失败:', e.message); process.exit(1); });
