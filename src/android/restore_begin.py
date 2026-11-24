"""补回被误删的 beginShooting（含邀请码、省市区、面积、场景校验）。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

anchor = '    /** 第一个还没拍完的任务下标；全拍完返回 -1 */'
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

'''

s = s.replace(anchor, BLOCK + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('beginShooting 已补回')
