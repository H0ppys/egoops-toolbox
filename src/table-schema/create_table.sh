#!/usr/bin/env bash
set -eu
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

test -f /tmp/egoops_fields.json || { echo "字段定义文件缺失"; exit 1; }
FIELDS=$(cat /tmp/egoops_fields.json)

echo "=== 建表 ==="
$L base +table-create --base-token "$B" --name "MTSY-egoops录制数据" --fields "$FIELDS" 2>&1 | head -c 1200
echo
echo "=== 建表后表清单 ==="
$L base +table-list --base-token "$B" --format json 2>&1 \
  | grep -oE '"id": "tbl[^"]*"|"name": "[^"]*"|"records_count": [0-9]+' | paste - - - 2>/dev/null | tail -6
