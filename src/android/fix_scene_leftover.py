"""删掉 refreshSceneSpinner 之后遗留的残段（626-640 行）。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
lines = io.open(P, encoding='utf-8').read().splitlines(True)

# 找到残留块的起止：从 '        } else {' 紧跟 'String cat = categories.get(catPos - 1);'
start = None
for i in range(620, 645):
    if lines[i].strip() == '} else {' and 'catPos' in ''.join(lines[max(0, i - 3):i]):
        start = i
        break
if start is None:
    for i in range(620, 645):
        if lines[i].strip() == '} else {':
            start = i
            break

# 结束：下一行是 '    private void loadScenes() {'
end = None
for i in range(start, len(lines)):
    if lines[i].startswith('    private void loadScenes()'):
        end = i
        break

print('删除行区间:', start + 1, '到', end)
print(''.join(lines[start:start + 3]))
removed = ''.join(lines[start:end])
assert 'shownIndex.add(i)' in removed and 'loadScenes' not in removed

del lines[start:end]
io.open(P, 'w', encoding='utf-8').write(''.join(lines))
print('已删除', end - start, '行')
