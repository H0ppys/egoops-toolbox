"""1) 服务器：加 PATCH /api/sites/:id/tasks/:taskId（改任务名/区域）
2) App：填完区域后调用 syncTaskNames()
"""

import io

# ---------- 服务器 ----------
P = 'relay/server.mjs'
s = io.open(P, encoding='utf-8').read()

if 'PATCH' not in s.split('// 申请一个分片上传')[0].split('/api/sites')[-1]:
    anchor = '''    // 申请一个分片上传'''
    block = '''    // 改任务名 / 区域
    m = p.match(/^\\/api\\/sites\\/([^/]+)\\/tasks\\/([^/]+)$/);
    if (m && req.method === 'PATCH') {
      const task = db.prepare('SELECT * FROM tasks WHERE id = ? AND site_id = ?').get(m[2], m[1]);
      if (!task) throw notFound('任务不存在');
      const b = await readJson(req);
      const name = b.name === undefined ? task.name : String(b.name).slice(0, 60);
      const area = b.area === undefined ? task.area : String(b.area).slice(0, 60);
      db.prepare('UPDATE tasks SET name = ?, area = ? WHERE id = ?').run(name, area, task.id);
      return send(res, 200, { task: db.prepare('SELECT * FROM tasks WHERE id = ?').get(task.id) });
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)
    io.open(P, 'w', encoding='utf-8').write(s)
    print('server: PATCH 任务 已加')

# ---------- App ----------
P2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(P2, encoding='utf-8').read()

# showAreaForTask1 填完
old = '''            Model.Task t = site.tasks.get(0);
            t.area = a;
            t.name = n + " · 门头与全景";
            store.saveQueue(site);'''
new = '''            Model.Task t = site.tasks.get(0);
            t.area = a;
            t.name = n + " · 门头与全景";
            store.saveQueue(site);
            syncTaskNamesAsync();'''
if old in t:
    t = t.replace(old, new)
    print('showAreaForTask1：加同步')

# askTask 填完
old2 = '''            currentShot = firstUndone(currentTask);
            if (currentShot < 0) currentShot = 0;
            store.saveQueue(site);'''
new2 = '''            currentShot = firstUndone(currentTask);
            if (currentShot < 0) currentShot = 0;
            store.saveQueue(site);
            syncTaskNamesAsync();'''
if old2 in t:
    t = t.replace(old2, new2, 1)
    print('askTask：加同步')

# 辅助方法
if 'syncTaskNamesAsync' not in t.split('private void askTask')[0]:
    anchor2 = '    private void askTask(String presetArea) {'
    helper = '''    /** 任务名/区域改动后同步到服务器（后台，不打断拍摄） */
    private void syncTaskNamesAsync() {
        try {
            if (site.siteId == null || site.siteId.isEmpty()) return;
            new Thread(() -> {
                try {
                    new Uploader(site, api, store).syncTaskNames();
                } catch (Exception ignored) {
                }
            }).start();
        } catch (Exception ignored) {
        }
    }

'''
    assert anchor2 in t
    t = t.replace(anchor2, helper + anchor2, 1)

io.open(P2, 'w', encoding='utf-8').write(t)
print('App: syncTaskNamesAsync 已加')
