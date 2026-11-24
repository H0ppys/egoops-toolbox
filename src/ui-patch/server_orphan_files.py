"""服务器：把「没有归属任务」的历史文件也显示出来（挂在「未归类」任务里）。

原因：老数据的 files.task_id 是空的，siteView 只按 task_id 分组，
这些文件在查看器里就永远看不到，于是勾采集点显示「没有文件」。
"""

import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

old = '''    // 老数据没有任务维度：兜底显示成一个任务
    if (!view.tasks.length && files.length) {'''
new = '''    // 有文件但没归到任何任务（历史数据）→ 单独挂成「未归类」
    {
      const ids = new Set(tasks.map(t => t.id));
      const orphans = files.filter(f => !f.task_id || !ids.has(f.task_id));
      if (orphans.length) {
        view.tasks.push({
          id: 'unassigned', site_id: site.id, idx: 999, name: '未归类素材',
          note: '（历史数据，没归到任务）', area: '',
          photos: orphans.filter(f => f.kind === 'photo'),
          videos: orphans.filter(f => f.kind === 'video'),
          legacy: true,
        });
      }
    }

    // 老数据没有任务维度：兜底显示成一个任务
    if (!view.tasks.length && files.length) {'''
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('server: 未归类素材已显示')
