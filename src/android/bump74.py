import io

# manifest
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="73"', 'android:versionCode="74"')
m = m.replace('android:versionName="73.0"', 'android:versionName="74.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

# build.ps1：版本参数 + 输出名
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('--version-code 73 --version-name 73.0', '--version-code 74 --version-name 74.0')
b = b.replace('egoops-collect-v73.apk', 'egoops-collect-v74.apk')
b = b.replace('egoops-nocap-v73.apk', 'egoops-nocap-v74.apk')
b = b.replace('egoops-wm-v73.apk', 'egoops-wm-v74.apk')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 74')
