import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

old = '                            shoot(pendingShot);'
new = '''                            String kind2 = (pendingShot != null && pendingShot.toLowerCase().contains("video")) ? "video" : "photo";
                            captureShot(pendingShot, kind2);'''
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('fixed capture call')
