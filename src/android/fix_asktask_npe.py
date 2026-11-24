"""修「再拍一个区域/任务」闪退：presetArea 为空指针，以及 renderShot 的越界防护。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) presetArea 可能是 null（采集点级任务的 area 为 null）
s = s.replace('''        if (!presetArea.isEmpty()) etTaskName.requestFocus();''',
'''        if (presetArea != null && !presetArea.isEmpty()) etTaskName.requestFocus();''')

# 2) 调用处也兜一下
s = s.replace('''            String area = currentTask < site.tasks.size() ? site.tasks.get(currentTask).area : "";
            askTask(area);''',
'''            String area = "";
            if (currentTask >= 0 && currentTask < site.tasks.size()) {
                String a = site.tasks.get(currentTask).area;
                area = a == null ? "" : a;
            }
            askTask(area);''')

# 3) 新增任务后，确保 shots 索引有效再渲染
s = s.replace('''            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;
            currentShot = 0;
            store.saveQueue(site);
            showPage(2);
            renderShot();''',
'''            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;
            currentShot = firstUndone(currentTask);
            if (currentShot < 0) currentShot = 0;
            store.saveQueue(site);
            try {
                showPage(2);
                renderShot();
            } catch (Exception e) {
                toast("打开拍摄页失败：" + e);
            }''')

io.open(P, 'w', encoding='utf-8').write(s)
print('askTask 空指针已修')
