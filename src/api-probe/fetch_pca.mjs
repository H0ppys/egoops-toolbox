import fs from 'node:fs';

const url = 'https://cdn.jsdelivr.net/gh/modood/Administrative-divisions-of-China@master/dist/pca-code.json';
const res = await fetch(url);
if (!res.ok) { console.log('FAIL', res.status); process.exit(1); }
const text = await res.text();
fs.writeFileSync('viewer/pca.json', text);
const data = JSON.parse(text);
console.log('省', data.length, '| 文件', (text.length / 1024).toFixed(0) + 'KB');
