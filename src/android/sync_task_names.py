"""修：区域/动作填完后立刻把任务名和区域同步到服务器。

原因：拍完第 3 项就触发上传，上传前会把当时的任务名（"任务1"、区域空）建到服务器；
之后弹窗填的区域和动作只改了本地，服务器没更新，所以后台数据里看不到。
"""

import io

# ---------- 1) Uploader：加一个只同步任务名/区域的公开方法 ----------
P = 'android/src/com/egoops/collect/Uploader.java'
s = io.open(P, encoding='utf-8').read()

if 'public void syncTaskNames' not in s:
    anchor = '    /** 把后加的区域任务登记到服务器，拿回 task_id */'
    block = '''    /** 任务名/区域改了以后同步到服务器（不动素材） */
    public void syncTaskNames() {
        try {
            if (site.siteId == null || site.siteId.isEmpty()) return;
            for (Model.Task t : site.tasks) {
                if (t.serverId == null || t.serverId.isEmpty()) continue;
                JSONObject body = new JSONObject();
                body.put("name", t.name == null ? "" : t.name);
                body.put("area", t.area == null ? "" : t.area);
                api.request("PATCH", "/api/sites/" + site.siteId + "/tasks/" + t.serverId, body);
            }
        } catch (Exception ignored) {
        }
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)
    io.open(P, 'w', encoding='utf-8').write(s)
    print('Uploader.syncTaskNames 已加')

# ---------- 2) MainActivity：填完区域后调用 ----------
P2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(P2, encoding='utf-8').read()

old = '''            Model.Task t = site.tasks.get(0);
            t.area = a;
            t.name = n + " · 门头与全景";
            store.saveQueue(site);'''
new = '''            Model.Task t = site.tasks.get(0);
            t.area = a;
            t.name = n + " · 门头与全景";
            store.saveQueue(site);
            // 上传线程可能已经把旧名字建到服务器了，这里立刻改回去
            final Model.Site snap = site;
            new Thread(() -> {
                try {
                    Uploader u = new Uploader(snap, api, store);
                    u.syncTaskNames();
                } catch (Exception ignored) {
                }
            }).start();'''
assert old in t
t = t.replace(old, new)

# 普通区域任务也一样
old2 = '''            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;'''
new2 = '''            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;
            new Thread(() -> {
                try {
                    new Uploader(site, api, store).syncTaskNames();
                } catch (Exception ignored) {
                }
            }).start();'''
assert old2 in t
t = t.replace(old2, new2, 1)

io.open(P2, 'w', encoding='utf-8').write(t)
print('MainActivity 已调用同步')
