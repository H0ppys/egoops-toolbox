import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 记一个当前页号，返回键判断用
if 'private int curPage' not in s:
    s = s.replace('''    private void showPage(int n) {''', '''    private int curPage = 1;

    private void showPage(int n) {
        curPage = n;''')

s = s.replace('''        if (page > 0) {''', '''        if (curPage > 1) {''')

io.open(p, 'w', encoding='utf-8').write(s)
print('返回键改用 curPage')
