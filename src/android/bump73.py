import io

m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="72"', 'android:versionCode="73"')
m = m.replace('android:versionName="72.0"', 'android:versionName="73.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('--version-code 72 --version-name 72.0', '--version-code 73 --version-name 73.0')
b = b.replace('egoops-nocap-v72.apk', 'egoops-nocap-v73.apk')
b = b.replace('egoops-collect-v72.apk', 'egoops-collect-v73.apk')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 73')
