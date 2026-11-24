"""记录拍摄时刻，并让「照片时间」用真正拍摄时间（文件生成那一刻），
   同时把水印里的定位/时间都改成拍摄时快照，避免上传时再取。"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 收下素材时记录拍摄时刻
old = '''        m.shot = pendingShot;
        Model.Task task = task(currentTask);'''
new = '''        m.shot = pendingShot;
        m.capturedAt = dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis();
        Model.Task task = task(currentTask);'''
assert old in s
s = s.replace(old, new)

# 2) 照片烧水印用 capturedAt（落盘那一刻）
s = s.replace('            if (!video) stampWatermark(dest, System.currentTimeMillis());',
              '            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis());')

io.open(p, 'w', encoding='utf-8').write(s)
print('capturedAt 已记录')

# 3) 版本 60
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="59"', 'android:versionCode="60"').replace('android:versionName="59.0"', 'android:versionName="60.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v59.apk', 'egoops-collect-v60.apk').replace('--version-code 59 --version-name 59.0', '--version-code 60 --version-name 60.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 60')
