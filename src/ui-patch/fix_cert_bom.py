"""去掉证书文件的 BOM/CRLF——Android 解析带 BOM 的 PEM 会失败（https 一直握手不上的真因）。"""

import io

SRC = 'viewer/egoops.crt'

raw = open(SRC, 'rb').read()
print('原始前 3 字节:', raw[:3], '| 有 CRLF:', b'\r\n' in raw, '| 长度:', len(raw))

text = raw.decode('utf-8-sig')           # 去掉 BOM
text = text.replace('\r\n', '\n').replace('\r', '\n')
text = text.strip() + '\n'               # 统一 LF，结尾一个换行

out = text.encode('utf-8')
open(SRC, 'wb').write(out)
open('android/res/raw/egoops_cert.crt', 'wb').write(out)

print('清理后前 30 字节:', out[:30])
print('有 BOM:', out[:3] == b'\xef\xbb\xbf', '| 有 CR:', b'\r' in out, '| 长度:', len(out))

# 顺手用 Python ssl 再验一次这个 CA 能校验服务器
import ssl
import socket
ctx = ssl.create_default_context(cafile=SRC)
with socket.create_connection(('<FILL_ME>', 443), timeout=10) as sock:
    with ctx.wrap_socket(sock, server_hostname='<FILL_ME>') as ss:
        print('TLS 校验通过，协议:', ss.version())
