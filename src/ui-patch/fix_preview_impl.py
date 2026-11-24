import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 用自带的 urllib + PIL 实现照片预览（on_tree_select 里会用）
old = s[s.index('    def show_photo_file(self, f):'):s.index('    def on_tree_open(self, event):')]
new = '''    def show_photo_file(self, f):
        """选中照片时在预览区显示"""
        if f.get("kind") != "photo":
            self.preview.config(image="", text="视频双击用系统播放器打开")
            return
        try:
            import tempfile
            import urllib.request
            url = self.cfg.get("server", "").rstrip("/") + "/files/" + f["id"]
            req = urllib.request.Request(url)
            if self.api.token:
                req.add_header("Authorization", "Bearer " + self.api.token)
            data = urllib.request.urlopen(req, timeout=30).read()
            tmp = os.path.join(tempfile.gettempdir(), "preview_" + f["id"] + ".jpg")
            with open(tmp, "wb") as fh:
                fh.write(data)
            self.show_photo(tmp)
        except Exception as e:
            self.preview.config(image="", text="预览失败：%s" % e)

    def show_photo(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((520, 300))
            self._img = ImageTk.PhotoImage(img)
            self.preview.config(image=self._img, text="")
        except Exception as e:
            self.preview.config(image="", text="预览失败：%s" % e)

'''
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('preview implemented')
