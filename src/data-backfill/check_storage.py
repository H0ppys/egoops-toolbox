"""查看服务器上「数据库记录」和「磁盘文件」是否一致（有没有删不掉/对不上的备份）。"""

import sys

sys.path.insert(0, ".")

import subprocess

CMD = (
    "cd /opt/egoops/relay && "
    "du -sh data tmp 2>/dev/null; "
    "echo '--- 磁盘文件数'; find data -type f 2>/dev/null | wc -l; "
    "echo '--- 磁盘占用'; du -sb data 2>/dev/null | cut -f1; "
    "echo '--- 数据库记录'; /opt/node22/bin/node -e \""
    "const {DatabaseSync}=require('node:sqlite');"
    "const db=new DatabaseSync('/opt/egoops/relay/db.sqlite');"
    "const r=db.prepare('select count(*) c, coalesce(sum(size),0) s from files').get();"
    "console.log(JSON.stringify(r));\""
)

r = subprocess.run([sys.executable, "ssh_exec.py", CMD], capture_output=True, text=True, encoding="utf-8")
print(r.stdout)
print(r.stderr[-800:] if r.stderr else "")
