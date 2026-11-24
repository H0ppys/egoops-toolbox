#!/usr/bin/env bash
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>
T=tblzOM1S78dnIf1K

cd /tmp
$L base +record-list --base-token "$B" --table-id "$T" --limit 200 --format json > cross.json 2>&1

python3 - <<'PY'
import json
d = json.load(open('/tmp/cross.json', encoding='utf-8'))
names = d['data']['fields']
rows = d['data']['data']
idx = {n: i for i, n in enumerate(names)}
print("字段顺序:", " | ".join(names))
print("总行数:", len(rows))
print()
for r in rows:
    if str(r[idx.get('任务ID')]) == '1041042328' and r[idx.get('执行者')] == '唐朝阳':
        print("✓ 任务1041042328 + 唐朝阳:")
        for n in names:
            print(f"   {n}: {r[idx[n]]}")
    if r[idx.get('任务')] == '＝合计＝':
        print("✓ 合计行:")
        for n in names:
            print(f"   {n}: {r[idx[n]]}")
PY
