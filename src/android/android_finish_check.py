"""兜底：拍完点「全部拍完」时，如果任务1 还没填区域/动作，先让人补填。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old = '''    private void finishAll() {
        showPage(4);'''
new = '''    private void finishAll() {
        // 任务1 还缺区域/动作：先补填，否则 EgoOps 里会是一条没名字的任务
        if (!site.tasks.isEmpty()) {
            Model.Task t0 = site.tasks.get(0);
            boolean missing = (t0.area == null || t0.area.trim().isEmpty())
                    || (t0.name == null || t0.name.trim().isEmpty() || "任务1".equals(t0.name.trim()));
            if (missing) {
                toast("任务1 还没填区域和动作，请先补填");
                showAreaForTask1();
                return;
            }
        }
        showPage(4);'''
assert old in s
s = s.replace(old, new)

# 其它任务缺名字也拦一下
old2 = '''            if (missing) {
                toast("任务1 还没填区域和动作，请先补填");
                showAreaForTask1();
                return;
            }
        }
        showPage(4);'''
new2 = '''            if (missing) {
                toast("任务1 还没填区域和动作，请先补填");
                showAreaForTask1();
                return;
            }
        }
        for (int i = 1; i < site.tasks.size(); i++) {
            Model.Task t = site.tasks.get(i);
            if (t.name == null || t.name.trim().isEmpty() || "任务" + (i + 1).equals(t.name.trim())) {
                toast("还有任务没填动作名称，请补填");
                return;
            }
        }
        showPage(4);'''
assert old2 in s
s = s.replace(old2, new2)

io.open(P, 'w', encoding='utf-8').write(s)
print('全部拍完前的检查已加')
