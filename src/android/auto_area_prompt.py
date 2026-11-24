"""流程：门头照+全景照片+全景视频拍完 → 自动弹出「填区域名称 + 区域动作」→ 再拍该区域 6 项。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 拍完一个任务后的分支：如果是任务1（采集点级），直接问区域
old = '''        if (doneCount(currentTask) >= shotsOf(task).length) {
            toast("这个任务拍完了");
            tvTaskDoneTitle.setText(labelOf(task) + " 拍完了");
            tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有区域或任务要拍吗？");
            showPage(3);
            if (!uploading) startUpload();
        } else {'''
new = '''        if (doneCount(currentTask) >= shotsOf(task).length) {
            if ("site".equals(task.type)) {
                // 门头 + 全景照片 + 全景视频拍完：直接让填区域，不用再点一次
                toast("门头/全景拍完了，接着拍区域");
                tvTaskDoneTitle.setText("门头与全景 拍完了");
                tvTaskDoneSub.setText("接着填这次要拍的区域和动作");
                showPage(3);
                tvTaskDoneTitle.postDelayed(() -> askTask(""), 400);
            } else {
                toast("这个任务拍完了");
                tvTaskDoneTitle.setText(labelOf(task) + " 拍完了");
                tvTaskDoneSub.setText("还有区域或任务要拍吗？");
                showPage(3);
            }
            if (!uploading) startUpload();
        } else {'''
assert old in s
s = s.replace(old, new)

# 2) 区域弹窗文案更贴切
s = s.replace('l1.setText("区域名称（比如：客厅 / 后厨 / 3号包间）");',
              'l1.setText("1. 这是哪个区域？（比如：客厅 / 后厨 / 3号包间）");')
s = s.replace('l2.setText("任务名称（比如：擦拭桌面 / 整理货架）");',
              'l2.setText("2. 在这个区域要做什么动作？（比如：擦拭桌面 / 整理货架）");')
s = s.replace('.setTitle("这个区域要拍什么？")', '.setTitle("填写区域和动作")')
s = s.replace('.setPositiveButton("开始拍摄", null)', '.setPositiveButton("开始拍摄这个区域", null)')

io.open(P, 'w', encoding='utf-8').write(s)
print('流程已改：门头/全景拍完自动问区域')
