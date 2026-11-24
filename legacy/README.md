# legacy/ 为什么是空的

按 [CONVENTIONS.md](../docs/SPLIT.md) 的要求，拆分类仓库通常要在 `legacy/` 放一份**逐字节一致**的原始文件镜像作为只读参照。本仓有意不这么做：

1. 原始脚本里直接写着真实的生产口令、飞书 base token、高德地图 Key、生产主机 IP、手机号与 open_id。
2. 硬要求是「真实值绝不进仓库」，而逐字节镜像与脱敏天然冲突。
3. 因此本仓只保留**脱敏后的唯一副本**（`src/`），脱敏只把值替换成 `<FILL_ME>`，函数体、锚点字符串、调用顺序逐字未动（见 [SECRETS.md](../docs/SECRETS.md) 的 86 处位置记录）。

如果需要回看原始文件：都在原始工作区 `C:\Users\Administrator\Documents\deepseek-harness\default-workspace`（工作区根目录 / `tools\` / `deploy\`），本仓的 [SPLIT.md](../docs/SPLIT.md) 给了逐文件对应关系。
