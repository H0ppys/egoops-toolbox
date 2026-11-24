#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>

FIELDS='[
 {"name":"Token ID","type":"text"},
 {"name":"任务","type":"text"},
 {"name":"采集员","type":"text"},
 {"name":"执行者姓名","type":"text"},
 {"name":"模式","type":"select","multiple":false,"options":[{"name":"被动"},{"name":"主动"}]},
 {"name":"时长（原文）","type":"text"},
 {"name":"时长（秒）","type":"number"},
 {"name":"QC","type":"select","multiple":false,"options":[{"name":"通过"},{"name":"拒绝"},{"name":"待质检"},{"name":"执行失败"}]},
 {"name":"入库时间","type":"datetime"},
 {"name":"片段链接","type":"text"},
 {"name":"批次","type":"text"}
]'

echo "$FIELDS" > /tmp/egoops_fields.json

$L base +table-create --base-token "$B" --name "MTSY-egoops录制数据" --fields "$FIELDS" --dry-run 2>&1 | head -c 2500
