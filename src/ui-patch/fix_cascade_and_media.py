"""1) 勾选父级后，子节点（含尚未展开加载的）也跟着勾
2) 建草稿后回查任务，素材数量不一致会明确提示
"""

import io

# ---------------- 查看器：级联 + 懒加载 ----------------
p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 勾父级时：先展开加载，再级联
old = '''        want = self.tree.set(iid, "sel") != "☑"     # 点一下要变成的状态
        self._set_checked(iid, want, cascade=True)   # 勾采集点 = 连带下面全部'''
new = '''        want = self.tree.set(iid, "sel") != "☑"     # 点一下要变成的状态
        if iid in self.site_rows and want and iid not in self.loaded_sites:
            # 还没展开过：先加载，加载完会自动按父级状态补勾
            try:
                self.tree.item(iid, open=True)
                self.on_tree_open(None)
            except Exception:
                pass
        self._set_checked(iid, want, cascade=True)   # 勾采集点 = 连带下面全部'''
assert old in s
s = s.replace(old, new)

# 加载完子节点后，按父级状态补齐勾选
old2 = '''        self.tree.item(iid, open=True)'''
new2 = '''        # 父级已勾选的话，把新加载的子节点也勾上
        if self.tree.set(iid, "sel") == "☑":
            for child in self.tree.get_children(iid):
                self._set_checked(child, True, cascade=True)

        self.tree.item(iid, open=True)'''
assert old2 in s
s = s.replace(old2, new2, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('级联 + 懒加载已修')

# ---------------- 建草稿：回查素材数量 ----------------
p2 = 'viewer/egoops_draft.py'
t = io.open(p2, encoding='utf-8').read()

old3 = '''        log("    已写入：%s（照片 %d，视频 %d，SOP %d 步）" % (task_name, len(photo_ids), len(video_ids), len(content["sop"])))'''
new3 = '''        # 回查：确认素材真的挂上去了
        try:
            chk = _api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid,
                       token=token).get("records") or []
            got = next((x for x in chk if x.get("task_id") == tid), {})
            got_p = len(got.get("task_photos") or [])
            got_v = len(got.get("task_videos") or [])
            if got_p != len(photo_ids) or got_v != len(video_ids):
                log("    ⚠ 回查不一致：本地 照片%d/视频%d，EgoOps 照片%d/视频%d"
                    % (len(photo_ids), len(video_ids), got_p, got_v))
            log("    已写入：%s（照片 %d，视频 %d，SOP %d 步）" % (task_name, got_p, got_v, len(content["sop"])))
            photo_ids, video_ids = [None] * got_p, [None] * got_v
        except Exception as e:
            log("    已写入：%s（照片 %d，视频 %d，SOP %d 步）" % (task_name, len(photo_ids), len(video_ids), len(content["sop"])))
            log("    （回查失败：%s）" % e)'''
assert old3 in t
t = t.replace(old3, new3)

io.open(p2, 'w', encoding='utf-8').write(t)
print('建草稿回查已加')
