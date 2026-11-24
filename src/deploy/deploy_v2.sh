#!/usr/bin/env bash
set -u
cd /opt/lark-bot || exit 1

# 规范化备份名
if [ -f bot.js.bak- ] && [ ! -f bot.js.bak-20261119 ]; then
  mv bot.js.bak- bot.js.bak-20261119-1035
fi
ls -l bot.js* | cat

# 群白名单注释更新（CHAT_ID 已不再使用；CHAT_IDS 留空=任意群）
if grep -q '^CHAT_ID=' config.env; then
  sed -i 's/^CHAT_ID=.*/# 已废弃：v2 用 CHAT_IDS（逗号分隔，留空=任意群 @机器人 都回复）\n# CHAT_ID=/' config.env
fi
grep -nE 'CHAT_ID|CHAT_IDS' config.env || true

echo "=== 重启服务 ==="
systemctl restart lark-bot.service
sleep 6
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 6 -o cat
