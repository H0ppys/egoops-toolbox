#!/usr/bin/env bash
cd /opt/lark-bot || exit 1
echo "=== 非 cli_stderr / session_end 的事件 ==="
grep -vE '"ev":"(cli_stderr|session_end)"' events.ndjson | cut -c1-700
echo
echo "=== 最后一次 boot 之后是否有 reply 相关 ==="
grep -oE '"ev":"[a-z_]+"' events.ndjson | sort -u
