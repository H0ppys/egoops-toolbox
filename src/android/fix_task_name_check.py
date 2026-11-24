import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()
old = '"任务" + (i + 1).equals(t.name.trim())'
new = '("任务" + (i + 1)).equals(t.name.trim())'
assert old in s
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8').write(s)
print('括号修好')
