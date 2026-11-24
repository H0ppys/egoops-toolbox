// 模拟安卓 App 的完整上传：登录(带邀请码) → 建采集点 → 建任务 → 分片上传 8 个文件 → 校验
import fs from 'node:fs';
import path from 'node:path';

const BASE = process.env.RELAY || 'https://<FILL_ME>/relay';
const INVITE = 'ZJMEIYI';
const NAME = '模拟测试店-勿用';
const ADDRESS = '广东省湛江市赤坎区人民大道88号';
const CHUNK = 4 * 1024 * 1024;

const req = (p, opt = {}) => fetch(BASE + p, opt);

async function json(p, opt) {
  const r = await req(p, opt);
  const t = await r.text();
  if (!r.ok) throw new Error(`${p} -> ${r.status} ${t.slice(0, 200)}`);
  return t ? JSON.parse(t) : {};
}

async function uploadFile(token, siteId, taskId, file, kind) {
  const buf = fs.readFileSync(file);
  const init = await json('/api/sites/' + siteId + '/uploads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
    body: JSON.stringify({
      filename: path.basename(file), kind, size: buf.length,
      content_type: kind === 'photo' ? 'image/jpeg' : 'video/mp4',
      task_id: taskId,
    }),
  });
  const uploadId = init.upload_id;
  const total = init.total;
  let sent = 0;
  for (let i = 0; i < total; i++) {
    const part = buf.subarray(i * CHUNK, Math.min((i + 1) * CHUNK, buf.length));
    const r = await req(`/api/uploads/${uploadId}/${i}`, {
      method: 'PUT', headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/octet-stream' }, body: part,
    });
    if (!r.ok) throw new Error('分片失败 ' + i + ' ' + r.status);
    sent += part.length;
  }
  const done = await json(`/api/uploads/${uploadId}/complete`, {
    method: 'POST', headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' }, body: '{}',
  });
  console.log(`   上传 ${path.basename(file)} ${(buf.length / 1048576).toFixed(2)}MB (${total} 片) -> ${done.file.id.slice(0, 8)}`);
  return done.file;
}

(async () => {
  console.log('1) 登录（带邀请码）');
  const login = await json('/api/auth/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: '模拟采集员', invite: INVITE }),
  });
  console.log('   invite =', login.invite, '| token =', login.token.slice(0, 8) + '…');
  const H = { 'Content-Type': 'application/json', Authorization: 'Bearer ' + login.token };

  console.log('2) 建采集点（模拟 App 的请求体）');
  const site = await json('/api/sites', {
    method: 'POST', headers: H,
    body: JSON.stringify({
      name: NAME, address: ADDRESS, area: 85,
      scene: 'restaurant/餐厅', scene_label: '餐馆 / 餐厅',
      invite: INVITE,
      tasks: [
        { name: '采集点-门头与全景', area: '' },
        { name: '捡垃圾', area: '饮料区' },
      ],
    }),
  });
  const siteId = site.site.id;
  console.log('   site =', siteId.slice(0, 8), '| 上限覆盖', site.replaced, '| invite =', site.site.invite);

  const detail = await json('/api/sites/' + siteId, { headers: { Authorization: 'Bearer ' + login.token } });
  const t0 = detail.tasks[0];
  const t1 = detail.tasks[1];
  console.log('   任务:', t0.name, '/', t1.area + '：' + t1.name);

  console.log('3) 上传 8 个素材（模拟 1 门头照 + 1 全景视频 + 区域 6 项）');
  const files = [
    [t0.id, 'sim/sharp.jpg', 'photo'],
    [t0.id, 'sim/video_h264.mp4', 'video'],
    [t1.id, 'sim/sharp.jpg', 'photo'],
    [t1.id, 'sim/blur.jpg', 'photo'],
    [t1.id, 'sim/dark.jpg', 'photo'],
    [t1.id, 'sim/sharp.jpg', 'photo'],
    [t1.id, 'sim/video_hevc.mp4', 'video'],
    [t1.id, 'sim/video_h264.mp4', 'video'],
  ];
  for (const [tid, f, kind] of files) await uploadFile(login.token, siteId, tid, f, kind);

  console.log('4) 回查');
  const after = await json('/api/sites/' + siteId, { headers: { Authorization: 'Bearer ' + login.token } });
  let photos = 0, videos = 0, bytes = 0;
  for (const t of after.tasks) {
    photos += (t.photos || []).length;
    videos += (t.videos || []).length;
    for (const f of [...(t.photos || []), ...(t.videos || [])]) bytes += f.size || 0;
  }
  console.log(`   ${after.name} | 任务 ${after.tasks.length} | 照片 ${photos} | 视频 ${videos} | ${(bytes / 1048576).toFixed(1)}MB`);
  console.log('   site_id=' + siteId);
  fs.writeFileSync('sim/site_id.txt', siteId);
})().catch((e) => { console.error('模拟失败:', e.message); process.exit(1); });

