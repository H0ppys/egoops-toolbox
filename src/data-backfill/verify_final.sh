#!/usr/bin/env bash
export HOME=/root
L=/usr/local/bin/lark-cli
B=<FILL_ME>
T=tblzOM1S78dnIf1K
cd /tmp
$L base +record-list --base-token "$B" --table-id "$T" --limit 200 --format json > cross2.json 2>&1
python3 - <<'PY'
import json
d = json.load(open('/tmp/cross2.json', encoding='utf-8'))
if not d.get('ok'):
    print("读取失败:", json.dumps(d.get('error'), ensure_ascii=False)[:300])
    raise SystemExit
names = d['data']['fields']
rows = d['data']['data']
idx = {n: i for i, n in enumerate(names)}
print("行数:", len(rows))
for r in rows:
    if r[idx.get('任务')] == '＝合计＝':
        print("合计:", {n: r[idx[n]] for n in ('录制总数', '总时长（小时）', '质检通过（小时）', '合格率（%）', '大小（GB）')})
    if str(r[idx.get('任务ID')]) == '1041042328' and r[idx.get('执行者')] == '唐朝阳':
        print("唐朝阳·养老院:", {n: r[idx[n]] for n in ('录制总数', '总时长（小时）', '质检通过（小时）', '质检拒绝（小时）', '合格率（%）', '大小（GB）', '最近入库', '最近录制')})
PY
