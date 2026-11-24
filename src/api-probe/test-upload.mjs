// 分片上传端到端测试：登录 → 建采集点 → 断点 → 续传 → 合并 → 下载校验
const BASE = (process.argv[2] || 'http://127.0.0.1:18090').replace(/\/+$/, '');
let token = '';

async function api(method, path, body, opts = {}) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok && !opts.allowFail) throw new Error(`${method} ${path} -> ${res.status} ${JSON.stringify(data)}`);
  return { status: res.status, data };
}
const log = (...a) => console.log('  ', ...a);
const mb = (n) => (n / 1048576).toFixed(1) + 'MB';

function makeVideo(size) {
  const b = Buffer.alloc(size);
  for (let i = 0; i < size; i += 4096) b.writeUInt32LE((i / 4096) | 0, i);
  b.write('ftypisom', 4, 'binary');
  return b;
}

async function putChunk(uploadId, index, part) {
  return fetch(`${BASE}/api/uploads/${uploadId}/${index}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/octet-stream', Authorization: 'Bearer ' + token },
    body: part,
  });
}

(async () => {
  console.log('1) 登录');
  const l = await api('POST', '/api/auth/login', { name: '上传测试员', phone: '', invite: '' });
  token = l.data.token;
  log('token 长度', token.length);

  console.log('2) 建采集点');
  const s = await api('POST', '/api/sites', { name: '分片测试点-' + Date.now(), address: '广东省广州市测试路 9 号', note: '验证断点续传' });
  const site = s.data.site;
  log('site_id', site.id, '| existing', s.data.existing);

  console.log('3) 建上传会话（12MB 假视频）');
  const buf = makeVideo(12 * 1024 * 1024);
  const init = await api('POST', `/api/sites/${site.id}/uploads`, { filename: 'VID_test.mp4', content_type: 'video/mp4', size: buf.length, kind: 'video' });
  const { upload_id, chunk_size, total } = init.data;
  log('upload_id', upload_id, '| chunk', mb(chunk_size), '| total', total);

  console.log('4) 只传前 2 片，模拟断网');
  for (let i = 0; i < 2; i++) {
    const part = buf.subarray(i * chunk_size, Math.min((i + 1) * chunk_size, buf.length));
    const r = await putChunk(upload_id, i, part);
    log(`  片 ${i} -> ${r.status}`);
    if (r.status !== 200) throw new Error(`片 ${i} 上传失败: ${r.status}`);
  }
  const st = await api('GET', `/api/uploads/${upload_id}`);
  log('服务端已收到分片', JSON.stringify(st.data.received), '/', total);

  console.log('5) 直接 complete 应被拒');
  const early = await api('POST', `/api/uploads/${upload_id}/complete`, {}, { allowFail: true });
  log('状态码', early.status, '| 缺片', JSON.stringify(early.data?.error?.detail));

  console.log('6) 续传剩余分片');
  const have = new Set(st.data.received);
  for (let i = 0; i < total; i++) {
    if (have.has(i)) continue;
    const part = buf.subarray(i * chunk_size, Math.min((i + 1) * chunk_size, buf.length));
    const r = await putChunk(upload_id, i, part);
    if (r.status !== 200) throw new Error(`片 ${i} 失败 ${r.status}`);
  }
  log('已补齐');

  console.log('7) 合并');
  const done = await api('POST', `/api/uploads/${upload_id}/complete`, {});
  log('file', JSON.stringify(done.data.file));

  console.log('8) 下载并校验字节一致');
  const dl = await fetch(BASE + done.data.file.url);
  const got = Buffer.from(await dl.arrayBuffer());
  log('下载', mb(got.length), '| 一致:', got.length === buf.length && got.equals(buf));

  console.log('9) Range 请求（视频拖动进度条）');
  const rg = await fetch(BASE + done.data.file.url, { headers: { Range: 'bytes=100-199' } });
  const rgBuf = Buffer.from(await rg.arrayBuffer());
  log('状态码', rg.status, '| 长度', rgBuf.length, '| 内容一致:', rgBuf.equals(buf.subarray(100, 200)));

  console.log('10) 采集点详情');
  const detail = await api('GET', `/api/sites/${site.id}`);
  log('照片', detail.data.photos.length, '| 视频', detail.data.videos.length, '| 字节', mb(detail.data.bytes));

  console.log('11) 删除文件');
  const del = await api('DELETE', `/api/files/${done.data.file.id}`);
  const after = await api('GET', `/api/sites/${site.id}`);
  log('删除', del.status, '| 剩余文件', after.data.file_count);

  const ok = got.length === buf.length && got.equals(buf) && rgBuf.equals(buf.subarray(100, 200)) && after.data.file_count === 0;
  console.log(ok ? '\n✅ 分片上传全链路通过' : '\n❌ 校验失败');
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error('\n❌ 失败:', e.message); process.exit(1); });
