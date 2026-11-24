"""去掉重复方法：每个方法保留一个（优先保留靠后的新版本 useLocation/startGps），
   然后重新编译。"""

import io
import re

p = 'android/src/com/egoops/collect/MainActivity.java'
lines = io.open(p, encoding='utf-8').read().splitlines(True)


def method_span(start):
    """从签名行开始，找到方法体结束（大括号配平），包含前面紧邻的注释"""
    depth = 0
    end = start
    for i in range(start, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if depth == 0 and i > start:
            end = i
            break
        if depth == 0 and i == start and '{' in lines[i] and '}' in lines[i]:
            end = i
            break
    return end


def drop(defs, keep_last):
    # 收集每个定义的行区间
    spans = []
    for d in defs:
        idxs = [i for i, l in enumerate(lines) if d in l]
        if len(idxs) > 1:
            keep = idxs[-1] if keep_last else idxs[0]
            for i in idxs:
                if i == keep:
                    continue
                s = i
                # 带上注释
                while s > 0 and (lines[s - 1].strip().startswith('/**') or lines[s - 1].strip().startswith('*')):
                    s -= 1
                e = method_span(i)
                spans.append((s, e))
    return spans


spans = drop([
    'private static String antiCodeOf',   # 保留第一个
], keep_last=False) + drop([
    'private void stampWatermark',
    'private void startGps',
    'private void useLocation',            # 保留靠后的新版本
], keep_last=True)

# 从后往前删，避免行号错位
for s, e in sorted(spans, key=lambda x: -x[0]):
    del lines[s:e + 1]
    print('删除行 %d - %d' % (s + 1, e + 1))

io.open(p, 'w', encoding='utf-8').write(''.join(lines))

# 复核
s2 = ''.join(lines)
for name in ['private void startGps', 'private void useLocation',
             'private void stampWatermark', 'private static String antiCodeOf']:
    print(name, s2.count(name))
