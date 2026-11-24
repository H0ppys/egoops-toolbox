import io

p = 'relay/transcode.mjs'
s = io.open(p, encoding='utf-8').read()

old = '''  let codec = '';
  try { codec = await codecOf(abs); } catch (_) { codec = ''; }
  if (codec === 'h264') return { done: false, reason: 'already-h264' };
  if (codec && codec !== 'hevc') return { done: false, reason: 'codec-' + codec };'''
new = '''  let codec = '';
  try { codec = await codecOf(abs); } catch (_) { codec = ''; }
  codec = (codec || '').replace(/[^a-z0-9]/g, '');   // 去掉换行/逗号之类
  if (codec === 'h264' || codec === 'avc1') return { done: false, reason: 'already-h264' };'''
assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('transcode logic fixed')
