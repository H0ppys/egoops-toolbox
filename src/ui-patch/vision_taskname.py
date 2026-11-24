import io

p = 'viewer/agent_fill.py'
s = io.open(p, encoding='utf-8').read()

# 1) 提示词：连任务名称也由画面决定，SOP 一行一条
s = s.replace('''        "要求：\\n"
        "1. desc：60~110 字，要写**画面里真实看到的东西**（具体物件、位置），不要套话；\\n"
        "2. hours：按实际耗时估算，0.5~3 的数字；\\n"
        "3. sop：5~7 条，按真实执行顺序，每条 8~18 字，动词开头，"
        "必须和画面里出现的东西对应（比如画面里是货架就写走到货架前，是机器就写操作机器）；\\n"
        "4. seen：一句话描述你从画面里看到了什么。\\n\\n"
        "只输出 JSON，不要代码块：\\n"
        '{"seen": "...", "desc": "...", "hours": 1, "sop": ["...", "..."]}\\n\\n' ''',
'''        "要求：\\n"
        "1. name：任务名称，8~14 字，动宾结构，必须来自画面（比如画面里在擦显示器，就写「擦拭显示器与桌面」）；\\n"
        "2. desc：60~110 字，写**画面里真实看到的东西**（具体物件、位置、动作），不要套话；\\n"
        "3. hours：按实际耗时估算，0.5~3 的数字；\\n"
        "4. sop：5~7 条，**一条只写一个动作**，每条 8~18 字，动词开头，"
        "必须和画面里的东西对应；不要用分号把两个动作挤在一条里；\\n"
        "5. seen：一句话描述你从画面里看到了什么。\\n\\n"
        "只输出 JSON，不要代码块：\\n"
        '{"seen": "...", "name": "...", "desc": "...", "hours": 1, "sop": ["一条一个动作", "..."]}\\n\\n' ''')

# 2) 返回值带上 name
s = s.replace('''            if sop:
                return {
                    "desc": str(obj.get("desc") or "").strip(),
                    "hours": float(obj.get("hours") or 1),
                    "sop": sop,
                    "seen": str(obj.get("seen") or "").strip(),
                }, "vision"''',
'''            if sop:
                return {
                    "name": str(obj.get("name") or "").strip(),
                    "desc": str(obj.get("desc") or "").strip(),
                    "hours": float(obj.get("hours") or 1),
                    "sop": sop,
                    "seen": str(obj.get("seen") or "").strip(),
                }, "vision"''')

# 3) 纯文本兜底也带 name
s = s.replace('''    return {"desc": desc, "hours": hours, "sop": sop}''',
              '''    return {"name": name, "desc": desc, "hours": hours, "sop": [s for s in sop if s]}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('提示词: 加任务名称 + SOP 一行一条')

# 4) 建草稿时任务名用模型给的
p2 = 'viewer/egoops_draft.py'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('''    _api("PATCH", "/api/v1/tasks/%s" % tid, {
        "task_name": label,''', '''    task_name = (content.get("name") or "").strip() or label
    if len(task_name) > 24:
        task_name = task_name[:24]
    step(96, "任务名称：%s" % task_name)
    _api("PATCH", "/api/v1/tasks/%s" % tid, {
        "task_name": task_name,''')

t = t.replace('''    return {
        "task_set_id": tsid,''', '''    return {
        "task_set_id": tsid,
        "task_name": task_name,''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('建草稿: 任务名用模型生成的')
