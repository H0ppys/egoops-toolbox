import io

p = 'ssh_exec.py'
s = io.open(p, encoding='utf-8').read()

if 'egoops_ed25519' not in s:
    s = s.replace('''PASS = os.environ.get("DEPLOY_PASS", "<FILL_ME>")''',
'''PASS = os.environ.get("DEPLOY_PASS", "<FILL_ME>")
KEY = os.environ.get("DEPLOY_KEY", os.path.join(os.path.expanduser("~"), ".ssh", "egoops_ed25519"))''')

    s = s.replace('''        password=PASS,''', '''        password=PASS,
        key_filename=KEY if os.path.exists(KEY) else None,''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('ssh_exec 改为优先用密钥')

# 根目录再放一份便于直接调用的说明
print('done')
