import io

p = 'viewer/transcode_pc.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('FFMPEG_URL = "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-win32-x64-gnu.gz"',
              'FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"')

s = s.replace('''    os.makedirs(APP_DIR, exist_ok=True)
    tmp = FFMPEG + ".gz"
    urllib.request.urlretrieve(FFMPEG_URL, tmp)
    import gzip
    with gzip.open(tmp, "rb") as src, open(FFMPEG, "wb") as dst:
        shutil.copyfileobj(src, dst)
    os.remove(tmp)
    return FFMPEG''', '''    os.makedirs(APP_DIR, exist_ok=True)
    tmp = os.path.join(APP_DIR, "ffmpeg.zip")
    urllib.request.urlretrieve(FFMPEG_URL, tmp)
    import zipfile
    with zipfile.ZipFile(tmp) as z:
        name = next(n for n in z.namelist() if n.endswith("bin/ffmpeg.exe"))
        with z.open(name) as src, open(FFMPEG, "wb") as dst:
            shutil.copyfileobj(src, dst)
    os.remove(tmp)
    return FFMPEG''')

io.open(p, 'w', encoding='utf-8').write(s)
print('download url fixed')
