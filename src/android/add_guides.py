import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 每个拍摄项的要点提示 ----------
if 'GUIDE' not in s:
    s = s.replace('''    private EditText etInvite;''', '''    private EditText etInvite;

    /** 每一项怎么拍（中老年用户看得懂的短句） */
    private static final String[][] GUIDE = {
        {"门头", "站在马路对面或门口正前方，把整块招牌拍进去，不要只拍一角；避免逆光和路人正脸。"},
        {"全景", "站在门店正中央，手机横着拿稳，原地慢慢转一整圈，货架和通道都要扫到。"},
        {"对角", "走到店铺的一个角，对着斜对面的角拍，让整个空间的对角线出现在画面里。"},
        {"任务照", "先拍你要动那个东西的全貌，再拍细节（手和物体都要清楚），别贴太近。"},
        {"任务视频", "从头到尾一遍做完，动作慢一点、稳一点，手和物体始终在画面里，不要中途停下。"},
    };''')

    # 拍摄页：加「拍摄要点」按钮（放在重拍/相册按钮同一行附近）
    s = s.replace('''        b.setText(done ? "重新拍这一项" : (kind.equals("video") ? "开始录像" : "拍照"));''',
'''        TextView tip = new TextView(this);
        tip.setText("不会拍？点这里看要点");
        tip.setTextSize(13);
        tip.setTextColor(Color.parseColor("#1B63D6"));
        tip.setPadding(0, dp(8), 0, dp(4));
        tip.setOnClickListener(v -> showGuide(currentShot));
        bottom.addView(tip);

        b.setText(done ? "重新拍这一项" : (kind.equals("video") ? "开始录像" : "拍照"));''')

    # 加方法
    s = s.replace('''    /** 质检：模糊 / 过暗 / 视频太短 返回问题描述，合格返回 null */''',
'''    private String guideOf(String shot) {
        String s = shot == null ? "" : shot;
        for (String[] g : GUIDE) if (s.contains(g[0])) return g[1];
        return "对准要拍的东西，拿稳手机，光线充足再按快门。";
    }

    private void showGuide(String shot) {
        new AlertDialog.Builder(this)
                .setTitle("怎么拍：「" + shot + "」")
                .setMessage(guideOf(shot))
                .setPositiveButton("知道了", null)
                .show();
    }

    /** 质检：模糊 / 过暗 / 视频太短 返回问题描述，合格返回 null */''')

    io.open(p, 'w', encoding='utf-8').write(s)
    print('拍摄要点已加')
