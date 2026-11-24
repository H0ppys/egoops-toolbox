#!/usr/bin/env bash
set -u
cd /opt/lark-bot || exit 1
export HOME=/root
set -a; . ./config.env; set +a

echo "=== 配置里的 CHAT_ID ==="
echo "$CHAT_ID"

echo
echo "=== 机器人所在群列表 ==="
/usr/local/bin/lark-cli im +chats --as bot 2>&1 | head -60

echo
echo "=== 多维表格字段 ==="
/usr/local/bin/lark-cli base +field-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --format json 2>&1 | head -c 3000
echo
