#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

echo "=== 删除任务级表 ==="
$L base +table-delete --base-token "$B" --table-id tblry6YJn801c0yt --yes 2>&1 | grep -E '"deleted"' | head -1

FIELDS='[
 {"name":"任务","type":"text"},
 {"name":"任务ID","type":"text"},
 {"name":"一级场景","type":"text"},
 {"name":"二级场景","type":"text"},
 {"name":"执行者","type":"text"},
 {"name":"录制总数","type":"number"},
 {"name":"总时长（小时）","type":"number"},
 {"name":"质检通过（小时）","type":"number"},
 {"name":"质检拒绝（小时）","type":"number"},
 {"name":"合格率（%）","type":"number"},
 {"name":"大小（GB）","type":"number"},
 {"name":"最近录制","type":"text"},
 {"name":"更新时间","type":"datetime"}
]'
echo "$FIELDS" > /tmp/cross_fields.json

echo "=== 创建任务×执行者表 ==="
$L base +table-create --base-token "$B" --name "egoops任务执行者合格率" --fields "$FIELDS" 2>&1 | grep -c '"name"'
$L base +table-list --base-token "$B" 2>&1 | grep -B2 'egoops任务执行者合格率' | head -4
