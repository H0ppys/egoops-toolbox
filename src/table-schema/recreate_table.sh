#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

echo "=== 删除旧明细表 ==="
$L base +table-delete --base-token "$B" --table-id tblc9lzxiDYJZA9d --yes 2>&1 | head -c 400
echo

FIELDS='[
 {"name":"执行者姓名","type":"text"},
 {"name":"录制总数","type":"number"},
 {"name":"总时长（小时）","type":"number"},
 {"name":"质检通过（小时）","type":"number"},
 {"name":"质检拒绝（小时）","type":"number"},
 {"name":"其他/待质检（小时）","type":"number"},
 {"name":"通过率（%）","type":"number"},
 {"name":"大小（GB）","type":"number"},
 {"name":"更新时间","type":"datetime"}
]'
echo "$FIELDS" > /tmp/agg_fields.json

echo "=== 创建汇总表 ==="
$L base +table-create --base-token "$B" --name "egoops执行者汇总" --fields "$FIELDS" 2>&1 | head -c 500
echo
echo "=== 当前表清单 ==="
$L base +table-list --base-token "$B" 2>&1 | grep -oE '"id": "tbl[^"]*"|"name": "[^"]*"|"records_count": [0-9]+' | paste - - - | tail -4
