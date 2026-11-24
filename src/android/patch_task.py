import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

s = s.replace('''        if (site.tasks.isEmpty()) {
            Model.Task t = new Model.Task();
            t.name = "任务1";
            site.tasks.add(t);
        }''', '''        if (site.tasks.isEmpty()) {
            Model.Task t = new Model.Task();
            t.type = "site";
            t.name = "采集点-门头与全景";
            site.tasks.add(t);
        }''')

s = s.replace('''                    Model.Task t = new Model.Task();
                    t.name = "任务1";
                    site.tasks.add(t);''', '''                    Model.Task t = new Model.Task();
                    t.type = "site";
                    t.name = "采集点-门头与全景";
                    site.tasks.add(t);''')

s = s.replace('''        Model.Task t = new Model.Task();
        t.name = "任务" + (site.tasks.size() + 1);''', '''        int areas = 0;
        for (Model.Task x : site.tasks) if ("area".equals(x.type)) areas++;
        Model.Task t = new Model.Task();
        t.type = "area";
        t.name = "区域" + (areas + 1);''')

s = s.replace('''                tvTaskDoneTitle.setText(task.name + " 拍完了");
                tvTaskDoneSub.setText("这家店还有别的任务要拍吗？");''', '''                tvTaskDoneTitle.setText(task.name + " 拍完了");
                tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有别的区域要拍吗？");''')

s = s.replace('''        Button more = primaryButton("再拍一个任务", 68, PRIMARY);''',
              '''        Button more = primaryButton("再拍一个区域", 68, PRIMARY);''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
