# table-schema（表结构建立与校验）

本组 **11** 个脚本。飞书多维表格（Bitable）与 relay SQLite 的建表、重建、字段增补、容量与字段一致性校验。

## 代表脚本

- `create_table.sh` / `create_table_dryrun.sh`：按 FIELDS JSON 建表（dryrun 只打印请求）
- `recreate_table.sh` ~ `recreate_table4.sh`：四种字段集的删表重建（迭代版本，v4 最全）
- `add_fields.sh` / `add_ingest_field.sh`：给已有表补字段（入库时间、来源等）
- `verify_table.sh` / `inspect_tables.js` / `inspect_capacity.js`：字段名/类型核对与行数容量估算

## 运行前提

`lark-cli`（`base +table-create` / `+field-list`）；删表重建不可逆，先备份。

## 注意

`recreate_table*.sh` 会 `+table-delete` 再建，**只在测试基线上跑**；`B=`/`BASE_TOKEN=` 已置 `<FILL_ME>`。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
