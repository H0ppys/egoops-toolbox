"""导入新一版「场景分类」Excel，自动比对差异并保留各厂商配置。

用法：
    python tools/import_scenes.py "C:\\path\\MT-EGO TET v2.3 场景分类.xlsx"

做的事：
  1. 读新表的 domain / scene，重建 relay/scenes.json（保留能对上的 TET path）
  2. 和旧表比对：新增/删除的大类与场景
  3. 检查 relay/vendor_scenes.json 里配的大类在新表里还在不在（不在就报警）
  4. 打印变更摘要，等你确认后再发布
"""

import io
import json
import os
import re
import sys
from collections import OrderedDict

import openpyxl

SCENES = 'relay/scenes.json'
VENDORS = 'relay/vendor_scenes.json'


def norm(t):
    return re.sub(r'[\s\-_/·、（）()]+', '', t or '').lower()


def read_xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['场景分类']
    pairs = []
    for r in ws.iter_rows(values_only=True):
        d = (r[0] or '').strip() if r[0] else ''
        s = (r[1] or '').strip() if len(r) > 1 and r[1] else ''
        if d and s and d.lower() != 'domain':
            pairs.append((d, s))

    restricted = []
    if '限制场景分类' in wb.sheetnames:
        ws2 = wb['限制场景分类']
        for r in ws2.iter_rows(values_only=True):
            if not r or not r[0] or str(r[0]).strip() in ('Domain', ''):
                continue
            restricted.append({
                'domain': str(r[0]).strip(),
                'scene': str(r[1] or '').strip(),
                'status': str(r[4] or '').strip(),
                'note': str(r[3] or '').strip(),
            })
    return pairs, restricted


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    xlsx = sys.argv[1]

    try:
        old = json.load(io.open(SCENES, encoding='utf-8'))
    except Exception:
        old = {'items': []}

    old_tet = {}
    old_domains = OrderedDict()
    old_pair = set()
    for it in old.get('items', []):
        old_tet.setdefault(norm(it['scene']), it.get('tet') or it['path'])
        old_domains.setdefault(it['category'], 0)
        old_domains[it['category']] += 1
        old_pair.add((it['category'], it['scene']))

    pairs, restricted = read_xlsx(xlsx)

    items = []
    new_domains = OrderedDict()
    for d, s in pairs:
        tet = old_tet.get(norm(s), '')
        if not tet:
            for part in re.split(r'[-—·]', s):
                tet = old_tet.get(norm(part), '')
                if tet:
                    break
        items.append({'path': tet or (d + '/' + s), 'category': d, 'scene': s,
                      'label': d + ' / ' + s, 'tet': tet})
        new_domains.setdefault(d, 0)
        new_domains[d] += 1

    new_pair = set((it['category'], it['scene']) for it in items)
    added = sorted(new_pair - old_pair)
    removed = sorted(old_pair - new_pair)

    print('旧表: %d 个场景 / %d 个大类' % (len(old_pair), len(old_domains)))
    print('新表: %d 个场景 / %d 个大类' % (len(new_pair), len(new_domains)))
    print('匹配到 TET path: %d / %d' % (sum(1 for x in items if x['tet']), len(items)))

    new_cats = set(new_domains)
    old_cats = set(old_domains)
    if new_cats - old_cats:
        print('\n[新增大类]', ' / '.join(sorted(new_cats - old_cats)))
    if old_cats - new_cats:
        print('[消失的大类]', ' / '.join(sorted(old_cats - new_cats)))
    if added:
        print('\n[新增场景 %d]' % len(added))
        for c, s in added[:25]:
            print('  + %s / %s' % (c, s))
        if len(added) > 25:
            print('  … 还有 %d 个' % (len(added) - 25))
    if removed:
        print('\n[删除场景 %d]' % len(removed))
        for c, s in removed[:25]:
            print('  - %s / %s' % (c, s))
        if len(removed) > 25:
            print('  … 还有 %d 个' % (len(removed) - 25))

    # 各厂商配置是否还合法
    try:
        vendors = json.load(io.open(VENDORS, encoding='utf-8'))
    except Exception:
        vendors = {}
    if vendors:
        print('\n[厂商配置检查]')
        changed = False
        for code, allow in list(vendors.items()):
            bad = [a for a in allow if a not in new_cats]
            if bad:
                print('  ! %s 配的大类在新表里没有了：%s' % (code, ' / '.join(bad)))
                vendors[code] = [a for a in allow if a in new_cats]
                changed = True
            else:
                print('  OK  %s：%s' % (code, ' / '.join(allow)))
        if changed:
            print('  （已自动移除失效大类；如需改成全部，执行 set_vendor_scenes.py %s all）' % list(vendors)[0])

    out = {'version': os.path.basename(xlsx), 'count': len(items),
           'items': items, 'restricted': restricted}
    io.open(SCENES, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=0))
    io.open(VENDORS, 'w', encoding='utf-8').write(json.dumps(vendors, ensure_ascii=False, indent=1))
    print('\n已写入 %s 与 %s' % (SCENES, VENDORS))
    print('发布到服务器：')
    print('  python ssh_exec.py -u relay/scenes.json /opt/egoops/relay/scenes.json')
    print('  python ssh_exec.py -u relay/vendor_scenes.json /opt/egoops/relay/vendor_scenes.json')
    print('  python ssh_exec.py "systemctl restart egoops-relay"')


if __name__ == '__main__':
    main()
