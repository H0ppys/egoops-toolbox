import io

p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()
old = "if ($NoCapture) { $outApk = Join-Path $APP 'egoops-nocap-v72.apk' }\n"
new = ("if ($NoCapture) {\n"
       "    $outApk = Join-Path $APP 'egoops-nocap-v72.apk'\n"
       "} else {\n"
       "    $outApk = Join-Path $APP 'egoops-collect-v72.apk'\n"
       "}\n")
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('已修复 outApk')
else:
    print('未找到目标行，当前内容：')
    for line in s.splitlines():
        if 'outApk' in line:
            print(' ', line)
