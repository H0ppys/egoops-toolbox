"""按 EgoOps「申请采集点」真实表单结构生成草稿（HTML），任务级字段由 agent 补全。"""
import html
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://<FILL_ME>/relay"
SITE_INDEX = int(sys.argv[2]) if len(sys.argv) > 2 else 0
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode() or "{}")


def human(n):
    n = float(n or 0)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%d %s" % (n, u)) if u == "B" else ("%.1f %s" % (n, u))
        n /= 1024


tok = call("POST", "/api/auth/login", {"name": "草稿预览"})["token"]
sites = call("GET", "/api/sites", token=tok)["items"]
sites.sort(key=lambda s: s.get("created_at") or "", reverse=True)
site = call("GET", "/api/sites/" + sites[min(SITE_INDEX, len(sites) - 1)]["id"], token=tok)

desc, desc_src = ("", "现有")
if not (site.get("note") or "").strip():
    desc, desc_src = generate_description(site)

tasks = site.get("tasks") or []
task_blocks = []
for t in tasks:
    content, src = generate_task_content(site, t)
    photos = t.get("photos") or []
    videos = t.get("videos") or []
    task_blocks.append({
        "title": ((t.get("area") + " ") if (t.get("area") or "").strip() else "") + (t.get("name") or ""),
        "area": t.get("area") or "",
        "desc": content["desc"],
        "hours": content["hours"],
        "sop": content["sop"],
        "photos": photos,
        "videos": videos,
        "src": src,
    })

esc = html.escape
addr = site.get("address") or ""

css = """
body{margin:0;padding:28px;background:#eef2f8;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#17202e}
.card{max-width:900px;margin:0 auto;background:#fff;border-radius:16px;padding:26px 30px;box-shadow:0 8px 28px rgba(23,32,46,.08)}
h1{font-size:21px;margin:0 0 2px}.sub{color:#6b7a90;font-size:12px;margin-bottom:18px}
.lbl{color:#6b7a90;font-size:13px;margin-top:14px}
.val{border:1px solid #e6ecf4;border-radius:8px;padding:9px 11px;font-size:14px;background:#fbfcfe}
.req{color:#c0392b}
.tag{display:inline-block;background:#f3ecff;color:#7a3ff2;border-radius:6px;padding:1px 7px;font-size:11px;margin-left:6px;vertical-align:middle}
.task{border:1px solid #e6ecf4;border-radius:12px;padding:14px 16px;margin-top:12px}
.task h3{margin:0 0 6px;font-size:15px}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.chip{background:#eef4ff;color:#2f6fed;border-radius:999px;padding:3px 10px;font-size:12px}
.sop{margin:8px 0 0;padding-left:18px;font-size:13px;color:#39465a}
.sop li{margin:3px 0}
.files{margin-top:8px;font-size:12px;color:#6b7a90}
.warn{color:#c0392b}
"""

parts = []
parts.append('<div class="card">')
parts.append("<h1>申请采集点 · 草稿</h1>")
parts.append('<div class="sub">采集员 %s · %d 个任务 · 生成于 %s</div>'
             % (esc(site.get("created_by") or ""), len(tasks), esc((site.get("created_at") or "")[:16])))

parts.append('<div class="lbl">采集点名称 <span class="req">*</span></div><div class="val"><b>%s</b></div>' % esc(site.get("name") or ""))
parts.append('<div class="lbl">采集场景分类 <span class="req">*</span></div><div class="val">%s</div>'
             % esc(site.get("scene_label") or site.get("scene") or "（未选）"))
parts.append('<div class="lbl">现场地址 <span class="req">*</span></div><div class="val">%s</div>'
             % (esc(addr) if addr else '<span class="warn">（未采集：省 / 市 / 区 + 街道门牌号，需要人工补）</span>'))
parts.append('<div class="lbl">采集点描述 <span class="req">*</span></div><div class="val">%s%s</div>'
             % (esc(desc), '<span class="tag">AI 补全</span>' if desc_src != "现有" else ""))

parts.append('<h3 style="margin:22px 0 0;font-size:15px">作业任务</h3>')
for i, b in enumerate(task_blocks, 1):
    parts.append('<div class="task">')
    parts.append("<h3>任务 %d　%s</h3>" % (i, esc(b["title"])))
    parts.append('<div class="lbl">任务描述 <span class="req">*</span></div><div class="val">%s%s</div>'
                 % (esc(b["desc"]), '<span class="tag">AI 补全</span>'))
    parts.append('<div class="lbl">预计时长（小时） <span class="req">*</span></div><div class="val">%g</div>' % b["hours"])
    parts.append('<div class="lbl">SOP 步骤 <span class="req">*</span></div><ul class="sop">')
    for s in b["sop"]:
        parts.append("<li>%s</li>" % esc(s))
    parts.append("</ul>")
    parts.append('<div class="files">任务照片 %d 张 · 任务视频 %d 个</div>' % (len(b["photos"]), len(b["videos"])))
    parts.append("</div>")

parts.append('<div class="sub" style="margin-top:20px">这是提交前核对稿，尚未提交到 EgoOps。紫色标签为 agent 生成内容。</div>')
parts.append("</div>")

doc = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>申请采集点草稿</title><style>%s</style></head><body>%s</body></html>' % (css, "".join(parts))

name = (site.get("name") or "site").replace("/", "_").replace("\\", "_")
path = os.path.join(OUT_DIR, "草稿-%s.html" % name)
open(path, "w", encoding="utf-8").write(doc)

print("采集点：", site.get("name"), "| 任务", len(tasks))
for b in task_blocks:
    print("  -", b["title"], "| 时长", b["hours"], "| SOP", len(b["sop"]), "条 | 来源", b["src"])
print("草稿：", path)
