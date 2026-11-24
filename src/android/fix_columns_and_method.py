"""修两处：
  1) 表格列错位：fill_sites 还在按旧列（8 列）塞数据，新表只有 6 列
  2) 补上 App 里漏掉的 syncTaskNamesAsync 方法
"""

import io

# ---------------- 查看器：列对齐 ----------------
p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''            self.tree.insert("", "end", iid=iid, text="", values=(
                "☐",
                it.get("name", ""),
                self.vendor_of(it),
                it.get("address") or "（未填地址）",
                "%s · %d文件" % (it.get("created_by", ""), it.get("file_count", 0)),
                (it.get("created_at") or "").replace("T", " ")[:16],
                human_size(it.get("bytes", 0)),
                self.draft_text(it),
            ))
            self.tree.insert(iid, "end", iid=iid + ":loading", text="", values=("", "加载中…", "", "", "", ""))'''
new = '''            # 列顺序：sel / name / address / vendor / time / draft
            self.tree.insert("", "end", iid=iid, text="", values=(
                "☐",
                it.get("name", ""),
                it.get("address") or "（未填地址）",
                self.vendor_of(it),
                (it.get("created_at") or "").replace("T", " ")[:16] + " · %d件" % it.get("file_count", 0),
                self.draft_text(it),
            ))
            self.tree.insert(iid, "end", iid=iid + ":loading", text="", values=("", "加载中…", "", "", "", ""))'''
assert old in s
s = s.replace(old, new)

s = s.replace('''            self.tree.insert("", "end", iid="empty:hint", text="", values=(
                "", "还没有采集点", "让采集员用手机 App 拍完上传，这里会自动出现", "", "", "", ""))''',
'''            self.tree.insert("", "end", iid="empty:hint", text="", values=(
                "", "还没有采集点", "让采集员用手机 App 拍完上传，这里会自动出现", "", "", ""))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('查看器：列对齐')

# ---------------- App：补方法 ----------------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

if 'private void syncTaskNamesAsync()' not in t:
    anchor = '    /** 任务1 的区域填写：写回当前任务，不新建 */'
    block = '''    /** 任务名/区域改动后同步到服务器（后台，不打断拍摄） */
    private void syncTaskNamesAsync() {
        try {
            if (site.siteId == null || site.siteId.isEmpty()) return;
            new Thread(() -> {
                try {
                    new Uploader(site, api, store).syncTaskNames();
                } catch (Exception ignored) {
                }
            }).start();
        } catch (Exception ignored) {
        }
    }

'''
    if anchor in t:
        t = t.replace(anchor, block + anchor, 1)
    else:
        anchor2 = '    private void askTask(String presetArea) {'
        t = t.replace(anchor2, block + anchor2, 1)
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('App: syncTaskNamesAsync 已补')
else:
    print('App: 方法已存在')
