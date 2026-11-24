#!/usr/bin/env bash
set -u
cd /opt/lark-bot || exit 1
export HOME=/root
set -a; . ./config.env; set +a

echo "=== 机器人所在群（bot 身份）==="
/usr/local/bin/lark-cli im +chat-list --as bot --format json 2>&1 | head -c 4000
echo
echo "=== Base 里的数据表 ==="
/usr/local/bin/lark-cli base +table-list --base-token "$BASE_TOKEN" --format json 2>&1 | head -c 2500
echo
echo "=== 全部字段名 ==="
/usr/local/bin/lark-cli base +field-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --format json 2>&1 \
  | grep -o '"name": "[^"]*"' | sed 's/"name": //'
