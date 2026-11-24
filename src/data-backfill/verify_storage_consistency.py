"""核对：数据库里的文件记录 vs 磁盘上的实际文件（找出“删了还在”或“记录在没文件”）。"""

import sys

sys.path.insert(0, ".")

import subprocess

CMD = r"""cd /opt/egoops/relay && /opt/node22/bin/node -e '
const {DatabaseSync}=require("node:sqlite");
const fs=require("fs"); const path=require("path");
const db=new DatabaseSync("/opt/egoops/relay/relay.db");
const rows=db.prepare("select id,path,size from files").all();
let sum=0, missing=0;
const set=new Set();
for (const r of rows){ sum+=r.size||0; const p=path.resolve("/opt/egoops/relay", r.path); set.add(p); if(!fs.existsSync(p)) missing++; }
let disk=0, orphan=[];
function walk(d){ for(const e of fs.readdirSync(d,{withFileTypes:true})){ const p=path.join(d,e.name); if(e.isDirectory()) walk(p); else { disk+=fs.statSync(p).size; if(!set.has(p)) orphan.push(p); } } }
walk("/opt/egoops/relay/data");
console.log(JSON.stringify({db_files:rows.length, db_bytes:sum, disk_bytes:disk, missing_on_disk:missing, orphan_files:orphan.length, orphan_bytes: orphan.reduce((n,p)=>n+fs.statSync(p).size,0)}));
'"""
r = subprocess.run([sys.executable, "ssh_exec.py", CMD], capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
if r.stderr.strip():
    print("ERR:", r.stderr.strip()[-500:])
