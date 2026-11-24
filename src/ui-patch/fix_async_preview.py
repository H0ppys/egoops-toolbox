import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 初始化缓存
s = s.replace('''        self.site_rows = {}
        self.file_rows = {}
        self.loaded_sites = set()''', '''        self.site_rows = {}
        self.file_rows = {}
        self.loaded_sites = set()
        self._preview_cache = {}
        self._preview_pending = set()''')

# 2) on_tree_select 里改成异步请求预览
s = s.replace('''            self.lbl_site.config(text="%s · %s · %s" % (
                f.get("filename", ""), human_size(f.get("size", 0)), f.get("kind", "")))
            self.show_photo_file(f)''', '''            self.lbl_site.config(text="%s · %s · %s" % (
                f.get("filename", ""), human_size(f.get("size", 0)), f.get("kind", "")))
            if f.get("kind") == "photo":
                self.request_preview(f)
            else:
                self.preview.config(image="", text="视频：双击用系统播放器打开")''')

# 3) 用异步 + 缓存替换同步下载
start = s.index('    def show_photo_file(self, f):')
end = s.index('    def on_tree_open(self, event):')
new = '''    def request_preview(self, f):
        """后台线程下载照片，绝不阻塞界面"""
        fid = f.get("id")
        if not fid:
            return
        if fid in self._preview_cache:
            self.show_photo(self._preview_cache[fid])
            return
        if fid in self._preview_pending:
            return
        self._preview_pending.add(fid)
        self.preview.config(image="", text="正在加载照片…")

        server = (self.cfg.get("server") or "").rstrip("/")
        token = getattr(self.api, "token", "")

        def work():
            try:
                import urllib.request
                req = urllib.request.Request(server + "/files/" + fid)
                if token:
                    req.add_header("Authorization", "Bearer " + token)
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                tmp = os.path.join(os.environ.get("TEMP") or ".", "egoops_preview_" + fid + ".jpg")
                with open(tmp, "wb") as fh:
                    fh.write(data)
                self.ui(self._preview_ready, fid, tmp)
            except Exception as e:
                self.ui(self._preview_failed, fid, str(e))

        threading.Thread(target=work, daemon=True).start()

    def _preview_ready(self, fid, path):
        self._preview_pending.discard(fid)
        self._preview_cache[fid] = path
        # 只在当前选中的仍是这张时才显示
        cur = self.tree.focus()
        f = self.file_rows.get(cur)
        if f and f.get("id") == fid:
            self.show_photo(path)

    def _preview_failed(self, fid, err):
        self._preview_pending.discard(fid)
        cur = self.tree.focus()
        f = self.file_rows.get(cur)
        if f and f.get("id") == fid:
            self.preview.config(image="", text="预览失败：%s" % err)

    def show_photo(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((560, 320))
            self._img = ImageTk.PhotoImage(img)
            self.preview.config(image=self._img, text="")
            img.close()
        except Exception as e:
            self.preview.config(image="", text="预览失败：%s" % e)

'''
s = s[:start] + new + s[end:]

io.open(p, 'w', encoding='utf-8').write(s)
print('preview is async now')
