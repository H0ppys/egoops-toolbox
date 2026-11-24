#!/usr/bin/env bash
cd /opt/lark-bot || exit 1

echo "=== ev 类型统计 ==="
if command -v jq >/dev/null 2>&1; then
  jq -r '.ev // "unknown"' events.ndjson 2>/dev/null | sort | uniq -c | sort -rn
else
  grep -o '"ev":"[^"]*"' events.ndjson | sort | uniq -c | sort -rn
fi

echo
echo "=== 最近 12 条事件 ==="
tail -12 events.ndjson | cut -c1-320

echo
echo "=== state.json ==="
cat state.json 2>/dev/null
echo
echo "=== config.env 键名 ==="
cut -d= -f1 config.env
echo "=== 最近活动时间 ==="
ls -l --time-style=full-iso events.ndjson state.json
