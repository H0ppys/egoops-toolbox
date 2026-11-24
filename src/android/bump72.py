import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

old = '''                @Override public void onLocationChanged(android.location.Location l) {
                    useLocation(l);
                    try { lm.removeUpdates(holder[0]); } catch (Exception ignored) {}
                }'''
new = '''                @Override public void onLocationChanged(android.location.Location l) {
                    if (l.getAccuracy() > 80 && gpsAddress != null && !gpsAddress.isEmpty()) return;
                    useLocation(l);
                    try { lm.removeUpdates(holder[0]); } catch (Exception ignored) {}
                }'''

if 'getAccuracy() > 80' not in s:
    assert old in s
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('精度过滤已加')
else:
    print('已有精度过滤')

m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="71"', 'android:versionCode="72"')
m = m.replace('android:versionName="71.0"', 'android:versionName="72.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v71.apk', 'egoops-collect-v72.apk')
b = b.replace('--version-code 71 --version-name 71.0', '--version-code 72 --version-name 72.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 72')
