"""App：场景分类按邀请码从服务器取（失败退回内置全量）。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) loadScenes 改成带邀请码参数
old_start = s.index('    private void loadScenes() {')
old_end = s.index('    /** 从 res/raw/pca.json 读省市区')
old_block = s[old_start:old_end]

new_block = r'''    private void loadScenes() {
        loadScenes(store.invite());
    }

    /** 先用这个邀请码问服务器「你能看到哪些大类」，拿不到就用安装包里的全量 */
    private void loadScenes(final String invite) {
        new Thread(() -> {
            String code = invite == null ? "" : invite.trim().toUpperCase();
            org.json.JSONArray items = null;
            String note = "";
            if (!code.isEmpty()) {
                try {
                    org.json.JSONObject r = api.request("GET",
                            "/api/scenes?vendor=" + android.net.Uri.encode(code), null);
                    items = r.optJSONArray("items");
                    if (items != null && items.length() > 0) {
                        int n = items.length();
                        note = code + " 可见 " + n + " 个场景";
                    }
                } catch (Exception e) {
                    items = null;
                }
            }
            if (items == null || items.length() == 0) {
                try {
                    java.io.InputStream in = getResources().openRawResource(R.raw.scenes);
                    java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
                    in.close();
                    items = new org.json.JSONObject(bos.toString("UTF-8")).optJSONArray("items");
                    note = "离线分类表";
                } catch (Exception e2) {
                    final String msg = e2.getMessage() == null ? e2.toString() : e2.getMessage();
                    runOnUiThread(() -> toast("场景分类读取失败：" + msg));
                    return;
                }
            }

            final List<String[]> list = new ArrayList<String[]>();
            final List<String> cats = new ArrayList<String>();
            for (int i = 0; i < items.length(); i++) {
                org.json.JSONObject o = items.optJSONObject(i);
                if (o == null) continue;
                String path = o.optString("path");
                String label = o.optString("label");
                String cat = o.optString("category");
                String scene = o.optString("scene");
                if (path == null || path.isEmpty()) continue;
                list.add(new String[]{path, label, cat, scene});
                if (!cats.contains(cat)) cats.add(cat);
            }

            final String tip = note;
            runOnUiThread(() -> {
                sceneItems.clear();
                sceneItems.addAll(list);
                categories.clear();
                categories.addAll(cats);

                List<String> catLabels = new ArrayList<String>();
                catLabels.add("① 请选择大类");
                catLabels.addAll(categories);
                if (spCat != null) {
                    spCat.setAdapter(new android.widget.ArrayAdapter<String>(this,
                            android.R.layout.simple_spinner_dropdown_item, catLabels));
                    spCat.setSelection(0);
                    spCat.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
                        @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                            refreshSceneSpinner();
                        }
                        @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
                    });
                }
                refreshSceneSpinner();
                if (tpVendorHint() != null && !tip.isEmpty()) tvVendorHint().setText("分类：" + tip + "（点这里可改邀请码）");
            });
        }).start();
    }

'''
s = s[:old_start] + new_block + s[old_end:]

# 2) 邀请码校验通过后重新加载分类
s = s.replace('''        store.setInvite(code);
        refreshVendorLabel();''',
'''        store.setInvite(code);
        refreshVendorLabel();
        loadScenes(code);''')

# 3) 顶部提示行的辅助方法
if 'tpVendorHint' not in s:
    s = s.replace('''    private void refreshVendorLabel() {''',
'''    private TextView tpVendorHint() {
        return tvVendor;
    }

    private void refreshVendorLabel() {''')

io.open(P, 'w', encoding='utf-8').write(s)
print('App：分类按邀请码加载')
