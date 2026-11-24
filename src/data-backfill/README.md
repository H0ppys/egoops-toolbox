# data-backfill（数据回填、导入与一致性核对）

本组 **12** 个脚本。把外部数据（Excel 场景表、ndjson、接口分页）回填进 relay SQLite 或飞书表，并做「记录 vs 磁盘」一致性核对与清理。

## 代表脚本

- `import_scenes.py` / `import_vendor_scenes.py` / `importer_three_level.py`：场景分类表导入（支持两级/三级表头、按厂商分离）
- `rebuild_scenes.py`：用官方 Excel 重建 12 domain / 254 scene 并映射回 TET path
- `verify_storage_consistency.py` / `check_storage.py` / `test_delete_frees_disk.py`：数据库记录与磁盘文件核对
- `cleanup_empty_sites.py` / `restore_deletes.py`：空采集点清理与被删数据恢复
- `verify_cross.sh` / `verify_final.sh` / `diag_data.sh`：飞书表与 relay 数据的交叉校验

## 运行前提

`openpyxl`（读 Excel）；`lark-cli` 或 relay HTTP 接口；写库前先备份 `relay.db`。

## 注意

会写数据；`relay.db` 与 `data/` 属运行态，不入库。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
