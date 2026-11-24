"""把 vendorScenes() 补进 server.mjs（SCENES 是 try/catch 里赋值，之前的插入点不匹配）。"""

import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

if 'function vendorScenes()' not in s:
    anchor = "console.warn('scenes.json 读取失败，场景列表将为空：', e.message);"
    # 在该 try/catch 结束之后插入函数
    idx = s.index(anchor)
    end = s.index('}', idx) + 1        # catch 块结束的 '}'
    insert = """

// 厂商 → 可见大类（relay/vendor_scenes.json，没有配置就是全部）
function vendorScenes() {
  try {
    return JSON.parse(fs.readFileSync(path.join(HERE, 'vendor_scenes.json'), 'utf8'));
  } catch (_) {
    return {};
  }
}
"""
    s = s[:end] + insert + s[end:]
    io.open(p, 'w', encoding='utf-8').write(s)
    print('vendorScenes() 已插入')

# 顺便把 file 常量准备好
if 'const VENDOR_FILE' in s:
    s = s.replace("const VENDOR_FILE = path.join(HERE, 'vendor_scenes.json');\n", "")
    io.open(p, 'w', encoding='utf-8').write(s)
