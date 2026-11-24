import io

p = 'tools/api_draft.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('''    log("1) 建草稿")
    draft = call("POST", "/api/v1/task-sets/allocate-draft", {})
    tsid = draft.get("task_set_id")
    log("   task_set_id =", tsid, "| 初始状态", draft.get("review_status"))''',
'''    if len(sys.argv) > 2:
        tsid = sys.argv[2]
        log("1) 复用已有草稿", tsid)
    else:
        log("1) 建草稿")
        draft = call("POST", "/api/v1/task-sets/allocate-draft", {})
        tsid = draft.get("task_set_id")
        log("   task_set_id =", tsid, "| 初始状态", draft.get("review_status"))''')

s = s.replace('''    tl = call("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid)
    default_task = (tl.get("records") or [{}])[0]
    log("   默认任务", default_task.get("task_id"))''',
'''    tl = call("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid)
    recs = tl.get("records") or []
    if not recs:
        log("   没有默认任务，创建一个")
        nt = call("POST", "/api/v1/task-sets/%s/tasks/allocate-draft" % tsid, {})
        default_task = nt if nt.get("task_id") else (nt.get("task") or {})
        if not default_task.get("task_id"):
            tl2 = call("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid)
            default_task = (tl2.get("records") or [{}])[0]
    else:
        default_task = recs[0]
    log("   默认任务", default_task.get("task_id"))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
