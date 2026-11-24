"""启动时只在「真的没拍完/没传完」时才恢复上次内容；已完成的采集点自动清空，从空白开始。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old = '''        Model.Site saved = store.loadQueue();
        if (saved != null && !saved.tasks.isEmpty()) site = saved;'''

new = '''        // 上次的采集点：只有没拍完或没传完才恢复，拍完传完的就当新的开始
        Model.Site saved = store.loadQueue();
        if (saved != null && !saved.tasks.isEmpty()) {
            int pending = 0, total = 0;
            for (Model.Task t : saved.tasks) {
                for (Model.Media m : t.media) {
                    total++;
                    if (!"uploaded".equals(m.state)) pending++;
                }
            }
            boolean finished = total > 0 && pending == 0;
            if (finished) {
                store.clearQueue();          // 已经传完：清掉，下次是干净的开始
                site = new Model.Site();
            } else {
                site = saved;
            }
        }'''

assert old in s
s = s.replace(old, new)

# 进页面时按 site 回填（原来是直接读 site.name/area，已经是这样）
io.open(P, 'w', encoding='utf-8').write(s)
print('启动恢复逻辑已改')
