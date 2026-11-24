#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>
T=tblzOM1S78dnIf1K

echo "=== 增加「最近入库」字段 ==="
$L base +field-create --base-token "$B" --table-id "$T" \
  --json '[{"name":"最近入库","type":"text"}]' 2>&1 | grep -E '"created"|"message"' | head -2

echo "=== 现有字段 ==="
$L base +field-list --base-token "$B" --table-id "$T" --format json 2>&1 \
  | grep -oE '"name": "[^"]*"' | sed 's/"name": //' | tr -d '"' | nl
