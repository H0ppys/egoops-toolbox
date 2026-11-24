import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

old = '''        if (!collector.equals(store.name())) {
            store.setName(collector);
            store.setToken("");
            api.token = "";
        }
        site.name = typed;
        String[] chosen = sceneItems.get(shownIndex.get(p2 - 1));
        site.scene = chosen[0];
        site.sceneLabel = chosen[1];
        site.area = areaVal;
        if (site.tasks.isEmpty()) {
            Model.Task t = new Model.Task();
            t.type = "site";
            t.name = "采集点-门头与全景";
            site.tasks.add(t);
        }
        currentTask = 0;
        currentShot = firstUndone(0);
        showPage(2);
        renderShot();
        if (api.token.isEmpty()) autoLogin();
    }'''

new = '''        if (!collector.equals(store.name())) {
            store.setName(collector);
            store.setToken("");
            api.token = "";
        }
        // 本地队列是上一家店的：门店名变了就当新门店重新开始；同名则接着上次没拍完的继续
        if (!site.name.isEmpty() && !site.name.equals(typed)) {
            site = new Model.Site();
            store.clearQueue();
        }
        site.name = typed;
        String[] chosen = sceneItems.get(shownIndex.get(p2 - 1));
        site.scene = chosen[0];
        site.sceneLabel = chosen[1];
        site.area = areaVal;
        if (site.tasks.isEmpty()) {
            Model.Task t = new Model.Task();
            t.type = "site";
            t.name = "采集点-门头与全景";
            site.tasks.add(t);
        }
        try {
            int t = firstIncompleteTask();
            if (t < 0) {
                // 队列里的都拍完了：直接去结束页，把剩下的传完
                showPage(4);
                if (!uploading) startUpload();
                return;
            }
            currentTask = t;
            currentShot = firstUndone(t);
            showPage(2);
            renderShot();
        } catch (Exception e) {
            toast("开始拍摄失败：" + e);
            return;
        }
        if (api.token.isEmpty()) autoLogin();
    }

    /** 第一个还没拍完的任务下标；全拍完返回 -1 */
    private int firstIncompleteTask() {
        for (int i = 0; i < site.tasks.size(); i++) {
            Model.Task t = site.tasks.get(i);
            if (firstUndone(i) < shotsOf(t).length) return i;
        }
        return -1;
    }'''

assert old in s
s = s.replace(old, new)

# renderShot 入口加保护：下标越界就回到第一个未完成项 / 跳完成页
old2 = '''    private void renderShot() {
        shotArea.removeAllViews();
        Model.Task task = task(currentTask);
        String[][] shots = shotsOf(task);
        int idx = currentShot;'''
new2 = '''    private void renderShot() {
        shotArea.removeAllViews();
        Model.Task task = task(currentTask);
        String[][] shots = shotsOf(task);
        if (currentShot < 0 || currentShot >= shots.length) {
            currentShot = firstUndone(currentTask);
            if (currentShot >= shots.length) {
                tvTaskDoneTitle.setText(labelOf(task) + " 拍完了");
                tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有区域或任务要拍吗？");
                showPage(3);
                return;
            }
        }
        int idx = currentShot;'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
