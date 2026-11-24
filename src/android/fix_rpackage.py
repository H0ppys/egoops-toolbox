"""不拍摄版：清单包名变了，R 类默认也会跟着变，导致 Java 里 R 找不到。
   用 aapt2 --custom-package 把 R 固定回 com.egoops.collect。"""

import io

p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()

old = '''& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$manifest" --java "$BUILD\\gen" --min-sdk-version 21 --target-sdk-version 34 --version-code 72 --version-name 72.0 $flats'''
new = '''$rPkg = ''
if ($NoCapture) { $rPkg = '--custom-package com.egoops.collect' }
& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$manifest" --java "$BUILD\\gen" $rPkg --min-sdk-version 21 --target-sdk-version 34 --version-code 72 --version-name 72.0 $flats'''

assert old in s, '找不到 aapt2 link 行'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('aapt2 link 已加 --custom-package')
