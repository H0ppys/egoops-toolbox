#!/usr/bin/env bash
set -u
cd /opt/lark-bot || exit 1
export HOME=/root
set -a; . ./config.env; set +a
L=/usr/local/bin/lark-cli

echo "=== BASE_TOKEN 指向的 Base 信息 ==="
$L base +app-info --base-token "$BASE_TOKEN" --format json 2>&1 | head -c 1500
echo
echo "=== base 可用子命令 ==="
$L base --help 2>&1 | grep -E '^\s+\+' | head -40
