# lark（飞书多维表格读写）

本组 **6** 个脚本。通过 `lark-cli`（bot/user 身份）读写多维表格：字段结构、记录读写、厂商→邀请码→大类同步。

## 代表脚本

- `lark_probe.py` / `lark_read.py` / `lark_read2.py`：表结构与记录抽样
- `patch_feishu.py` / `patch_feishu_sync.py`：给查看器加「直连飞书 OpenAPI」模式（App ID + App Secret）
- `sync_lark_vendors.py`：从「厂家/邀请码/大类」表同步到 relay
- `list_ark_chat.py`：列 Ark 可用 chat 模型（配合 SOP 生成）

## 运行前提

`lark-cli` 与已完成授权的 bot（`--as bot`）；App ID/Secret 用环境变量注入。

## 注意

`app_secret`、`base token` 均已 `<FILL_ME>`。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
