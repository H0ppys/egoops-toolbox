import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old = '''            new AlertDialog.Builder(this)
                    .setTitle("上次运行出错了")
                    .setMessage(sb.toString())
                    .setPositiveButton("知道了", (d, w) -> newest.delete())
                    .setPositiveButton("知道了", null)
                    .show();'''
new = '''            final java.io.File crashFile = newest;
            new AlertDialog.Builder(this)
                    .setTitle("上次运行出错了")
                    .setMessage(sb.toString())
                    .setPositiveButton("知道了", (d, w) -> crashFile.delete())
                    .show();'''
assert old in s
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8').write(s)
print('修好 lambda 与重复按钮')
