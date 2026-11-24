#!/usr/bin/env bash
set -eu
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>
T=tblc9lzxiDYJZA9d

FIELDS='[
 {"name":"大小（GB）","type":"number"},
 {"name":"录制时间","type":"datetime"},
 {"name":"设备 SN","type":"text"},
 {"name":"数据源节点","type":"text"},
 {"name":"质检结果","type":"text"}
]'

echo "$FIELDS" > /tmp/extra_fields.json
$L base +field-create --base-token "$B" --table-id "$T" --json "$FIELDS" 2>&1 | head -c 900
echo
echo "=== 最终字段清单 ==="
$L base +field-list --base-token "$B" --table-id "$T" --format json 2>&1 \
  | grep -oE '"name": "[^"]*"' | sed 's/"name": //' | tr -d '"' | nl
