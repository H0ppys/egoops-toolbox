import io

m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="60"', 'android:versionCode="61"')
m = m.replace('android:versionName="60.0"', 'android:versionName="61.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v60.apk', 'egoops-collect-v61.apk')
b = b.replace('--version-code 60 --version-name 60.0', '--version-code 61 --version-name 61.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 61')
