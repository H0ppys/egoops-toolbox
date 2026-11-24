"""修缩略图：PhotoImage 必须在主线程创建（原来在线程里建，静默失败）。"""

import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    def load_thumb(self, f, label):')
end = s.index('    def update_sel_state(self):')

new = '''    def load_thumb(self, f, label):
        fid = f["id"]
        if fid in self.thumbs:
            try:
                label.config(image=self.thumbs[fid], text="")
            except Exception:
                pass
            return

        def work():
            try:
                from PIL import Image
                path = os.path.join(HERE, ".cache", fid + ".img")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                if not os.path.exists(path) or os.path.getsize(path) == 0:
                    self.api.download("/files/" + fid, path)
                im = Image.open(path)
                im.thumbnail((190, 130))
                pil = im.convert("RGB").copy()

                def apply():
                    try:
                        from PIL import ImageTk
                        tkimg = ImageTk.PhotoImage(pil)
                        self.thumbs[fid] = tkimg
                        if label.winfo_exists():
                            label.config(image=tkimg, text="")
                    except Exception as e:
                        if label.winfo_exists():
                            label.config(text="无预览")

                self.ui(apply)
            except Exception:
                def nope():
                    try:
                        if label.winfo_exists():
                            label.config(text="无预览")
                    except Exception:
                        pass
                self.ui(nope)

        threading.Thread(target=work, daemon=True).start()

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('缩略图已改为主线程创建，语法 OK')
