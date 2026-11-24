import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 在按钮前提前声明
if s.count('boolean galleryOnly') == 1:
    s = s.replace('''        Button b = new Button(this);
        b.setAllCaps(false);''',
'''        boolean galleryOnly = "panophoto".equals(key);
        Button b = new Button(this);
        b.setAllCaps(false);''')
    io.open(P, 'w', encoding='utf-8').write(s)
    print('galleryOnly 提前声明')

# 后面那处重复声明去掉（变成直接使用）
s = io.open(P, encoding='utf-8').read()
s = s.replace('''        boolean galleryOnly = "panophoto".equals(key);
        if (BuildConfigVersion.NO_CAPTURE && !galleryOnly) {''',
'''        if (BuildConfigVersion.NO_CAPTURE && !galleryOnly) {''')
io.open(P, 'w', encoding='utf-8').write(s)
print('重复声明已去掉；galleryOnly 出现次数:', s.count('boolean galleryOnly'))
