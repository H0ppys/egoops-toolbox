#!/usr/bin/env bash
set -u
cd /opt/lark-bot || exit 1
export HOME=/root
set -a; . ./config.env; set +a

/usr/local/bin/lark-cli base +record-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" \
  --limit 200 --format json > /tmp/rec.json 2>&1

node -e '
const o = JSON.parse(require("fs").readFileSync("/tmp/rec.json","utf8"));
if(!o.ok){ console.log("ERR", JSON.stringify(o.error)); process.exit(0); }
const f = o.data.fields, rows = o.data.data || [];
const ix = Object.fromEntries(f.map((n,i)=>[n,i]));
const get=(r,n)=>{ const i=ix[n]; if(i===undefined) return ""; const v=r[i];
  if(v==null) return ""; if(typeof v==="object"&&Array.isArray(v.value)) return v.value.join("/");
  return String(v); };
console.log("总行数:", rows.length);
const byDate = {};
for(const r of rows){
  const d = get(r,"日期").slice(0,10);
  (byDate[d] ||= []).push(get(r,"采集员姓名")+" 日产出="+get(r,"日产出")+" 蓝牙="+get(r,"蓝牙断联情况"));
}
for(const d of Object.keys(byDate).sort().reverse()) console.log(d, "->", byDate[d].length, "条");
console.log("\n最近日期明细:");
const last = Object.keys(byDate).sort().reverse()[0];
for(const l of (byDate[last]||[])) console.log("  ", l);
'
