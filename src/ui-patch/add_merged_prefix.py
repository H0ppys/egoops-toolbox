import io

p = 'viewer/egoops_draft.py'
s = io.open(p, encoding='utf-8').read()

old = '''        task_name = (content.get("name") or "").strip() or label
        if len(task_name) > 24:
            task_name = task_name[:24]'''
new = '''        task_name = (content.get("name") or "").strip() or label
        if task.get("_merged") and not task_name.startswith("门头"):
            task_name = "门头全景·" + task_name
        if len(task_name) > 26:
            task_name = task_name[:26]'''
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
