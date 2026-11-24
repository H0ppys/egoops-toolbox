"""拍摄项调整（按用户要求）：
   任务1（采集点级）：门头照 + 全景照片 + 全景视频
   后续区域：           对角照片 x2 + 任务照片 x2 + 任务视频 x2（6 项，不再拍门头/全景）
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old_site = '''    /** 采集点级拍摄：门头照 + 全景视频 */
    private static final String[][] SHOTS_SITE = {
            {"door", "门头照", "正对门头，把招牌和门都拍进去", "photo"},
            {"panovideo", "全景视频", "站在店中间，慢慢转一圈（15 秒左右）", "video"},
    };'''
new_site = '''    /** 任务1（采集点级）：门头照 + 全景照片 + 全景视频 */
    private static final String[][] SHOTS_SITE = {
            {"door", "门头照", "正对门头，把招牌和门都拍进去（用广角）", "photo"},
            {"panophoto", "全景照片", "站在店中央，用广角把整个空间拍全", "photo"},
            {"panovideo", "全景视频", "原地慢慢转一圈，用广角（15 秒左右）", "video"},
    };'''
assert old_site in s
s = s.replace(old_site, new_site)

old_area = '''    /** 每个区域：1 张全景 + 2 张对角照 + 2 张任务照 + 2 个任务视频 */
    private static final String[][] SHOTS_AREA = {
            {"areapano", "全景照片", "站在区域中央，用广角把整个区域拍全（四角都要进画面）", "photo"},
            {"corner1", "对角照片 1", "站在区域一个角，斜着拍对角", "photo"},
            {"corner2", "对角照片 2", "走到对角，反方向再拍一张", "photo"},
            {"work1", "任务照片 1", "拍这个区域要采集的内容", "photo"},
            {"work2", "任务照片 2", "换个角度再拍一张", "photo"},
            {"clip1", "任务视频 1", "对准要采集的动作，用广角录 10 秒", "video"},
            {"clip2", "任务视频 2", "换个角度再录 10 秒", "video"},
    };'''
new_area = '''    /** 后续区域：2 张对角照 + 2 张任务照 + 2 个任务视频（门头/全景只在任务1 拍） */
    private static final String[][] SHOTS_AREA = {
            {"corner1", "对角照片 1", "站在区域一个角，用广角斜着拍对角", "photo"},
            {"corner2", "对角照片 2", "走到对角，反方向再拍一张", "photo"},
            {"work1", "任务照片 1", "拍这个区域要采集的内容", "photo"},
            {"work2", "任务照片 2", "换个角度再拍一张", "photo"},
            {"clip1", "任务视频 1", "对准要采集的动作，用广角录 10 秒", "video"},
            {"clip2", "任务视频 2", "换个角度再录 10 秒", "video"},
    };'''
assert old_area in s
s = s.replace(old_area, new_area)

# 首页说明
s = s.replace('先拍门头照 + 全景视频\\n再逐个区域拍（每个区域 7 项，含全景照片）',
              '任务1：门头照 + 全景照片 + 全景视频\\n后续区域：对角2 + 任务照2 + 任务视频2（6 项）')

# 任务1 的名称更直观
s = s.replace('t.name = "采集点-门头与全景";', 't.name = "任务1·门头与全景";')

io.open(P, 'w', encoding='utf-8').write(s)
print('拍摄项已调整')
