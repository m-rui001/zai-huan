# -*- coding: utf-8 -*-
import io, re
p = r'E:\Novel2\40_卷一_人类反馈_正文.md'
L = io.open(p, encoding='utf-8').read().split('\n')
out = []
def sl(a, b, tag):
    out.append('===== %s L%d-%d =====' % (tag, a, b))
    for i in range(a-1, min(b, len(L))):
        if L[i].strip():
            out.append('%d|%s' % (i+1, L[i][:300]))
    out.append('')
sl(425, 460, '榜与回车')
sl(1118, 1160, '吴建')
sl(3176, 3215, '嫁女')
sl(3640, 3680, '外婆')
sl(8249, 8300, '第十八章')
sl(8380, 8400, '结尾前')
out.append('===== greps =====')
for kw in ('吴建', '席', '去世', '死了', '钟', '唱', '小川', '罗小满'):
    hits = [i+1 for i, l in enumerate(L) if kw in l]
    out.append('[%s] n=%d %s' % (kw, len(hits), hits[:25]))
io.open(r'E:\Novel2\_p1q2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
