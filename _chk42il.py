import io, re
# isolate banned-pattern scan to the two new blocks only
src = io.open('_p42il.py', 'rb').read().decode('utf-8')
blocks = {}
for name in ('NEW_I', 'NEW_L'):
    m = re.search(name + r" = '''(.*?)'''", src, re.S)
    blocks[name] = m.group(1)
pats = ['不是', '而是', '而非', '并非', '——', '不等于', '没有.{0,6}，是', '不叫.{0,6}，叫']
for k, t in blocks.items():
    hits = []
    for p in pats:
        for m in re.finditer(p, t):
            s = max(0, m.start() - 14)
            hits.append((p.encode('unicode_escape').decode('ascii'),
                         t[m.start():m.start()+14].encode('unicode_escape').decode('ascii')))
    print(k, len(t), 'hits', len(hits))
    for h in hits:
        print('   ', h[0], '|', h[1])
# pre-existing counts in the two files
for f in ('42i_', '42l_'):
    p = io.open(globp := __import__('glob').glob(f + '*.md')[0], 'rb').read().decode('utf-8')
    print(f, 'pre', [(x, p.count(x)) for x in ['不是', '不等于', '并非', '——']])
