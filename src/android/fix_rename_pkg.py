"""改用 aapt2 的 --rename-manifest-package：
   清单里保持 com.egoops.collect（R 类不变），只把安装包名改成 .nocap。"""

import io

p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()

# 清单副本：只改 label，不改包名
old_block = '''if ($NoCapture) {
    $m = Get-Content $manifest -Raw -Encoding UTF8
    $m = $m -replace 'package="com\\.egoops\\.collect"', 'package="com.egoops.collect.nocap"'
    $m = $m -replace 'android:label="@string/app_name"', 'android:label="不拍摄收集"'
    $manifest = "$BUILD\\AndroidManifest.xml"
    [System.IO.File]::WriteAllText($manifest, $m, (New-Object System.Text.UTF8Encoding($false)))
}'''
new_block = '''if ($NoCapture) {
    $m = Get-Content $manifest -Raw -Encoding UTF8
    $m = $m -replace 'android:label="@string/app_name"', 'android:label="不拍摄收集"'
    $manifest = "$BUILD\\AndroidManifest.xml"
    [System.IO.File]::WriteAllText($manifest, $m, (New-Object System.Text.UTF8Encoding($false)))
}'''
assert old_block in s
s = s.replace(old_block, new_block)

old_link = '''$rPkg = ''
if ($NoCapture) { $rPkg = '--custom-package com.egoops.collect' }
& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$manifest" --java "$BUILD\\gen" $rPkg --min-sdk-version 21 --target-sdk-version 34 --version-code 72 --version-name 72.0 $flats'''
new_link = '''$rename = @()
if ($NoCapture) { $rename = @('--rename-manifest-package', 'com.egoops.collect.nocap') }
& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$manifest" --java "$BUILD\\gen" @rename --min-sdk-version 21 --target-sdk-version 34 --version-code 72 --version-name 72.0 $flats'''
assert old_link in s
s = s.replace(old_link, new_link)

io.open(p, 'w', encoding='utf-8').write(s)
print('改用 --rename-manifest-package')
