# 样例数据（examples）

从 `sim\` 里挑出的**极小文本样例**，每条 ≤ 2KB，已脱敏。二进制样本（jpg/mp4）与整目录导出不进仓库。

| 文件 | 大小 | 原路径 | 说明 |
| --- | --- | --- | --- |
| `all_scenes_head.txt` | 1457 B | `sim\all_scenes.txt` | 见文件头 |
| `export_sample.csv` | 350 B | `sim\export.csv` | 见文件头 |
| `lark_q.json` | 14 B | `sim\lark_q.json` | 见文件头 |
| `restricted_sample.json` | 787 B | `sim\restricted.json` | 见文件头 |
| `scene_dump.txt` | 916 B | `sim\scene_dump.txt` | 见文件头 |
| `site_id.txt` | 20 B | `sim\site_id.txt` | 见文件头 |
| `xlsx_domains.json` | 1391 B | `sim\xlsx_domains.json` | 见文件头 |
| `xlsx_probe.json` | 1848 B | `sim\xlsx_probe.json` | 见文件头 |

## 未纳入的 sim 内容

| 原路径 | 大小 | 原因 |
| --- | --- | --- |
| `sim\blur.jpg` / `dark.jpg` / `sharp.jpg` / `vision_probe.jpg` | 23–45 KB | 图片样本，供质检阈值（模糊/亮度）校准用，二进制不入库 |
| `sim\video_h264.mp4` / `video_hevc.mp4` | 1.0–1.5 MB | 转码对比样本 |
| `sim\dl_check\*`（15 个 jpg/mp4） | 44 MB | 下载完整性校验的真实素材 |
| `sim\dl_test\盛宴便利店\*` | 8.7 MB | 断点续传测试产物（含 `.part` 半文件） |
| `sim\scenes_old.json` | 58 KB | 旧版场景表全量，已被 `examples\xlsx_domains.json` 概括 |
| `sim\ui_block.txt` | 17 KB | 界面代码片段，属源码不属样例 |
| `sim\import_test.txt` | 1.8 KB | 控制台输出被 UTF-16 转码损坏（大量替换符），无参考价值 |
| `sim\lark_records.json` | 0 字节 | 空文件 |
