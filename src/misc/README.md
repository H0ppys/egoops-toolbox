# misc（水印样式预览与杂项）

本组 **25** 个脚本。水印视觉复刻（对照「今日水印相机」参考图逐像素度量）、真实照片/视频上水印的效果验证，以及少量一次性实验脚本。

## 代表脚本

- `watermark_preview*.py`（7 版）：按参考图比例迭代水印排版
- `measure_mine.py` / `measure_ref.py` / `shrink_watermark.py` / `size38.py` / `tune7*.py`：尺寸与配色微调
- `preview_final.py` / `preview_with_map.py`：与 Java 端参数一致的效果图
- `calib_thresholds.py` / `calibrate_qc.py`：用真实照片校准清晰度/亮度阈值
- `app2_polish.py` / `setup_glm.py`：查看器小改与 GLM 配置

## 运行前提

`Pillow`、`numpy`；需要参考图与真实素材（不入库）。

## 注意

输出 PNG 属运行产物，不入库。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
