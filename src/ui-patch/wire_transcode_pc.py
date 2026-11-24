import io

# ---------- 1) transcode_pc: 换成国内镜像（27MB.gz，比 GitHub 快很多） ----------
p = 'viewer/transcode_pc.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"',
              'FFMPEG_URL = "https://registry.npmmirror.com/-/binary/ffmpeg-static/b6.0/ffmpeg-win32-x64.gz"')

s = s.replace('''    os.makedirs(APP_DIR, exist_ok=True)
    tmp = os.path.join(APP_DIR, "ffmpeg.zip")
    urllib.request.urlretrieve(FFMPEG_URL, tmp)
    import zipfile
    with zipfile.ZipFile(tmp) as z:
        name = next(n for n in z.namelist() if n.endswith("bin/ffmpeg.exe"))
        with z.open(name) as src, open(FFMPEG, "wb") as dst:
            shutil.copyfileobj(src, dst)
    os.remove(tmp)
    return FFMPEG''', '''    os.makedirs(APP_DIR, exist_ok=True)
    tmp = FFMPEG + ".gz"
    urllib.request.urlretrieve(FFMPEG_URL, tmp)
    import gzip
    with gzip.open(tmp, "rb") as src, open(FFMPEG, "wb") as dst:
        shutil.copyfileobj(src, dst)
    os.remove(tmp)
    return FFMPEG''')

io.open(p, 'w', encoding='utf-8').write(s)
print('transcode_pc 下载源已换成镜像')

# ---------- 2) 上传前转码：create_draft 里所有视频先过一遍 ----------
p2 = 'tools/create_draft.py'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('from address_parse import parse as parse_addr  # noqa: E402',
              'from address_parse import parse as parse_addr  # noqa: E402\nfrom transcode_pc import ensure_h264, codec_of  # noqa: E402')

t = t.replace('''    photos, videos = [], []
    for f in (tk.get("photos") or [])[:9]:
        photos.append(upload_media(tid, download(f), "photo"))
    for f in (tk.get("videos") or [])[:3]:
        videos.append(upload_media(tid, download(f), "video"))''',
'''    photos, videos = [], []
    for f in (tk.get("photos") or [])[:9]:
        photos.append(upload_media(tid, download(f), "photo"))
    for f in (tk.get("videos") or [])[:3]:
        path = download(f)
        codec = codec_of(path)
        if codec == "hevc":
            log("   转码 H.265 → H.264:", os.path.basename(path))
            path = ensure_h264(path)
            log("   转码完成", round(os.path.getsize(path) / 1048576, 2), "MB")
        videos.append(upload_media(tid, path, "video"))''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('create_draft 已接入转码')
