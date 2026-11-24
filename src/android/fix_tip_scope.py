import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 把提示条挂到 card 里（bottom 不在这个作用域）
s = s.replace('''        tip.setOnClickListener(v -> showGuide(currentShot));
        bottom.addView(tip);

        b.setText(done''', '''        b.setText(done''')

# 在按钮加到 card 之后插入提示条
marker = '''        card.addView(b);'''
if 'tip.setOnClickListener' not in s:
    s = s.replace(marker, marker + '''

        TextView tip = new TextView(this);
        tip.setText("不会拍？点这里看要点");
        tip.setTextSize(14);
        tip.setTextColor(Color.parseColor("#1B63D6"));
        tip.setGravity(Gravity.CENTER);
        tip.setPadding(0, dp(8), 0, 0);
        tip.setOnClickListener(v -> showGuide(currentShot));
        card.addView(tip);''', 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('tip 挂到 card')
