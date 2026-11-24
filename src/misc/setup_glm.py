import io
import json
import os

# ---------- 1) 把 key 写进查看器配置 ----------
cfg_path = os.path.join(os.environ["APPDATA"], "egoops-viewer", "config.json")
cfg = {}
if os.path.exists(cfg_path):
    try:
        cfg = json.load(open(cfg_path, encoding="utf-8"))
    except Exception:
        cfg = {}
cfg["llm"] = {
    "base": "https://ark.cn-beijing.volces.com/api/v3",
    "model": "glm-5-3-flash-260828",
    "key": "<FILL_ARK_API_KEY>",
}
os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
open(cfg_path, "w", encoding="utf-8").write(json.dumps(cfg, ensure_ascii=False, indent=2))
print("配置已写入:", cfg_path)

# ---------- 2) 改 prompt：SOP 要具体、动作化 ----------
p = "viewer/agent_fill.py"
s = io.open(p, encoding="utf-8").read()

old_prompt = s[s.index('def build_task_prompt(site, task):'):s.index('# ---------------------------------------------------------------- 调用')]
new_prompt = '''def build_task_prompt(site, task):
    scene = (site.get("scene_label") or site.get("scene") or "").replace("/", "·")
    return (
        "你在帮数据采集公司填写美团 EgoOps「申请采集点」里每个『任务』的三项内容。\\n"
        "这个任务是采集员拿着手机/头戴设备，在指定区域里做一遍动作并拍下来，用于具身智能训练数据。\\n\\n"
        "要求：\\n"
        "1. desc：60~110 字，写清 作业场景、执行范围（哪个区域）、关键动作、注意事项；\\n"
        "2. hours：按实际耗时估算（0.5~3 之间的数字）；\\n"
        "3. sop：5~7 条，按真实执行顺序，每条 8~18 字，必须动词开头、具体可执行，"
        "要包含『进入区域』『调整视角/构图』『执行任务动作本身』『补拍细节或环绕』『检查画面』『结束并上传』这类环节；"
        "不要写空话（如“按提示完成拍摄”）。\\n\\n"
        "只输出 JSON，不要 markdown 代码块：\\n"
        '{"desc": "...", "hours": 1, "sop": ["...", "..."]}\\n\\n'
        "门店：%s\\n场景分类：%s\\n场地面积：%s 平方米\\n"
        "任务名称：%s\\n所属区域：%s\\n"
        % (site.get("name") or "", scene or "未填", site.get("area") or "未填",
           task.get("name") or "", (task.get("area") or "未填"))
    )


'''
s = s.replace(old_prompt, new_prompt)

# ---------- 3) JSON 提取更稳 ----------
s = s.replace('''        raw = _chat(build_task_prompt(site, task))
        if raw:
            raw = raw.strip().strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
            obj = json.loads(raw)''', '''        raw = _chat(build_task_prompt(site, task))
        if raw:
            obj = _extract_json(raw)''')

s = s.replace('''def generate_description(site):''', '''def _extract_json(text):
    t = text.strip()
    if "```" in t:
        parts = t.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            if part.startswith("{"):
                t = part
                break
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        t = t[start:end + 1]
    return json.loads(t)


def generate_description(site):''')

io.open(p, "w", encoding="utf-8").write(s)
print("prompt 已更新")
