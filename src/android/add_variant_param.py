"""build.ps1 增加 -Variant：生成换名换包的独立版本（例如「采集水印相机」）。"""

import io

p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()

# 1) 参数
if '[string]$Variant' not in s:
    s = s.replace('''param(
    [switch]$NoCapture   # 生成「不拍摄收集」版本
)''',
'''param(
    [switch]$NoCapture,          # 生成「不拍摄收集」版本
    [string]$Variant = ""        # 换名版本，例如 "采集水印相机"
)''')

# 2) 清单：label + 重命名包
old = '''if ($NoCapture) {
    $m = Get-Content $manifest -Raw -Encoding UTF8
    $m = $m -replace 'android:label="@string/app_name"', 'android:label="不拍摄收集"'
    $manifest = "$BUILD\\AndroidManifest.xml"
    [System.IO.File]::WriteAllText($manifest, $m, (New-Object System.Text.UTF8Encoding($false)))
}'''
new = '''$label = ''
$pkgSuffix = ''
if ($NoCapture) { $label = '不拍摄收集'; $pkgSuffix = 'nocap' }
elseif ($Variant -ne '') { $label = $Variant; $pkgSuffix = 'wm' }

if ($label -ne '') {
    $m = Get-Content $manifest -Raw -Encoding UTF8
    $m = $m -replace 'android:label="@string/app_name"', ('android:label="' + $label + '"')
    $manifest = "$BUILD\\AndroidManifest.xml"
    [System.IO.File]::WriteAllText($manifest, $m, (New-Object System.Text.UTF8Encoding($false)))
}'''
assert old in s
s = s.replace(old, new)

# 3) aapt2 link：按后缀重命名包
old2 = '''$rename = @()
if ($NoCapture) { $rename = @('--rename-manifest-package', 'com.egoops.collect.nocap') }'''
new2 = '''$rename = @()
if ($pkgSuffix -ne '') { $rename = @('--rename-manifest-package', ('com.egoops.collect.' + $pkgSuffix)) }'''
assert old2 in s
s = s.replace(old2, new2)

# 4) 输出名
old3 = '''if ($NoCapture) {
    $outApk = Join-Path $APP 'egoops-nocap-v73.apk'
} else {
    $outApk = Join-Path $APP 'egoops-collect-v73.apk'
}'''
new3 = '''if ($NoCapture) {
    $outApk = Join-Path $APP 'egoops-nocap-v73.apk'
} elseif ($Variant -ne '') {
    $outApk = Join-Path $APP 'egoops-wm-v73.apk'
} else {
    $outApk = Join-Path $APP 'egoops-collect-v73.apk'
}'''
assert old3 in s
s = s.replace(old3, new3)

io.open(p, 'w', encoding='utf-8').write(s)
print('build.ps1: 支持 -Variant')
