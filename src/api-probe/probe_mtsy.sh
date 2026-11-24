#!/usr/bin/env bash
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

echo "=== 现有 MTSY具采_执行者录制数据 字段 ==="
$L base +field-list --base-token $B --table-id tbl1re75u4EhBFuN --format json 2>&1 \
  | grep -oE '"name": "[^"]*"|"type": [0-9]+' | paste - - | head -30

echo
echo "=== 该表样例 2 行 ==="
$L base +record-list --base-token $B --table-id tbl1re75u4EhBFuN --limit 2 --format json --as bot 2>&1 | head -c 1200

echo
echo "=== table-create 用法 ==="
$L base +table-create --help 2>&1 | head -40
