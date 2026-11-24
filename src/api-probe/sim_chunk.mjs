// 验证分片上传（>4MB 多片）与断点续传查询
import fs from 'node:fs';

const BASE = 'https://<FILL_ME>/relay';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const json = async (p, opt) => {
  const r = await fetch(BASE + p, opt);
  const t = await r.text();
  if (!r.ok) throw new Error(`${p} -> ${r.status} ${t.slice(0, 160)}`);
  return t ? JSON.parse(t) : {};
};

(async () => {
  const siteId = fs.readFileSync('sim/site_id.txt', 'utf-8').trim();
  const login = await json('/api/auth/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: '分片测试', invite: 'zjmeiyi' }),   // 故意小写
  });
  console.log('小写邀请码登录 -> 记录为', login.invite);
  const H = { 'Content-Type': 'application/json', Authorization: 'Bearer ' + login.token };

  const buf = fs.readFileSync('sim/video_h264.mp4');
  const big = Buffer.concat([buf, buf, buf, buf, buf]);   // 约 7.5MB，至少 2 片
  console.log('文件大小', (big.length / 1048576).toFixed(2) + 'MB');

  const init = await json('/api/sites/' + siteId + '/uploads', {
    method: 'POST', headers: H,
    body: JSON.stringify({ filename: 'big_video.mp4', kind: 'video', size: big.length,
                           content_type: 'video/mp4' }),
  });
  console.log('初始化: upload_id=', init.upload_id.slice(0, 8), '分片数=', init.total, '片大小=', init.chunk_size);

  // 只传第 0 片，然后查断点
  const chunk = init.chunk_size;
  let r = await fetch(`${BASE}/api/uploads/${init.upload_id}/0`, {
    method: 'PUT', headers: { Authorization: 'Bearer ' + login.token, 'Content-Type': 'application/octet-stream' },
    body: big.subarray(0, chunk),
  });
  console.log('传第 0 片:', r.status);
  const st = await json(`/api/uploads/${init.upload_id}`, { headers: { Authorization: 'Bearer ' + login.token } });
  console.log('断点查询: 已收', st.received, '/ 共', st.total);

  // 续传剩余
  for (let i = 1; i < init.total; i++) {
    const part = big.subarray(i * chunk, Math.min((i + 1) * chunk, big.length));
    r = await fetch(`${BASE}/api/uploads/${init.upload_id}/${i}`, {
      method: 'PUT', headers: { Authorization: 'Bearer ' + login.token, 'Content-Type': 'application/octet-stream' },
      body: part,
    });
    if (!r.ok) throw new Error('分片 ' + i + ' 失败');
  }
  const done = await json(`/api/uploads/${init.upload_id}/complete`, {
    method: 'POST', headers: { Authorization: 'Bearer ' + login.token, 'Content-Type': 'application/json' }, body: '{}',
  });
  console.log('合并完成: 文件 id=', done.file.id.slice(0, 8), '大小=', (done.file.size / 1048576).toFixed(2) + 'MB');
  console.log('大小一致:', done.file.size === big.length);
})().catch((e) => { console.error('失败:', e.message); process.exit(1); });
