// 可行性验证：用 Edge 无头模式 + 复制的用户资料，走 egoops 自己的 OIDC 流程拿 token
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const SRC = path.join(process.env.LOCALAPPDATA, 'Microsoft', 'Edge', 'User Data');
const TMP = path.join(os.tmpdir(), 'egoops_cdp_probe');
const PORT = 9333;

function copyProfile() {
  fs.rmSync(TMP, { recursive: true, force: true });
  fs.mkdirSync(path.join(TMP, 'Default', 'Network'), { recursive: true });
  const files = [
    ['Local State', 'Local State'],
    [path.join('Default', 'Network', 'Cookies'), path.join('Default', 'Network', 'Cookies')],
    [path.join('Default', 'Preferences'), path.join('Default', 'Preferences')],
    [path.join('Default', 'Login Data'), path.join('Default', 'Login Data')],
  ];
  for (const [from, to] of files) {
    try {
      fs.copyFileSync(path.join(SRC, from), path.join(TMP, to));
      console.log('copied', from);
    } catch (e) {
      console.log('skip', from, e.code);
    }
  }
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function httpJson(url, method = 'GET') {
  const r = await fetch(url, { method });
  const t = await r.text();
  try { return JSON.parse(t); } catch { return t; }
}

(async () => {
  copyProfile();
  const args = [
    '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${TMP}`,
    '--disable-features=msEdgeSplashScreen,EdgeCollections', 'about:blank',
  ];
  const child = spawn(EDGE, args, { stdio: 'ignore', detached: false });
  console.log('edge pid', child.pid);

  let ver = null;
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    try { ver = await httpJson(`http://127.0.0.1:${PORT}/json/version`); break; } catch {}
  }
  console.log('devtools:', typeof ver === 'object' ? ver.Browser : ver);
  if (!ver || typeof ver !== 'object') { child.kill(); process.exit(1); }

  const targets = await httpJson(`http://127.0.0.1:${PORT}/json/list`);
  const page = (Array.isArray(targets) ? targets : []).find(t => t.type === 'page');
  console.log('page target:', page ? page.url : 'none');
  if (!page) { child.kill(); process.exit(1); }

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const send = (method, params = {}) => new Promise(res => {
    const i = ++id; pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Page.navigate', { url: 'https://egoops.meituan.com/recordings' });
  console.log('navigated, waiting for token…');

  let token = null;
  for (let i = 0; i < 60; i++) {
    await sleep(1000);
    const r = await send('Runtime.evaluate', {
      expression: `(() => { const k = Object.keys(sessionStorage).find(x => x.startsWith('oidc.user:')); return k ? sessionStorage.getItem(k) : null; })()`,
      returnByValue: true,
    });
    const val = r.result && r.result.result && r.result.result.value;
    if (val) { token = val; break; }
    if (i === 10) {
      const u = await send('Runtime.evaluate', { expression: 'location.href', returnByValue: true });
      console.log('  当前地址:', u.result?.result?.value);
    }
  }

  if (token) {
    const obj = JSON.parse(token);
    const p = JSON.parse(Buffer.from(obj.access_token.split('.')[1], 'base64url').toString());
    console.log('\n✅ 拿到 token!');
    console.log('   用户:', p.name, ' 过期:', new Date(p.exp * 1000).toLocaleString());
    console.log('   refresh_token:', !!obj.refresh_token);
  } else {
    console.log('❌ 10 秒内没拿到 token');
  }
  ws.close();
  child.kill();
  fs.rmSync(TMP, { recursive: true, force: true });
  process.exit(token ? 0 : 1);
})();
