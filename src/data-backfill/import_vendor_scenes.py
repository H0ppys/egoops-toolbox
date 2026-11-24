"""按厂商导入各自的场景分类表（每个厂商一套大类/分类，互不影响）。

用法：
    python tools/import_scenes.py --vendor KWQZB "D:\\美团.xlsx"        # 美团自己的分类
    python tools/import_scenes.py --vendor MPRGV "D:\\小鹏.xlsx"        # 小鹏自己的分类
    python tools/import_scenes.py --vendor KWQZB "D:\\美团.xlsx" --deploy

不给 --vendor 时，导入的是"全局默认表"（没配过分类的厂商都看这份）。
"""

import io
import json
import os
import re
import sys
from collections import OrderedDict

import openpyxl

DEFAULT_FILE = 'relay/scenes.json'
VENDOR_DIR = 'relay/vendor_scenes'


def norm(t):
    return re.sub(r'[\s\-_/·、（）()]+', '', t or '').lower()


def read_xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    sheet = '场景分类' if '场景分类' in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))

    # 看表头判断是两级还是三级
    header = [str(x or '').strip().lower() for x in (rows[0] if rows else [])]
    three = False
    if len(header) >= 3 and header[0] in ('domain', '大类') and header[2] not in ('', 'none'):
        three = bool(header[2])
        three = True

    pairs = []
    for r in rows:
        if not r or not r[0]:
            continue
        d = str(r[0]).strip()
        if d.lower() in ('domain', '大类'):
            continue
        if three:
            g = str(r[1] or '').strip()
            s = str(r[2] or '').strip() if len(r) > 2 else ''
            if d and s:
                pairs.append((d, g, s))
        else:
            s = str(r[1] or '').strip() if len(r) > 1 else ''
            if d and s:
                pairs.append((d, '', s))
    restricted = []
    if '限制场景分类' in wb.sheetnames:
        for r in wb['限制场景分类'].iter_rows(values_only=True):
            if not r or not r[0] or str(r[0]).strip() in ('Domain', ''):
                continue
            restricted.append({'domain': str(r[0]).strip(), 'scene': str(r[1] or '').strip(),
                               'status': str(r[4] or '').strip()})
    return pairs, restricted


def build(pairs, restricted, old_tet, version):
    items = []
    for d, g, s in pairs:
        tet = old_tet.get(norm(s), '')
        if not tet:
            for part in re.split(r'[-—·]', s):
                tet = old_tet.get(norm(part), '')
                if tet:
                    break
        label = (d + ' / ' + g + ' / ' + s) if g else (d + ' / ' + s)
        path = tet or (d + ('/' + g if g else '') + '/' + s)
        items.append({'path': path, 'category': d, 'group': g, 'scene': s,
                      'label': label, 'tet': tet})
    return {'version': version, 'count': len(items), 'items': items, 'restricted': restricted}


def main():
    args = sys.argv[1:]
    deploy = '--deploy' in args
    args = [a for a in args if a != '--deploy']

    vendor = ''
    if '--vendor' in args:
        i = args.index('--vendor')
        vendor = args[i + 1].strip().upper()
        del args[i:i + 2]

    if not args:
        print(__doc__)
        return
    xlsx = args[0]

    # 复用默认表里已经匹配好的 TET path
    try:
        base = json.load(io.open(DEFAULT_FILE, encoding='utf-8'))
    except Exception:
        base = {'items': []}
    old_tet = {}
    for it in base.get('items', []):
        old_tet.setdefault(norm(it['scene']), it.get('tet') or it['path'])

    pairs, restricted = read_xlsx(xlsx)
    data = build(pairs, restricted, old_tet, os.path.basename(xlsx))

    cats = OrderedDict()
    groups = set()
    for it in data['items']:
        cats.setdefault(it['category'], 0)
        cats[it['category']] += 1
        if it.get('group'):
            groups.add((it['category'], it['group']))

    target = os.path.join(VENDOR_DIR, vendor + '.json') if vendor else DEFAULT_FILE
    print('厂商:', vendor or '（全局默认）')
    print('来源:', os.path.basename(xlsx))
    print('场景 %d 个 / 大类 %d 个%s' % (len(data['items']), len(cats),
          (' / 分类 %d 个' % len(groups)) if groups else '（两级）'))
    for c, n in cats.items():
        print('  %-10s %d' % (c, n))
    if restricted:
        print('限制场景:', len(restricted), '条')

    os.makedirs(os.path.dirname(target), exist_ok=True)
    io.open(target, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=0))
    print('已写入', target)

    if deploy:
        remote = '/opt/egoops/relay/' + ('vendor_scenes/%s.json' % vendor if vendor else 'scenes.json')
        import subprocess
        PY = os.environ.get('PYTHON_FOR_SSH', 'python')
        subprocess.run([PY, 'ssh_exec.py', 'mkdir -p /opt/egoops/relay/vendor_scenes'], check=True)
        subprocess.run([PY, 'ssh_exec.py', '-u', target, remote], check=True)
        subprocess.run([PY, 'ssh_exec.py', 'systemctl restart egoops-relay'], check=True)
        print('已发布到服务器')
    else:
        print('（加 --deploy 才会发布）')


if __name__ == '__main__':
    main()
