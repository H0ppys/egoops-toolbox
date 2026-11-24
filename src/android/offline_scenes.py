import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 场景分类完全本地：不再请求服务器
start = s.index('    private void loadScenes() {')
end = s.index('    /** 从 res/raw/pca.json 读省市区')
new = '''    private void loadScenes() {
        // 场景分类和省市一样，直接读安装包里的表，完全离线
        new Thread(() -> {
            try {
                java.io.InputStream in = getResources().openRawResource(R.raw.scenes);
                java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
                in.close();
                org.json.JSONArray items = new org.json.JSONObject(bos.toString("UTF-8")).optJSONArray("items");
                final List<String[]> list = new ArrayList<String[]>();
                final List<String> cats = new ArrayList<String>();
                if (items != null) {
                    for (int i = 0; i < items.length(); i++) {
                        org.json.JSONObject o = items.optJSONObject(i);
                        String path = o.optString("path");
                        String label = o.optString("label");
                        String cat = o.optString("category");
                        if (path.isEmpty()) continue;
                        list.add(new String[]{path, label, cat});
                        if (!cats.contains(cat)) cats.add(cat);
                    }
                }
                runOnUiThread(() -> {
                    sceneItems.clear();
                    sceneItems.addAll(list);
                    categories.clear();
                    categories.addAll(cats);

                    List<String> catLabels = new ArrayList<String>();
                    catLabels.add("全部分类");
                    catLabels.addAll(categories);
                    spCat.setAdapter(new android.widget.ArrayAdapter<String>(this,
                            android.R.layout.simple_spinner_dropdown_item, catLabels));
                    spCat.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
                        @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                            refreshSceneSpinner();
                        }
                        @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
                    });
                    if (site.scene != null && !site.scene.isEmpty()) {
                        for (int i = 0; i < sceneItems.size(); i++) {
                            if (sceneItems.get(i)[0].equals(site.scene)) {
                                int c = categories.indexOf(sceneItems.get(i)[2]);
                                if (c >= 0) spCat.setSelection(c + 1);
                                break;
                            }
                        }
                    }
                    refreshSceneSpinner();
                });
            } catch (Exception e) {
                final String msg = e.getMessage() == null ? e.toString() : e.getMessage();
                runOnUiThread(() -> toast("场景分类读取失败：" + msg));
            }
        }).start();
    }

'''
s = s[:start] + new + s[end:]

# 2) 初始占位不再说“加载中/重试”
s = s.replace('''        catLabels.add("① 全部 大类");
        catLabels.add("② 加载中…（点这里重试）");''',
'''        catLabels.add("全部分类");''')

s = s.replace('''                if (categories.isEmpty() && pos > 0) loadScenes();''', '''''')

io.open(p, 'w', encoding='utf-8').write(s)
print('场景分类改成纯离线')
