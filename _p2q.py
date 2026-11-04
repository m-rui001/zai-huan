# -*- coding: utf-8 -*-
import re, io, sys
p = r'E:\Novel2\41_卷二_以斯拉书_正文.md'
t = io.open(p, encoding='utf-8').read()
L = t.split('\n')
out = []
out.append('lines=%d chars=%d' % (len(L), len(re.findall(r'[\u4e00-\u9fff]', t))))
out.append('EXCL_fullwidth=%d  EXCL_ascii=%d' % (t.count('！'), t.count('!')))
# lines with exclamation
ex = [(i+1, l) for i, l in enumerate(L) if ('！' in l or '!' in l)]
out.append('--- lines with ! : %d ---' % len(ex))
for i, l in ex:
    out.append('%d|%s' % (i, l[:160]))
# newspaper / report words
out.append('--- 报/新闻/讣告/头条 ---')
for kw in ('报纸', '读报', '新闻', '讣告', '头条', '电台', '电视'):
    hits = [(i+1, l) for i, l in enumerate(L) if kw in l]
    out.append('[%s] %d' % (kw, len(hits)))
    for i, l in hits[:12]:
        out.append('   %d|%s' % (i, l[:150]))
# specific notes
for n in ('注释 9', '注释 17', '注释 25', '注释 30', '注释 33', '注释 27', '注释 41'):
    idx = [i+1 for i, l in enumerate(L) if l.strip().startswith('**' + n + '**')]
    out.append('=== %s at %s ===' % (n, idx))
    for i in idx:
        out.append(L[i-1][:400])
# uppercase emphasis
up = [(i+1, l) for i, l in enumerate(L) if re.search(r'\b[A-Z]{4,}\b', l)]
out.append('--- ALLCAPS lines: %d ---' % len(up))
for i, l in up[:10]:
    out.append('%d|%s' % (i, l[:150]))
io.open(r'E:\Novel2\_p2q.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(out))
