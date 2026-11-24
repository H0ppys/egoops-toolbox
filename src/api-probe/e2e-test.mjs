// 端到端验证：模拟一台手机走完「申请采集点」全流程
const RELAY = process.env.RELAY || 'http://127.0.0.1:18090';
let TOKEN = '';

async function api(method, path, body, opts = {}) {
  const res = await fetch(RELAY + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok && !opts.allowFail) throw new Error(`${method} ${path} -> ${res.status} ${JSON.stringify(data)}`);
  return { status: res.status, data };
}

const log = (...a) => console.log('  ', ...a);

// 假素材（体积小，但内容类型按真实走）
function fakeJpeg(size = 200 * 1024) {
  const b = Buffer.alloc(size, 0xff);
  b.write('\xff\xd8\xff\xe0', 0, 'binary');
  return b;
}
function fakeMp4(size = 2 * 1024 * 1024) {
  const b = Buffer.alloc(size, 0x00);
  b.write('ftypisom', 4, 'binary');
  return b;
}

async function uploadOne(siteId, taskId, kind, name, buf, contentType, role) {
  const init = await api('POST', `/api/sites/${siteId}/media/init`, {
    task_id: taskId, kind, filename: name, content_type: contentType, size: buf.length, role,
  });
  const { media_id, upload_url } = init.data;
  const put = await fetch(upload_url, { method: 'PUT', headers: { 'Content-Type': contentType }, body: buf });
  if (!put.ok) throw new Error(`PUT ${upload_url} -> ${put.status}`);
  await api('POST', `/api/sites/${siteId}/media/${media_id}/complete`, {});
  return media_id;
}

(async () => {
  console.log('1) 登录');
  const login = await api('POST', '/api/auth/login', { name: '采集员-张三', phone: '<FILL_ME>' });
  TOKEN = login.data.token;
  log('collector:', login.data.collector.name);

  console.log('2) 拉场景分类');
  const scenes = await api('GET', '/api/scenes');
  log('可选场景', scenes.data.total, '个，例如:', scenes.data.items.slice(0, 3).map(x => x.label).join(' / '));
  const scene = scenes.data.items.find(x => x.path === 'home/detached_house') || scenes.data.items[0];

  console.log('3) 建采集点草稿（2 个任务）');
  const payload = {
    name: `测试采集点-${Date.now()}`,
    address: '江西省南昌市东湖区测试路 1 号',
    tet_node_path: scene.path,
    description: '端到端测试用，验证申请采集点全链路。',
    tasks: [
      { task_name: '门头与全景采集', description: '门头照、店内全景、现场环境视频', required_duration: 1800, sop: ['门前全景环绕一周', '店内全景 360 度'] },
      { task_name: '清洁动作采集', description: '客厅擦拭动作', required_duration: 3600, sop: ['准备工具', '执行擦拭动作'] },
    ],
  };
  const created = await api('POST', '/api/sites', payload);
  const site = created.data.site;
  log('site_id:', site.id, 'ego_task_set_id:', site.ego_task_set_id, 'tasks:', site.tasks.length);

  console.log('4) 幂等校验：同名称同地址重复提交');
  const dup = await api('POST', '/api/sites', payload);
  log('重复提交返回 existing =', dup.data.existing, '，同一个 site_id =', dup.data.site.id === site.id);

  console.log('5) 提前提交（应当被拦）');
  const early = await api('POST', `/api/sites/${site.id}/submit`, undefined, { allowFail: true });
  log('状态码', early.status, '问题:', early.data?.error?.detail?.join('; '));

  console.log('6) 上传素材：每个任务 3 张照片 + 1 个视频');
  for (const [i, task] of site.tasks.entries()) {
    for (let k = 1; k <= 3; k++) {
      await uploadOne(site.id, task.id, 'photo', `IMG_${i}_${k}.jpg`, fakeJpeg(), 'image/jpeg', k === 1 ? 'door' : 'pano');
    }
    await uploadOne(site.id, task.id, 'video', `VID_${i}.mp4`, fakeMp4(), 'video/mp4', 'site');
    log(`任务${i + 1} 上传完成`);
  }

  console.log('7) 超限校验：补到 9 张后第 10 张应当被拒');
  for (let k = 4; k <= 9; k++) {
    await uploadOne(site.id, site.tasks[0].id, 'photo', `IMG_0_${k}.jpg`, fakeJpeg(), 'image/jpeg', 'detail');
  }
  const over = await api('POST', `/api/sites/${site.id}/media/init`, {
    task_id: site.tasks[0].id, kind: 'photo', filename: 'x.jpg', content_type: 'image/jpeg', size: 1000,
  }, { allowFail: true });
  log('状态码', over.status, '原因:', over.data?.error?.message);

  console.log('8) 提交审核');
  const sub = await api('POST', `/api/sites/${site.id}/submit`);
  log('review_status =', sub.data.site.review_status, 'status =', sub.data.site.status);

  console.log('9) 回查台账');
  const list = await api('GET', '/api/sites');
  const mine = list.data.items.find(x => x.id === site.id);
  log('台账条数', list.data.items.length, '| 本条状态', mine.status, mine.review_status);

  console.log('10) 模拟服务端数据核对');
  const mock = await fetch('http://127.0.0.1:18080/api/v1/__mock/sites', {
    headers: { Authorization: 'Bearer x' },
  }).then(r => r.json());
  const ms = mock.sites.find(s => s.task_set_id === site.ego_task_set_id);
  log('EgoOps 侧: 名称 =', ms.name);
  log('EgoOps 侧: 地址 =', ms.address);
  log('EgoOps 侧: 场景 =', ms.tet_node_path);
  log('EgoOps 侧: 审核状态 =', ms.review_status);
  log('EgoOps 侧: 任务 =', ms.tasks.map(t => `${t.task_name}(照片${t.task_photos.length}/视频${t.task_videos.length})`).join(', '));

  const ok = ms.review_status === 'submitted' && ms.tasks.every(t => t.task_photos.length === (t.task_set_id === site.ego_task_set_id && ms.tasks.indexOf(t) === 0 ? 9 : 3) && t.task_videos.length === 1);
  console.log(ok ? '\n✅ 全链路通过' : '\n❌ 校验失败');
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error('\n❌ 失败:', e.message); process.exit(1); });
