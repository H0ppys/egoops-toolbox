"""补回 beginShooting / firstIncompleteTask / installCrashReporter。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

anchor = '    private void confirmRestart() {'
assert anchor in s

BLOCK = r'''    private void beginShooting() {
        String collector = etCollector.getText().toString().trim();
        if (collector.isEmpty()) {
            toast("请先填写采集员姓名");
            etCollector.requestFocus();
            return;
        }

        String invite = etInvite == null ? store.invite() : etInvite.getText().toString().trim();
        invite = invite == null ? "" : invite.toUpperCase();
        if (invite.isEmpty()) {
            toast("请填写邀请码");
            if (etInvite != null) etInvite.requestFocus();
            return;
        }
        store.setInvite(invite);

        String typed = etStoreName.getText().toString().trim();
        if (typed.isEmpty()) {
            toast("请先填写门店名称");
            etStoreName.requestFocus();
            return;
        }

        int pi = spProv.getSelectedItemPosition();
        int ci = spCity.getSelectedItemPosition();
        int di = spDist.getSelectedItemPosition();
        if (pi <= 0 || ci < 0 || di < 0) {
            toast("请先选择省 / 市 / 区");
            return;
        }
        String street = etStreet.getText().toString().trim();
        if (street.isEmpty()) {
            toast("请填写街道门牌号");
            etStreet.requestFocus();
            return;
        }
        String provName = provArr[pi];
        String cityName = cityArr[pi - 1][ci];
        String distName = distArr[pi - 1][ci][di];
        String addr = provName + ("市辖区".equals(cityName) ? "" : cityName) + distName + street;

        if (sceneItems.isEmpty()) {
            toast("场景分类还没准备好，请稍等");
            loadScenes();
            return;
        }
        int p2 = spScene2.getSelectedItemPosition();
        if (p2 < 0 || p2 >= shownIndex.size()) {
            toast("请选择采集场景分类（先选大类，再选具体场景）");
            spScene2.performClick();
            return;
        }

        String areaTxt = etArea.getText().toString().trim();
        double areaVal = 0;
        try { areaVal = areaTxt.isEmpty() ? 0 : Double.parseDouble(areaTxt); } catch (Exception e) { areaVal = 0; }
        if (!(areaVal > 0)) {
            toast("请填写场地面积（平方米）");
            etArea.requestFocus();
            return;
        }

        if (!collector.equals(store.name())) {
            store.setName(collector);
            store.setToken("");
            api.token = "";
        }
        if (!site.name.isEmpty() && !site.name.equals(typed)) {
            site = new Model.Site();
            store.clearQueue();
        }
        site.name = typed;
        site.address = addr;
        site.invite = invite;
        String[] chosen = sceneItems.get(shownIndex.get(p2));
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
    }

    /** 闪退时把堆栈写到本地并上报服务器 */
    private void installCrashReporter() {
        final Thread.UncaughtExceptionHandler def = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((t, e) -> {
            try {
                java.io.StringWriter sw = new java.io.StringWriter();
                e.printStackTrace(new java.io.PrintWriter(sw));
                String stack = sw.toString();
                if (stack.length() > 6000) stack = stack.substring(0, 6000);
                try {
                    java.io.File dir = new java.io.File(getExternalFilesDir(null), "crash");
                    dir.mkdirs();
                    java.io.File f = new java.io.File(dir, "crash-" + System.currentTimeMillis() + ".txt");
                    java.io.FileWriter w = new java.io.FileWriter(f);
                    w.write(stack);
                    w.close();
                } catch (Throwable ignored) { }
                try {
                    org.json.JSONObject o = new org.json.JSONObject();
                    o.put("name", store == null ? "" : store.name());
                    o.put("message", String.valueOf(e));
                    o.put("stack", stack);
                    o.put("task", currentTask + "/" + currentShot);
                    byte[] body = o.toString().getBytes("UTF-8");
                    java.net.HttpURLConnection c = (java.net.HttpURLConnection)
                            new java.net.URL(api.base + "/api/client-log").openConnection();
                    c.setRequestMethod("POST");
                    c.setConnectTimeout(3000);
                    c.setReadTimeout(3000);
                    c.setDoOutput(true);
                    c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                    c.setFixedLengthStreamingMode(body.length);
                    c.getOutputStream().write(body);
                    c.getResponseCode();
                    c.disconnect();
                } catch (Throwable ignored) { }
            } catch (Throwable ignored) { }
            if (def != null) def.uncaughtException(t, e);
        });
    }

'''

s = s.replace(anchor, BLOCK + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('补回 3 个方法，当前行数:', len(s.splitlines()))
