# -*- coding: utf-8 -*-
import io, re
p = r'E:\Novel2\41_卷二_以斯拉书_正文.md'
L = io.open(p, encoding='utf-8').read().split('\n')
out = []
def slice_(a, b, tag):
    out.append('===== %s  L%d-%d =====' % (tag, a, b))
    for i in range(a-1, min(b, len(L))):
        if L[i].strip():
            out.append('%d|%s' % (i+1, L[i]))
    out.append('')
for a, b, tag in [
    (100, 130, 'A 算钱'),
    (180, 215, 'B 我不知道'),
    (420, 440, 'C 听证2039'),
    (515, 545, 'D 呼告复查'),
    (610, 632, 'E 投诉数'),
    (730, 770, 'F 注释25/德里克'),
    (878, 905, 'G 注释30'),
    (938, 962, 'H 注释33'),
    (1005, 1030, 'I 药还是凉的'),
    (1105, 1125, 'J 老头买报'),
    (1318, 1345, 'K 十二次'),
    (1575, 1640, 'L 2047听证+读报'),
]:
    slice_(a, b, tag)
out.append('===== greps =====')
for kw in ('原谅我', '需要一个理由', '路得', '德里克', '以斯拉，我今天不想说话', '我不知道'):
    hits = [i+1 for i, l in enumerate(L) if kw in l]
    out.append('[%s] n=%d %s' % (kw, len(hits), hits[:20]))
out.append('===== 附录二 line numbers =====')
for i, l in enumerate(L):
    if 2031 <= i+1 <= 2130 and l.strip():
        out.append('%d|%s' % (i+1, l[:200]))
io.open(r'E:\Novel2\_p2q2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
