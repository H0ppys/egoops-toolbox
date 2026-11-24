#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
cd /opt/lark-bot || exit 1
set -a; . ./config.env; set +a

echo "=== 当前 BASE_TOKEN 对应的 Base ==="
$L base +base-get --base-token "$BASE_TOKEN" 2>&1 | head -c 1200
echo
echo "=== 我名下/可见的 bitable 文件 ==="
$L drive +search --doc-types bitable --page-size 20 --mine 2>&1 \
  | grep -oE '"(title|token|type|owner_id)": *"[^"]*"' | paste - - - - 2>/dev/null | head -20
echo
echo "--- 全部 bitable（不限 owner）---"
$L drive +search --doc-types bitable --page-size 20 2>&1 \
  | grep -oE '"(title|token)"[^,]*' | head -40
