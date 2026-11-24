"""新增「不拍摄收集」版本：
   · 构建开关 -NoCapture 生成独立包（com.egoops.collect.nocap，名称「不拍摄收集」）
   · 该版本：不能拍照/录像，只能从相册选；且不给素材加水印（素材自带水印）
   · 不自动更新（避免被拍摄版覆盖）
"""

import io

# ---------- 1) build.ps1 ----------
p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()

if 'param(' not in s:
    s = s.replace('''$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot''',
'''param(
    [switch]$NoCapture   # 生成「不拍摄收集」版本
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot''')

# 版本号常量：加 NO_CAPTURE + 包名
s = s.replace('''    public static final int CODE = $vc;
    public static final String NAME = "$vn";
}''',
'''    public static final int CODE = $vc;
    public static final String NAME = "$vn";
    public static final boolean NO_CAPTURE = $($NoCapture.ToString().ToLower());
}''')

# 清单：不拍摄版换包名 + 名称
s = s.replace('''& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$APP\\AndroidManifest.xml"''',
'''$manifest = "$APP\\AndroidManifest.xml"
if ($NoCapture) {
    $m = Get-Content $manifest -Raw -Encoding UTF8
    $m = $m -replace 'package="com\\.egoops\\.collect"', 'package="com.egoops.collect.nocap"'
    $m = $m -replace 'android:label="@string/app_name"', 'android:label="不拍摄收集"'
    $manifest = "$BUILD\\AndroidManifest.xml"
    [System.IO.File]::WriteAllText($manifest, $m, (New-Object System.Text.UTF8Encoding($false)))
}
& "$BT\\aapt2.exe" link -o "$BUILD\\base.apk" -I $AJAR --manifest "$manifest"''')

# 输出名
s = s.replace('''$outApk = Join-Path $APP 'egoops-collect-v72.apk\'''',
'''if ($NoCapture) { $outApk = Join-Path $APP 'egoops-nocap-v72.apk' }''')

io.open(p, 'w', encoding='utf-8').write(s)
print('build.ps1: 支持 -NoCapture')
