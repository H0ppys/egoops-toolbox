# android（安卓采集端（Java / 构建 / 发布））

本组 **102** 个脚本。采集 App（`com.egoops.collect`）的 MainActivity/WatermarkVideo/Uploader 补丁，以及版本号、构建变体、APK 发布。

## 代表脚本

- `android_task1_9items.py` / `shots_restructure.py` / `android_merge_task1.py`：拍摄项结构改造
- `unify_watermark_style.py` / `java_watermark_v2.py` / `java_watermark_v3.py`：把预览参数落到 `WatermarkVideo.drawStamp()`
- `real_gps_watermark.py` / `fix_gps_accuracy.py` / `dynamic_time.py`：定位与拍摄时间写进水印
- `build_nocapture.py` / `nocap_code.py` / `enhance_nocap.py`：不拍摄版本（只从相册选、不烧水印）
- `bump*.py` / `build_version_sync.py` / `fix_rename_pkg.py` / `fix_rpackage.py`：版本号与包名/R 类
- `app_update.py` / `publish_apk.py` / `wire_tls_android.py`：自更新、发布、证书固定

## 运行前提

Android SDK（`build-tools;34.0.0`、`platforms;android-34`）+ JDK 17，见 [../docs/TOOLCHAIN.md](../docs/TOOLCHAIN.md)。

## 注意

脚本按锚点改 `MainActivity.java`；改完需 `build.ps1` 重新编译。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
