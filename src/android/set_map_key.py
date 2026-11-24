import io

p = 'android/src/com/egoops/collect/MapSnap.java'
s = io.open(p, encoding='utf-8').read()
old = 'DEFAULT_KEY = "<FILL_ME>"'
new = 'DEFAULT_KEY = "<FILL_ME>"'
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('Key 已更新为可用的 Web服务 Key')

m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="69"', 'android:versionCode="70"')
m = m.replace('android:versionName="69.0"', 'android:versionName="70.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v69.apk', 'egoops-collect-v70.apk')
b = b.replace('--version-code 69 --version-name 69.0', '--version-code 70 --version-name 70.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 70')
