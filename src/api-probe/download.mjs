// 下载 Android 构建工具链（JDK + build-tools + platform）
import fs from 'node:fs';
import path from 'node:path';

const items = [
  { url: 'https://mirrors.huaweicloud.com/openjdk/17.0.2/openjdk-17.0.2_windows-x64_bin.zip', out: 'tools/download/jdk17.zip' },
  { url: 'https://mirrors.cloud.tencent.com/AndroidSDK/build-tools_r34-windows.zip', out: 'tools/download/build-tools-34.zip' },
  { url: 'https://dl.google.com/android/repository/platform-34-ext7_r03.zip', out: 'tools/download/platform-34.zip' },
];

fs.mkdirSync('tools/download', { recursive: true });

async function grab({ url, out }) {
  const tmp = out + '.part';
  const res = await fetch(url, { redirect: 'follow' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const total = Number(res.headers.get('content-length') || 0);
  const fd = fs.openSync(tmp, 'w');
  let got = 0;
  let lastPct = -1;
  const reader = res.body.getReader();
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    fs.writeSync(fd, value);
    got += value.length;
    const pct = total ? Math.floor((got / total) * 100) : 0;
    if (pct !== lastPct && pct % 25 === 0) { lastPct = pct; console.log(`  ${path.basename(out)} ${pct}% (${(got / 1048576).toFixed(0)}MB)`); }
  }
  fs.closeSync(fd);
  fs.renameSync(tmp, out);
  console.log(`OK ${out} ${(fs.statSync(out).size / 1048576).toFixed(1)}MB`);
}

for (const it of items) {
  if (fs.existsSync(it.out) && fs.statSync(it.out).size > 20 * 1024 * 1024) { console.log('SKIP', it.out); continue; }
  for (let attempt = 1; attempt <= 3; attempt++) {
    try { await grab(it); break; } catch (e) {
      console.log(`  attempt ${attempt} failed: ${e.message}`);
      if (attempt === 3) { console.log('FAILED', it.out); process.exit(1); }
    }
  }
}
console.log('ALL DONE');
