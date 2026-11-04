import io, re
D = r'C:\Users\hp\.qoder-cn\projects\E--Novel2\memory'
def esc(s): return s.encode('unicode_escape').decode('ascii')

def patch(fn, pairs):
    p = D + '\\' + fn
    t = io.open(p, 'rb').read().decode('utf-8')
    for old, new in pairs:
        c = t.count(old)
        print(fn[:12], c, esc(old)[:40])
        assert c == 1, (fn, old)
        t = t.replace(old, new)
    io.open(p, 'wb').write(t.encode('utf-8'))

patch('project-literary-gaps-per-volume.md', [
    ('全书 941,593', '全书 943,576'),
])
patch('MEMORY.md', [
    ('[卷三 整卷读队列](project-volume3-reading-queue.md) — 42_/42i_/42n_ 已各交一段（水杯回付・H-05 附件一百四十七字照录）；余 42b_—42m_ 十一册待读，人称档位与既判清单在案',
     '[卷三 整卷读队列](project-volume3-reading-queue.md) — **11-04 十三盒各交过一段，队列清空**；已封顶族（规程二・「确认」两用・0.07 无分子・114 换算）与盒规矩在案'),
])
t = io.open(D + '\\project-literary-gaps-per-volume.md', 'rb').read().decode('utf-8')
print('gaps total ok', '943,576' in t)
t2 = io.open(D + '\\MEMORY.md', 'rb').read().decode('utf-8')
print('index ok', '队列清空' in t2)
