"""build.ps1 里自动把 AndroidManifest 的版本号写进 BuildConfigVersion.java。"""

import io

p = 'android/build.ps1'
s = io.open(p, encoding='utf-8').read()

if 'BuildConfigVersion' not in s:
    old = '$sources += Get-ChildItem "$APP\\src" -Recurse -Filter *.java | ForEach-Object { $_.FullName }'
    new = '''# 版本号同步到 Java 常量（App 内检查更新用）
$mf = Get-Content "$APP\\AndroidManifest.xml" -Raw -Encoding UTF8
$vc = [regex]::Match($mf, 'android:versionCode="(\\d+)"').Groups[1].Value
$vn = [regex]::Match($mf, 'android:versionName="([^"]+)"').Groups[1].Value
$vcFile = "$APP\\src\\com\\egoops\\collect\\BuildConfigVersion.java"
$vcBody = @"
package com.egoops.collect;

/** 当前 APK 的版本号（构建时自动生成，勿手改） */
public class BuildConfigVersion {
    public static final int CODE = $vc;
    public static final String NAME = "$vn";
}
"@
[System.IO.File]::WriteAllText($vcFile, $vcBody, (New-Object System.Text.UTF8Encoding($false)))

$sources += Get-ChildItem "$APP\\src" -Recurse -Filter *.java | ForEach-Object { $_.FullName }'''
    assert old in s, '找不到 javac 前的 sources 行'
    s = s.replace(old, new, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('build.ps1: 自动生成版本常量')
else:
    print('build.ps1: 已有版本常量生成')
