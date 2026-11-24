import io

p = 'viewer/agent_fill.py'
s = io.open(p, encoding='utf-8').read()

# 模型经常漏掉 name 字段：补一次轻量调用，用步骤反推一个任务名
s = s.replace('''def generate_task_content_from_media(site, task, photo_paths, video_paths):''',
'''def _name_from_steps(seen, desc, steps, task):
    """根据画面内容和步骤反推一个 8~14 字任务名；纯文本调用，快且便宜"""
    try:
        prompt = (
            "下面是一个采集任务看到的画面和要做的事。请起一个任务名称：8~14 个汉字，动宾结构，"
            "要概括这个任务到底在做什么，不要用「拍摄」「采集」「操作过程」这类空泛词。\\n"
            "只输出名称本身，不要引号、不要解释、不要编号。\\n\\n"
            "画面：%s\\n内容：%s\\n步骤：%s\\n原任务名：%s"
            % (seen or "", desc or "", "；".join(steps[:6]), task.get("name") or "")
        )
        text = _chat(prompt, timeout=45)
        if not text:
            return ""
        name = text.strip().strip('"').strip("“”").splitlines()[0].strip()
        name = name.replace("任务名称：", "").replace("名称：", "").strip("。 ，,")
        return name[:20]
    except Exception:
        return ""


def generate_task_content_from_media(site, task, photo_paths, video_paths):''')

s = s.replace('''            if sop:
                return {
                    "name": str(obj.get("name") or "").strip(),''',
'''            if sop:
                name = str(obj.get("name") or "").strip()
                if not name:
                    name = _name_from_steps(obj.get("seen"), obj.get("desc"), sop, task)
                return {
                    "name": name,''')

io.open(p, 'w', encoding='utf-8').write(s)
print('补任务名反推')
