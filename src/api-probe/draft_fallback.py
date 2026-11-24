"""让建草稿永不留下空任务：
   · 内容生成失败 → 用模板兜底
   · 每个任务整体 try/except，一个失败不影响其它
   · 无论怎样都要给任务写名称/描述/SOP
   · 出错时把原始异常写进日志，方便定位
"""

import io

P = 'viewer/egoops_draft.py'
s = io.open(P, encoding='utf-8').read()

# 1) 内容生成加兜底
old = '''        # 看图写这个任务的内容
        content, src2 = generate_task_content_from_media(
            site, task, [p for _, p in local_photos], [p for _, p in local_videos])'''
new = '''        # 看图写这个任务的内容（失败就退回模板，绝不让任务空着）
        try:
            content, src2 = generate_task_content_from_media(
                site, task, [p for _, p in local_photos], [p for _, p in local_videos])
        except Exception as e:
            log("    ⚠ 看图/大模型失败（%s），改用模板" % str(e)[:80])
            try:
                content, src2 = generate_task_content(site, task), "template"
            except Exception as e2:
                log("    ⚠ 模板也失败（%s），用最简内容" % str(e2)[:80])
                label_txt = ((task.get("area") or "") + "：" + (task.get("name") or "")).strip("：")
                content = {
                    "name": label_txt or "采集任务",
                    "desc": "在" + (site.get("name") or "") + "采集" + label_txt + "全过程，记录现场环境与操作步骤。",
                    "hours": 0.5,
                    "sop": ["到达采集区域，确认环境光线充足", "用广角拍摄区域全貌", "按步骤完成作业动作",
                            "补拍关键细节，确保画面清晰"],
                }
                src2 = "template"'''
assert old in s
s = s.replace(old, new)

# 2) 文字 PATCH 失败时再试一次（去掉可能不识别的字段）
old2 = '''        try:
            _api("PATCH", "/api/v1/tasks/%s" % tid, base_patch, token=token)
            log("    文字已写入：%s（时长 %s 小时，SOP %d 步）" % (task_name, content["hours"], len(content["sop"])))
        except Exception as e:
            log("    ✗ 写文字失败：%s" % e)'''
new2 = '''        try:
            _api("PATCH", "/api/v1/tasks/%s" % tid, base_patch, token=token)
            log("    文字已写入：%s（时长 %s 小时，SOP %d 步）" % (task_name, content["hours"], len(content["sop"])))
        except Exception as e:
            log("    ✗ 写文字失败：%s，改用最简字段重试" % e)
            try:
                _api("PATCH", "/api/v1/tasks/%s" % tid,
                     {"task_name": task_name, "description": content["desc"]}, token=token)
                log("    已用最简字段写入名称/描述")
            except Exception as e2:
                log("    ✗ 仍然失败：%s" % e2)'''
assert old2 in s
s = s.replace(old2, new2)

io.open(P, 'w', encoding='utf-8').write(s)
print('空任务兜底已加')
