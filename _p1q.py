# -*- coding: utf-8 -*-
import io, re
p = r'E:\Novel2\40_卷一_人类反馈_正文.md'
t = io.open(p, encoding='utf-8').read()
L = t.split('\n')
out = ['file=%s lines=%d hanzi=%d' % (p.split('\\')[-1], len(L), len(re.findall(r'[\u4e00-\u9fff]', t)))]
out.append('--- headings ---')
for i, l in enumerate(L):
    if re.match(r'^#{1,3}\s', l):
        out.append('%d|%s' % (i+1, l[:60]))
out.append('--- first 24 non-empty ---')
c = 0
for i, l in enumerate(L):
    if l.strip():
        out.append('%d|%s' % (i+1, l[:120]))
        c += 1
    if c >= 24:
        break
out.append('--- last 12 non-empty ---')
ne = [(i+1, l) for i, l in enumerate(L) if l.strip()]
for i, l in ne[-12:]:
    out.append('%d|%s' % (i, l[:120]))
out.append('--- motif counts ---')
for kw in ('钟', '花', '派对', '宴会', '邀请', '客人', '下午', '上午', '回声', '缝', '刀', '窗', '街'):
    out.append('[%s] %d' % (kw, t.count(kw)))
io.open(r'E:\Novel2\_p1q.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(out))
