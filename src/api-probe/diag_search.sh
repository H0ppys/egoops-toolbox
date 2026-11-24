#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli

for q in "开机率" "采集员" "作业数据" "具采"; do
  echo "=== 搜索：$q ==="
  $L drive +search --query "$q" --page-size 20 2>&1 \
    | grep -oE '"title": *"[^"]*"|"token": *"[^"]*"|"type": *"[^"]*"' \
    | paste - - - 2>/dev/null | head -12
  echo
done

echo "=== 知识空间 ==="
$L wiki +space-list 2>&1 | grep -oE '"(name|space_id)": *"[^"]*"' | paste - - 2>/dev/null | head -20
