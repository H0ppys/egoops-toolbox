"""删掉重复的旧 stampWatermark（保留新版）和重复的 showAreaForTask1。"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
lines = io.open(p, encoding='utf-8').read().splitlines(True)

def find_all(text):
    return [i for i, l in enumerate(lines) if text in l]

# --- 处理 stampWatermark 重复 ---
idx = find_all('private void stampWatermark(File f) {')
print('stampWatermark 定义数:', len(idx))
if len(idx) > 1:
    # 保留最后一个（新样式），删掉前面的整段（到下一个顶层方法注释或方法定义）
    for start in idx[:-1][::-1]:
        end = start + 1
        depth = 1
        while end < len(lines) and depth > 0:
            depth += lines[end].count('{') - lines[end].count('}')
            end += 1
        # 连同前面的注释行一起删
        s2 = start
        while s2 > 0 and lines[s2 - 1].strip().startswith('/**'):
            s2 -= 1
        if s2 > 0 and lines[s2 - 1].strip().startswith('*'):
            # 多行注释
            k = s2 - 1
            while k > 0 and not lines[k].strip().startswith('/**'):
                k -= 1
            s2 = k
        del lines[s2:end]
        print('删除旧 stampWatermark 行', s2 + 1, '-', end)

# --- 处理 showAreaForTask1 重复 ---
idx2 = [i for i, l in enumerate(lines) if 'private void showAreaForTask1()' in l]
print('showAreaForTask1 定义数:', len(idx2))
if len(idx2) > 1:
    for start in idx2[1:][::-1]:
        end = start + 1
        depth = 1
        while end < len(lines) and depth > 0:
            depth += lines[end].count('{') - lines[end].count('}')
            end += 1
        s2 = start
        while s2 > 0 and lines[s2 - 1].strip().startswith(('/**', '*')):
            s2 -= 1
        del lines[s2:end]
        print('删除重复 showAreaForTask1 行', s2 + 1, '-', end)

io.open(p, 'w', encoding='utf-8').write(''.join(lines))
print('清理完成')
