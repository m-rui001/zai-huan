import io
D = r'C:\Users\hp\.qoder-cn\projects\E--Novel2\memory'
def esc(s): return s.encode('unicode_escape').decode('ascii')
p = D + '\\MEMORY.md'
t = io.open(p, 'rb').read().decode('utf-8')
lines = t.split('\n')
hit = [i for i, l in enumerate(lines) if 'project-volume3-reading-queue.md' in l]
print('idx', hit)
for i in hit:
    print('OLD', esc(lines[i]))
NEW = '- [卷三 整卷读队列](project-volume3-reading-queue.md) — **11-04 十三盒各交过一段，队列清空**；已封顶族（规程二・「确认」两用・0.07 无分子・114 换算）、撤案与盒规矩在案'
for i in hit:
    lines[i] = NEW
io.open(p, 'wb').write('\n'.join(lines).encode('utf-8'))
t2 = io.open(p, 'rb').read().decode('utf-8')
print('ok', '队列清空' in t2, 'lines', len(lines))
