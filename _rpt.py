import io, re, sys, glob

rep = sys.argv[1]
src = sys.argv[2]
t = io.open(src, encoding='utf-8', newline='').read().replace('\r\n', '\n')
L = t.split('\n')
flat = t.replace('\n', '')
raw = io.open(rep, encoding='utf-8').read()

# 每条命中形如： 行号 || 原文 || 理由   （可能跨行，先按行号开头的块切）
blocks = re.split(u'\n(?=\s*[0-9]{1,6}\s*\|\|)', raw)
out = []
real = fake = 0
for b in blocks:
    m = re.match(u'\s*([0-9]{1,6})\s*\|\|\s*(.+)', b, re.S)
    if not m:
        continue
    ln, rest = m.group(1), m.group(2)
    parts = rest.split('||')
    if len(parts) < 2:
        continue
    quote = parts[0].strip().replace(u'\u201c', u'').replace(u'\u201d', u'')
    reason = parts[1].strip().replace('\n', ' ')
    q = quote.replace(' ', '').replace('\n', '')
    if len(q) < 4:
        continue
    c = flat.replace(' ', '').count(q)
    okline = ''
    if c:
        real += 1
        idx = [i + 1 for i, l in enumerate(L) if q in l.replace(' ', '')]
        okline = 'L%s' % (idx[0] if idx else '?')
    else:
        fake += 1
    out.append('%s claim@%s count=%d %s | %s | %s' % ('REAL ' if c else 'PHANTOM', ln, c, okline, quote[:70], reason[:90]))
out.append('--- real=%d phantom=%d ---' % (real, fake))
io.open('_tmp_rep.txt', 'w', encoding='utf-8').write('\n'.join(out))
