#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>
T=tblc9lzxiDYJZA9d

echo "=== 新表字段 ==="
$L base +field-list --base-token "$B" --table-id "$T" --format json 2>&1 \
  | grep -oE '"name": "[^"]*"|"type": "[a-z]+"' | paste - -

echo
echo "=== 是否 BaseApp（页面/分组）==="
$L base +app-get --base-token "$B" 2>&1 | head -c 900
