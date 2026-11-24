"""每个区域加一张「全景照片」，并全局提示用广角拍。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 区域拍摄项：全景照片放第一项（先拍全，再拍对角/任务）
old = '''    /** 每个区域：2 张对角照 + 2 张任务照 + 2 个任务视频 */
    private static final String[][] SHOTS_AREA = {
            {"corner1", "对角照片 1", "站在区域一个角，斜着拍对角", "photo"},
            {"corner2", "对角照片 2", "走到对角，反方向再拍一张", "photo"},
            {"work1", "任务照片 1", "拍这个区域要采集的内容", "photo"},
            {"work2", "任务照片 2", "换个角度再拍一张", "photo"},
            {"clip1", "任务视频 1", "对准要采集的动作，录 10 秒", "video"},
            {"clip2", "任务视频 2", "换个角度再录 10 秒", "video"},
    };'''
new = '''    /** 每个区域：1 张全景 + 2 张对角照 + 2 张任务照 + 2 个任务视频 */
    private static final String[][] SHOTS_AREA = {
            {"areapano", "全景照片", "站在区域中央，用广角把整个区域拍全（四角都要进画面）", "photo"},
            {"corner1", "对角照片 1", "站在区域一个角，斜着拍对角", "photo"},
            {"corner2", "对角照片 2", "走到对角，反方向再拍一张", "photo"},
            {"work1", "任务照片 1", "拍这个区域要采集的内容", "photo"},
            {"work2", "任务照片 2", "换个角度再拍一张", "photo"},
            {"clip1", "任务视频 1", "对准要采集的动作，用广角录 10 秒", "video"},
            {"clip2", "任务视频 2", "换个角度再录 10 秒", "video"},
    };'''
assert old in s
s = s.replace(old, new)

# 2) 首页说明
s = s.replace('先拍门头照 + 全景视频\\n再逐个区域拍（每个区域 6 项）',
              '先拍门头照 + 全景视频\\n再逐个区域拍（每个区域 7 项，含全景照片）')

# 3) 每张都提示广角：卡片标题下面加一行
if '广角' not in s:
    s = s.replace('''        TextView t = new TextView(this);
        t.setText(title);''',
'''        TextView wide = new TextView(this);
        wide.setText("📷 请用广角拍摄（0.5x），把整个空间拍全");
        wide.setTextSize(14);
        wide.setTextColor(Color.parseColor("#B45309"));
        wide.setGravity(Gravity.CENTER);
        wide.setPadding(0, dp(6), 0, dp(2));
        card.addView(wide);

        TextView t = new TextView(this);
        t.setText(title);''')

# 4) 拍摄要点里补一条
s = s.replace('''        {"任务视频", "从头到尾一遍做完，动作慢一点、稳一点，手和物体始终在画面里，不要中途停下。"},''',
'''        {"任务视频", "从头到尾一遍做完，动作慢一点、稳一点，手和物体始终在画面里，不要中途停下。"},
        {"全景照片", "站在区域正中央，手机切到广角（0.5x），举到胸口高度，把四个角都框进画面，再按快门。"},''')

io.open(P, 'w', encoding='utf-8').write(s)
print('区域加全景照片 + 广角提示')
