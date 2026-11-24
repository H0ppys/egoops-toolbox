// 从 EgoOps 拉一次「采集场景分类」，生成 relay/scenes.json
import fs from 'node:fs';

const tok = JSON.parse(fs.readFileSync('egoops_token.json', 'utf8'));
const exp = tok.exp * 1000;
console.log('token 到期', new Date(exp).toLocaleString(), '| 剩余小时', ((exp - Date.now()) / 3600000).toFixed(1));

const r = await fetch('https://mrobo.uav.meituan.com/egoops/api/v1/tet-snapshots/active', {
  headers: { Authorization: 'Bearer ' + tok.access_token },
});
console.log('status', r.status);
if (!r.ok) process.exit(1);
const j = await r.json();

const items = [];
for (const [k1, v1] of Object.entries(j.snapshot_data || {})) {
  for (const [k2, v2] of Object.entries(v1.children || {})) {
    items.push({
      path: k1 + '/' + k2,
      category: v1.name_zh,
      scene: String(v2.name_zh).trim(),
      label: v1.name_zh + ' / ' + String(v2.name_zh).trim(),
    });
  }
}
items.sort((a, b) => a.label.localeCompare(b.label, 'zh'));
console.log('分类数', items.length);
console.log('示例', items.slice(0, 5).map(x => x.label).join(' | '));

fs.writeFileSync('relay/scenes.json', JSON.stringify({
  generated_at: new Date().toISOString(),
  snapshot_id: j.snapshot_id,
  total: items.length,
  items,
}, null, 1));
console.log('written relay/scenes.json');
