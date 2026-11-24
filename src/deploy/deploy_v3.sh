#!/usr/bin/env bash
set -eu
cd /opt/lark-bot

cp -a config.env "config.env.bak-$(date +%Y%m%d-%H%M%S)"

python3 - <<'PY'
import re, io
p = '/opt/lark-bot/config.env'
s = open(p, encoding='utf-8').read()

s = re.sub(r'(?m)^BASE_TOKEN=.*$', 'BASE_TOKEN=<FILL_ME>', s)

tables = 'TABLES=项目生产与日报:tblnGVVPt6RYmnVV,每日开机播报:tblHjAuEdhi901vN'
if re.search(r'(?m)^TABLES=', s):
    s = re.sub(r'(?m)^TABLES=.*$', tables, s)
elif re.search(r'(?m)^TABLE_ID=', s):
    s = re.sub(r'(?m)^TABLE_ID=.*$', tables, s)
else:
    s = s.rstrip('\n') + '\n' + tables + '\n'

open(p, 'w', encoding='utf-8').write(s)
PY

echo "=== 新配置（键值，不打印密钥）==="
grep -E '^[A-Z_]+=' config.env | sed -E 's/(LLM_API_KEY)=.*/\1=***/'

echo "=== 重启 ==="
systemctl restart lark-bot.service
sleep 5
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 4 -o cat
