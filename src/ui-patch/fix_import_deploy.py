import io

p = 'tools/import_vendor_scenes.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("        import subprocess\n", "        import subprocess\n        PY = os.environ.get('PYTHON_FOR_SSH', 'python')\n")
s = s.replace("subprocess.run([sys.executable, 'ssh_exec.py'", "subprocess.run([PY, 'ssh_exec.py'")

io.open(p, 'w', encoding='utf-8').write(s)
print('deploy 用系统 python')
