"""安卓端也按同一规则：第一个区域并进「任务1」——
   任务1 = 门头照 + 全景照片 + 全景视频 + 该区域的对角2/任务照2/任务视频2
   后面新增的区域才各自单独成任务。
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old = '''            Model.Task t = new Model.Task();
            t.type = "area";
            t.area = a;
            t.name = n;
            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;'''

new = '''            Model.Task t;
            boolean firstArea = site.tasks.size() == 1 && "site".equals(site.tasks.get(0).type);
            if (firstArea) {
                // 门头/全景就并进这第一个区域，成为「任务1」
                t = site.tasks.get(0);
                t.type = "area";
                t.area = a;
                t.name = n;
                currentTask = 0;
                toast("任务1 = 门头/全景 + " + a);
            } else {
                t = new Model.Task();
                t.type = "area";
                t.area = a;
                t.name = n;
                site.tasks.add(t);
                currentTask = site.tasks.size() - 1;
            }'''

assert old in s
s = s.replace(old, new)

# renderShot 里显示"任务1"，让采集员知道第一项包含门头/全景
s = s.replace('''        tvStep.setText(labelOf(task) + " · 第 " + (idx + 1) + "/" + shots.length + " 项");''',
'''        String prefix = (currentTask == 0 && "area".equals(task.type)) ? "任务1（含门头/全景）· " : "";
        tvStep.setText(prefix + labelOf(task) + " · 第 " + (idx + 1) + "/" + shots.length + " 项");''')

io.open(P, 'w', encoding='utf-8').write(s)
print('安卓端任务1合并已实现')
