"""删掉重复的旧上传块（174-188 行），并给素材加数量上限（EgoOps：照片≤8、视频≤3）。"""

import io

P = 'viewer/egoops_draft.py'
lines = io.open(P, encoding='utf-8').read().splitlines(True)

# 删除 "# 上传素材" 那段旧块（从注释行到其后的空行）
start = None
for i, l in enumerate(lines):
    if l.strip() == '# 上传素材':
        start = i
        break
assert start is not None, '找不到旧上传块'
# 结束：到 "        task_name = (content.get(\"name\")" 之前
end = None
for i in range(start, start + 40):
    if lines[i].startswith('        task_name = (content.get("name")'):
        end = i
        break
assert end is not None, '找不到旧上传块结尾'
print('删除行:', start + 1, '到', end)
del lines[start:end]

s = ''.join(lines)

# 素材上限
s = s.replace('''        photos = task.get("photos") or []
        videos = task.get("videos") or []''',
'''        photos = task.get("photos") or []
        videos = task.get("videos") or []
        # EgoOps 限制：单个任务照片最多 8 张、视频最多 3 个
        if len(photos) > 8:
            log("  照片 %d 张，超过平台上限 8 张，只传前 8 张" % len(photos))
            photos = photos[:8]
        if len(videos) > 3:
            log("  视频 %d 个，超过平台上限 3 个，只传前 3 个" % len(videos))
            videos = videos[:3]''')

io.open(P, 'w', encoding='utf-8').write(s)
print('已去重 + 加限制')
