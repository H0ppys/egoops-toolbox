#!/usr/bin/env bash
set -eu
cd /opt/lark-bot

cp -a config.env "config.env.bak-$(date +%Y%m%d-%H%M%S)"

python3 - <<'PY'
import re
p = '/opt/lark-bot/config.env'
s = open(p, encoding='utf-8').read()

tables = (
    'TABLES='
    '项目生产与日报:tblnGVVPt6RYmnVV,'
    '每日开机播报:tblHjAuEdhi901vN,'
    '具采项目产能汇总:tbljA6GP9vi9zXYI,'
    'KWQX-广州-设备产能统计:tblorr4LiWR9nlBZ:agg,'
    'ZBL-广州-设备产能统计:tblkkXbmtJWBc5MQ:agg,'
    'MT-SY-设备产能统计:tblf0wwdCou84MBw:agg'
)
s = re.sub(r'(?m)^TABLES=.*$', tables, s)
open(p, 'w', encoding='utf-8').write(s)
PY

grep -E '^[A-Z_]+=' config.env | sed -E 's/(LLM_API_KEY)=.*/\1=***/'

systemctl restart lark-bot.service
sleep 5
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 3 -o cat
