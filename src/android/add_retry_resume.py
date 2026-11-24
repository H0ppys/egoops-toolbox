import io

# ---------- 1) Uploader：单个文件失败重试（指数退避） ----------
p = 'android/src/com/egoops/collect/Uploader.java'
s = io.open(p, encoding='utf-8').read()

old = '''                    if (!"uploaded".equals(m.state)) {'''
if 'uploadOneWithRetry' not in s:
    # 在 run() 里换调用
    s = s.replace('''                        sentAll += uploadOne(task, m);''',
                  '''                        sentAll += uploadOneWithRetry(task, m);''')
    # 新增重试方法（放在 uploadOne 之前）
    s = s.replace('''    private long uploadOne(Model.Task task, Model.Media m) throws Exception {''',
'''    /** 分片上传失败自动重试：网络抖一下就重来，最多 4 次 */
    private long uploadOneWithRetry(Model.Task task, Model.Media m) throws Exception {
        Exception last = null;
        for (int attempt = 1; attempt <= 4; attempt++) {
            if (cancelled) throw new Exception("已取消");
            try {
                return uploadOne(task, m);
            } catch (Exception e) {
                last = e;
                boolean fatal = e instanceof Api.ApiException
                        && ((Api.ApiException) e).errorCode != null
                        && !"NETWORK".equals(((Api.ApiException) e).errorCode);
                if (fatal || attempt == 4) throw e;
                stage("网络不稳，" + (attempt * 2) + " 秒后重试（第 " + attempt + " 次）");
                try { Thread.sleep(attempt * 2000L); } catch (InterruptedException ie) {
                    throw new Exception("已取消");
                }
            }
        }
        throw last == null ? new Exception("上传失败") : last;
    }

    private long uploadOne(Model.Task task, Model.Media m) throws Exception {''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Uploader: 重试已加')

# ---------- 2) MainActivity：启动时若有未传完的队列，自动继续 ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

if 'resumePendingUpload' not in t:
    t = t.replace('''        autoLogin();''', '''        autoLogin();
        resumePendingUpload();''', 1)

    t = t.replace('''    private void startUpload() {''', '''    /** 上次没传完：打开 App 自动接着传 */
    private void resumePendingUpload() {
        try {
            Model.Site saved = store.loadQueue();
            if (saved == null || saved.fileCount() == 0) return;
            int pending = 0;
            for (Model.Task t : saved.tasks) {
                for (Model.Media m : t.media) {
                    if (!"uploaded".equals(m.state)) pending++;
                }
            }
            if (pending == 0) return;
            final int n = pending;
            toast("上次还有 " + n + " 个文件没传完，自动继续");
            tvUpload.postDelayed(this::startUpload, 1500);
        } catch (Exception ignored) {
        }
    }

    private void startUpload() {''')
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('MainActivity: 启动自动续传已加')
