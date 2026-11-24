import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()
old = 'String who = (site.collector == null || site.collector.trim().isEmpty()) ? "" : site.collector.trim();'
new = 'String who = (etCollector == null || etCollector.getText() == null) ? "" : etCollector.getText().toString().trim();'
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
