#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

echo "=== 删除刚才的临时汇总表 ==="
$L base +table-delete --base-token "$B" --table-id tblvwKgJCvSUs75d --yes 2>&1 | grep -E '"deleted"|"message"' | head -2

FIELDS='[
 {"name":"执行者姓名","type":"text"},
 {"name":"录制总数","type":"number"},
 {"name":"总时长（小时）","type":"number"},
 {"name":"质检通过（小时）","type":"number"},
 {"name":"质检拒绝（小时）","type":"number"},
 {"name":"通过率（%）","type":"number"},
 {"name":"大小（GB）","type":"number"},
 {"name":"最近录制","type":"text"},
 {"name":"更新时间","type":"datetime"}
]'
echo "$FIELDS" > /tmp/final_fields.json

echo "=== 创建最终汇总表 ==="
$L base +table-create --base-token "$B" --name "egoops执行者汇总" --fields "$FIELDS" 2>&1 | grep -oE '"name": "[^"]*"' | head -12
echo
$L base +table-list --base-token "$B" 2>&1 | grep -B1 -A1 'egoops执行者汇总' | head -6
