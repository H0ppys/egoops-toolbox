import io

p = 'tools/watermark_preview7.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('    chip_h = 2.29 * F', '    chip_h = 2.15 * F')
s = s.replace('    line_h = 1.43 * F', '    line_h = 1.30 * F')
s = s.replace('    off_date = 1.86 * F', '    off_date = 1.62 * F')
s = s.replace('    off_small = 1.86 * F', '    off_small = 1.72 * F')
s = s.replace('    tag_pad = 0.10 * F', '    tag_pad = 0.16 * F')

io.open(p, 'w', encoding='utf-8').write(s)
print('参数微调')
