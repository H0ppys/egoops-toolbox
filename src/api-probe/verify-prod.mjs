// 线上只读自检：不建点、不提交，只验证服务端到 EgoOps 的链路是否正常
// 用法：node tools/verify-prod.mjs [http://<FILL_ME>/relay]
const BASE = (process.argv[2] || 'http://<FILL_ME>/relay').replace(/\/+$/, '');
const log = (...a) => console.log('  ', ...a);
let failed = 0;

async function call(method, path, body, token) {
  const res = await fetch(BASE + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: 'Bearer ' + token } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = text; }
  return { status: res.status, data };
}

function check(ok, label, extra = '') {
  console.log(`${ok ? '  ✅' : '  ❌'} ${label}${extra ? ' — ' + extra : ''}`);
  if (!ok) failed++;
}

(async () => {
  console.log(`\n目标：${BASE}\n`);

  console.log('1) 服务健康');
  const h = await call('GET', '/api/health');
  check(h.status === 200 && h.data.ok, 'relay 存活', h.data.egoopsBase);

  console.log('2) 采集员登记（只写本地台账）');
  const l = await call('POST', '/api/auth/login', { name: '自检-' + new Date().toISOString().slice(11, 19), phone: '' });
  check(l.status === 200 && !!l.data.token, '拿设备 token');
  const token = l.data.token;

  console.log('3) 场景分类（读 EgoOps 真实接口）');
  const s = await call('GET', '/api/scenes', undefined, token);
  check(s.status === 200 && s.data.total > 0, '拉到场景分类', `${s.data.total} 个`);
  if (s.data.total) {
    const sample = s.data.items.slice(0, 3).map(x => x.label).join(' | ');
    log('示例：', sample);
  }

  console.log('4) 台账');
  const sites = await call('GET', '/api/sites', undefined, token);
  check(sites.status === 200 && Array.isArray(sites.data.items), '台账可读', `${sites.data.items.length} 条`);

  console.log('\n' + (failed ? `❌ ${failed} 项失败` : '✅ 全部通过（未产生任何 EgoOps 写入）'));
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error('❌ 脚本异常：', e.message); process.exit(1); });
