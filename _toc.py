# -*- coding: utf-8 -*-
import fitz, io, json
d = fitz.open(r'E:\Novel2\在环_十卷_打印本.pdf')
toc = d.get_toc(simple=True)
out = ['pages=%d toc=%d' % (len(d), len(toc))]
want = ('卷二', '附录二', '附录一', '卷三', '第三章', '编者说明', '第四十七条', '附录三')
for t in toc:
    if any(t[1].startswith(w) for w in want):
        out.append('%d|%d|%s' % (t[0], t[2], t[1][:40]))
io.open(r'E:\Novel2\_toc.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
