import re, io, glob, os

files = sorted(x for x in glob.glob('*_*.md') if '_正文' in x and 'backup' not in x)
q = re.compile(r'[“"][^”"\n]*[”?！.,、]?[^”"\n]*[”"]|「[^」\n]*」|‘[^’\n]*’')
shapes = [
    ('NOA_ISB', re.compile(r'没有[^。\n]{1,16}[，、][^。\n]{0,8}是')),
    ('NOA_ZHI', re.compile(r'没有[^。\n]{1,16}[，、][^。\n]{0,4}只是')),
    ('NOTEQ', re.compile(r'[^。\n]{0,10}不等于')),
    ('ERFEI', re.compile(r'而非')),
    ('BUSHI_ERSHI', re.compile(r'不是[^。\n]{1,16}而是')),
    ('BINGFEI', re.compile(r'并非[^。\n]{1,14}而是')),
    ('NOJIAO', re.compile(r'不叫[^。\n]{1,12}叫')),
    ('BUIJSB', re.compile(r'[^。\n]{0,8}，不是[^。\n]{1,14}[。]')),
]
out = io.open('_tmp_scan.txt', 'w', encoding='utf-8')
tot = 0
for f in files:
    txt = open(f, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    lines = txt.split('\n')
    vol = f.split('_')[0]
    for i, l in enumerate(lines):
        if not l.strip() or l.startswith('#') or l.startswith('|') or l.startswith('---'):
            continue
        plain = q.sub('', l)
        if len(plain.strip()) < 4:
            continue
        for tag, rx in shapes:
            for m in rx.finditer(plain):
                tot += 1
                out.write('%s %s %d| >>%s\n   FULL %s\n' % (vol, tag, i + 1, m.group(0), l[:190]))
                break
out.write('TOTAL %d files %d\n' % (tot, len(files)))
out.close()
print('files', len(files), 'hits', tot)
