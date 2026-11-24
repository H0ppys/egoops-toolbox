# bot（飞书机器人巡检）

本组 **5** 个脚本。lark-bot（systemd 服务 `lark-bot.service`）的运行状态、事件流、权限与数据可见性巡检。

## 代表脚本

- `health_bot.sh`：服务 enabled/active、重启次数、内存、最近日志、磁盘
- `watch_bot.sh`：轮询观察（配合 cron/while 使用）
- `probe_bot.sh` / `probe_bot2.sh`：`events.ndjson` 事件类型统计、最近事件、`config.env` 键名
- `check_bot_access.js`：以 bot/user 两种身份读飞书表，确认权限与数据条数

## 运行前提

服务器上需有 `/opt/lark-bot`、`lark-cli`、`systemctl` 权限。

## 注意

只读巡检；`config.env` 只打印键名不打印值。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
