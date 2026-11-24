"""用官方 Excel 重建场景分类表（12 个 domain / 254 个 scene），并尽量映射回 TET path。"""

import io
import json
import re

import openpyxl

XLSX = r'C:\Users\Administrator\Desktop\MT-EGO TET v2.2 场景分类（domain & Scene）.xlsx'
OLD = 'relay/scenes.json'
NEW = 'relay/scenes.json'

# ---------- 1) 读 Excel ----------
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb['场景分类']
pairs = []
for r in ws.iter_rows(values_only=True):
    d = (r[0] or '').strip() if r[0] else ''
    s = (r[1] or '').strip() if len(r) > 1 and r[1] else ''
    if d and s and d.lower() != 'domain':
        pairs.append((d, s))


def norm(t):
    return re.sub(r'[\s\-_/·、（）()]+', '', t or '').lower()


# ---------- 2) 旧表里能对上的 TET path ----------
old = json.load(io.open(OLD, encoding='utf-8'))['items']
old_by_scene = {}
for it in old:
    old_by_scene.setdefault(norm(it['scene']), it['path'])
    old_by_scene.setdefault(norm(it['scene'].split('-')[-1]), it['path'])

items = []
matched = 0
for d, s in pairs:
    tet = old_by_scene.get(norm(s), '')
    if not tet:
        # “便利店的收银台” 这种带前缀的，用后半段再试一次
        for part in re.split(r'[-—·]', s):
            tet = old_by_scene.get(norm(part), '')
            if tet:
                break
    if tet:
        matched += 1
    items.append({
        "path": tet or (d + '/' + s),
        "category": d,
        "scene": s,
        "label": d + ' / ' + s,
        "tet": tet,
    })

# ---------- 3) 限制场景（拒收/审批加严） ----------
ws2 = wb['限制场景分类']
restricted = []
for r in ws2.iter_rows(values_only=True):
    if not r or not r[0] or str(r[0]).strip() in ('Domain', ''):
        continue
    restricted.append({
        "domain": str(r[0]).strip(),
        "scene": str(r[1] or '').strip(),
        "status": str(r[4] or '').strip(),
        "note": str(r[3] or '').strip(),
    })

out = {
    "version": "TET v2.2",
    "count": len(items),
    "items": items,
    "restricted": restricted,
}
io.open(NEW, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=0))

cats = {}
for it in items:
    cats.setdefault(it['category'], 0)
    cats[it['category']] += 1

print('场景数:', len(items), '| 大类数:', len(cats), '| 匹配到 TET path:', matched, '/', len(items))
for c, n in cats.items():
    print('  %-8s %d' % (c, n))
print('限制场景:', len(restricted), '（状态示例:', [x['status'] for x in restricted[:3]], '）')
print('前 3 条:', json.dumps(items[:3], ensure_ascii=False))
