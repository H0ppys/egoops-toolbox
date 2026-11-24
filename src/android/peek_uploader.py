import io

p = 'android/src/com/egoops/collect/Uploader.java'
s = io.open(p, encoding='utf-8').read()
i = s.find('uploadOneWithRetry(task, m)')
print(repr(s[max(0, i - 500):i + 100]))
