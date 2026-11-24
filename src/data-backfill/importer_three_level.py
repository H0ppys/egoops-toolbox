"""导入脚本支持三种表头：
   大类 + 场景            （现在美团这份）
   大类 + 分类 + 场景     （有的厂商是三级）
带三级时，items 里会多一个 group 字段，App 会显示三个下拉。
"""

import io

p = 'tools/import_vendor_scenes.py'
s = io.open(p, encoding='utf-8').read()

old = '''def read_xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    sheet = '场景分类' if '场景分类' in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet]
    pairs = []
    for r in ws.iter_rows(values_only=True):
        d = (r[0] or '').strip() if r[0] else ''
        s = (r[1] or '').strip() if len(r) > 1 and r[1] else ''
        if d and s and d.lower() != 'domain':
            pairs.append((d, s))'''

new = '''def read_xlsx(path):
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
                pairs.append((d, '', s))'''

assert old in s
s = s.replace(old, new)

old2 = '''    items = []
    for d, s in pairs:'''
new2 = '''    items = []
    for d, g, s in pairs:'''
assert old2 in s
s = s.replace(old2, new2)

old3 = '''        items.append({'path': tet or (d + '/' + s), 'category': d, 'scene': s,
                      'label': d + ' / ' + s, 'tet': tet})'''
new3 = '''        label = (d + ' / ' + g + ' / ' + s) if g else (d + ' / ' + s)
        path = tet or (d + ('/' + g if g else '') + '/' + s)
        items.append({'path': path, 'category': d, 'group': g, 'scene': s,
                      'label': label, 'tet': tet})'''
assert old3 in s
s = s.replace(old3, new3)

# 统计里也带上分组数
s = s.replace('''    cats = OrderedDict()
    for it in data['items']:
        cats.setdefault(it['category'], 0)
        cats[it['category']] += 1''', '''    cats = OrderedDict()
    groups = set()
    for it in data['items']:
        cats.setdefault(it['category'], 0)
        cats[it['category']] += 1
        if it.get('group'):
            groups.add((it['category'], it['group']))''')

s = s.replace('''    print('场景 %d 个 / 大类 %d 个' % (len(data['items']), len(cats)))''',
'''    print('场景 %d 个 / 大类 %d 个%s' % (len(data['items']), len(cats),
          (' / 分类 %d 个' % len(groups)) if groups else '（两级）'))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('importer 支持三级（大类/分类/场景）')
