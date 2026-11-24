"""按邀请码给厂商分配可见的大类（写 relay/vendor_scenes.json，服务器和 App 都读它）。"""

import io
import json
import sys

PATH = 'relay/vendor_scenes.json'


def load():
    try:
        return json.load(io.open(PATH, encoding='utf-8'))
    except Exception:
        return {}


def save(d):
    io.open(PATH, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))


def main():
    if len(sys.argv) < 2:
        d = load()
        scenes = json.load(io.open('relay/scenes.json', encoding='utf-8'))
        cats = []
        for it in scenes['items']:
            if it['category'] not in cats:
                cats.append(it['category'])
        print('可用大类:', ' / '.join(cats))
        print()
        if not d:
            print('（还没有任何厂商配置，所有厂商都看到全部大类）')
        for code, allow in d.items():
            print('%-10s %s' % (code, ' / '.join(allow) if allow else '（全部）'))
        print()
        print('用法:')
        print('  python tools/set_vendor_scenes.py ZJMEIYI 零售 餐饮     # 只给这个码这两类')
        print('  python tools/set_vendor_scenes.py ZJMEIYI all          # 恢复全部')
        return

    code = sys.argv[1].upper()
    allow = [a for a in sys.argv[2:] if a]
    d = load()
    if allow and allow[0].lower() in ('all', '全部'):
        d.pop(code, None)
        save(d)
        print('%s 恢复为全部大类' % code)
        return
    if not allow:
        d.pop(code, None)
        save(d)
        print('%s 已移除限制（全部大类）' % code)
        return
    d[code] = allow
    save(d)
    print('%s → %s' % (code, ' / '.join(allow)))


if __name__ == '__main__':
    main()
