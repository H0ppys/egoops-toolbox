# 未纳入仓库的工具链（TOOLCHAIN）

`tools\` 下有 5 个目录合计约 **1.05 GB**、约 1.16 万个文件，属于 Android 构建工具链与缓存，不复制进仓库。下面是清点结果与用途说明。

| 目录 | 大小 | 文件数 | 是什么 | 版本 | 来源 |
| --- | --- | --- | --- | --- | --- |
| `tools\build-tools\android-14` | 136.6 MB | 169 | Android SDK Build-Tools（`aapt2`、`d8`、`apksigner`、`zipalign`） | `Pkg.Revision=34.0.0`（`source.properties`） | Google Android SDK（`download\build-tools-34.zip` 解压） |
| `tools\jdk\jdk-17.0.2` | 294.5 MB | 485 | OpenJDK，供 `javac`/`keytool`/`apksigner` 使用 | Oracle OpenJDK `17.0.2`（2022-01-18，`release` 文件） | Oracle JDK 17 归档包（`download\jdk17.zip` 解压） |
| `tools\platform\android-34` | 94.5 MB | 10963 | Android SDK Platform 34（`android.jar`、`Layoutlib`、`data`） | `AndroidVersion.ApiLevel=34`、`Pkg.Revision=3`、`Platform.Version=14` | Google Android SDK（`download\platform-34.zip` 解压） |
| `tools\download` | 293.4 MB | 3 | 上述三者的原始压缩包 | `build-tools-34.zip`、`jdk17.zip`、`platform-34.zip` | 官方下载（构建时缓存） |
| `tools\__pycache__` | 23 KB | 2 | Python 字节码缓存 | `cpython-315`（Python 3.15） | 本地运行 `preview_final.py` / `watermark_preview7.py` 产生 |

合计：约 **1.05 GB / 11622 个文件**。

## 为什么不入库

- 单一压缩包就 293 MB，超 GitHub 单文件 100 MB 限制，且可用官方包重现。
- SDK 由 `sdkmanager` 或官方 zip 可复现，入库只会让仓库变成二进制垃圾场。
- `__pycache__` 是机器相关缓存，规范明确禁止。

## 需要构建安卓端时怎么复原

```bash
# 1) 下载（或复用 tools\download 里的 zip）
sdkmanager "build-tools;34.0.0" "platforms;android-34"
# 2) 环境变量
export ANDROID_HOME=<SDK_ROOT>
export JAVA_HOME=<JDK17_ROOT>
# 3) 构建（脚本见 src/android/build_*.py 与工作区 android/build.ps1）
```

脚本侧的调用约定（`src/android/` 里的补丁脚本会引用）：

| 变量/路径 | 期望值 |
| --- | --- |
| `JAVA_HOME` | `...\jdk\jdk-17.0.2` |
| `ANDROID_HOME` | `...\tools`（下有 `build-tools\android-14`、`platform\android-34`） |
| `aapt2` | `%ANDROID_HOME%\build-tools\android-14\aapt2.exe` |
| `android.jar` | `%ANDROID_HOME%\platform\android-34\android.jar` |
