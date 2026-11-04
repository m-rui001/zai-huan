import io, re, sys, glob

vol = sys.argv[1]          # e.g. '50'
src = [x for x in glob.glob(vol + '_*.md') if '_正文' in x and 'backup' not in x][0]
txt = io.open(src, encoding='utf-8', newline='').read().replace('\r\n', '\n')
lines = txt.split('\n')
files = sorted(glob.glob('_cbd/k' + vol + '*_*.md'))
out = io.open('_tmp_chk_' + vol + '.txt', 'w', encoding='utf-8')

def find(s):
    s = s.strip().strip('**').strip()
    s = s.replace('\u201c', '“').replace('\u201d', '”').replace('"', '“')
    for q in ['“', '”', '「', '」', '\u2018', '\u2019', "'", '‘', '’']:
        s = s.replace(q, '')
    s = s.strip()
    if len(s) < 6:
        return None, 0, []
    hits = [i + 1 for i in range(len(lines)) if s in lines[i]]
    return s, len(hits), hits

for f in files:
    out.write('===== %s =====\n' % f)
    cls = ''
    for ln in io.open(f, encoding='utf-8').read().replace('\r\n', '\n').split('\n'):
        m = re.match(r'^\s*[*#\-\s]*([ABCD])\b', ln)
        if m and '｜' not in ln:
            cls = m.group(1)
            continue
        if '｜' not in ln:
            continue
        parts = ln.split('｜')
        coord = re.sub(r'^[^0-9]*', '', parts[0])[:22]
        body = parts[1] if len(parts) > 1 else ''
        s, n, hits = find(body)
        if s is None:
            out.write(' %s %s |SNIP-TOO-SHORT|\n' % (cls, coord))
        else:
            out.write(' %s %s |n=%d| %s | %s\n' % (
                cls, coord, n, s[:34], ('L' + ','.join(map(str, hits[:5])) if hits else 'NOT-ON-PAGE')))
    out.write('\n')
out.close()
print('checked', len(files), 'reports')
