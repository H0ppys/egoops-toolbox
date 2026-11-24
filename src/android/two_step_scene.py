"""场景分类：必须先选大类，二级才出现具体场景；二级只显示场景名。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 场景条目多存一个"场景名"，二级只显示它
s = s.replace('''                        String cat = o.optString("category");
                        if (path.isEmpty()) continue;
                        list.add(new String[]{path, label, cat});''',
'''                        String cat = o.optString("category");
                        String scene = o.optString("scene");
                        if (path.isEmpty()) continue;
                        list.add(new String[]{path, label, cat, scene});''')

# 2) 二级联动：没选大类时只显示提示，不能选具体场景
old = s[s.index('    private void refreshSceneSpinner() {'):]
end = old.index('\n    ' , old.index('        }\n    }'))
old = old[:old.index('    }\n') + len('    }\n')]
new = '''    private void refreshSceneSpinner() {
        int catPos = spCat == null ? 0 : spCat.getSelectedItemPosition();
        shownIndex.clear();
        List<String> labels = new ArrayList<String>();
        if (catPos <= 0) {
            labels.add("① 先选上面的大类");
        } else {
            String cat = categories.get(catPos - 1);
            for (int i = 0; i < sceneItems.size(); i++) {
                if (cat.equals(sceneItems.get(i)[2])) {
                    String[] row = sceneItems.get(i);
                    String text = row.length > 3 && row[3] != null && !row[3].isEmpty() ? row[3] : row[1];
                    labels.add(text);
                    shownIndex.add(i);
                }
            }
            if (labels.isEmpty()) labels.add("这个大类下没有场景");
        }
        if (spScene2 != null) {
            spScene2.setAdapter(new android.widget.ArrayAdapter<String>(this,
                    android.R.layout.simple_spinner_dropdown_item, labels));
        }
    }
'''
s = s.replace(old, new)

# 3) 开始拍摄：先校验大类，再校验具体场景
s = s.replace('''        if (sceneItems.isEmpty()) {
            toast("场景分类还没准备好，请稍等");
            loadScenes();
            return;
        }
        int p2 = spScene2.getSelectedItemPosition();
        if (p2 < 0 || p2 >= shownIndex.size()) {
            toast("请选择采集场景分类（先选大类，再选具体场景）");
            spScene2.performClick();
            return;
        }''',
'''        if (sceneItems.isEmpty()) {
            toast("场景分类还没准备好，请稍等");
            loadScenes();
            return;
        }
        if (spCat.getSelectedItemPosition() <= 0) {
            toast("请先选大类（上面第一个）");
            spCat.performClick();
            return;
        }
        int p2 = spScene2.getSelectedItemPosition();
        if (p2 < 0 || p2 >= shownIndex.size()) {
            toast("请再选具体场景（下面第二个）");
            spScene2.performClick();
            return;
        }''')

# 4) 恢复上次场景时，先定位大类再定位场景
s = s.replace('''                    if (site.scene != null && !site.scene.isEmpty()) {''',
'''                    if (site.scene != null && !site.scene.isEmpty()) {''')

io.open(P, 'w', encoding='utf-8').write(s)
print('场景分类改为两级强制')
