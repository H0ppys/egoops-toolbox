"""从 Ark /models 里挑出支持 chat/completions 的模型 id。"""
import os
import json
import urllib.request

KEY = os.environ.get("ARK_API_KEY", "<FILL_ARK_API_KEY>")
BASE = "https://ark.cn-beijing.volces.com/api/v3"

req = urllib.request.Request(BASE + "/models")
req.add_header("Authorization", "Bearer " + KEY)
data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
items = data.get("data") or []
print("总模型数:", len(items))

chat = []
for m in items:
    api = m.get("api_supported") or {}
    if api.get("chat/completions"):
        chat.append(m)

print("支持 chat 的:", len(chat))
for m in chat:
    print(" -", m.get("id"), "|", m.get("name"), "| ctx", m.get("context_window"), "|", m.get("status"))

print("\n含 glm 的:", [m.get("id") for m in items if "glm" in (m.get("id") or "").lower()])
