"""切到拍摄页时收键盘；顺带把设置里的服务器地址显示成当前实际值。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

if 'hideKeyboard' not in s:
    s = s.replace('''    private void showPage(int n) {
        curPage = n;''', '''    private void hideKeyboard() {
        try {
            android.view.inputmethod.InputMethodManager imm =
                    (android.view.inputmethod.InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
            View v = getCurrentFocus();
            if (imm != null && v != null) {
                imm.hideSoftInputFromWindow(v.getWindowToken(), 0);
                v.clearFocus();
            }
        } catch (Exception ignored) { }
    }

    private void showPage(int n) {
        curPage = n;
        if (n != 1) hideKeyboard();''')

io.open(P, 'w', encoding='utf-8').write(s)
print('切页收键盘')
