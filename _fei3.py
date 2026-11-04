# -*- coding: utf-8 -*-
import io, os, re

files = sorted([f for f in os.listdir('.') if f.endswith('_正文.md')])
out = []
tot = 0
for f in files:
    t = io.open(f, 'rb').read().decode('utf-8').replace('\r\n', '\n').split('\n')
    hits = []
    for i, l in enumerate(t, 1):
        s = l.strip()
        if not s:
            continue
        # narration voice only: not a quote-embedded line, not speaker-prefixed, not fenced
        if s.startswith(('#', '>', '|', '```', '【')):
            continue
        if re.match(r'^(\*\*)?[^\s「“”"]{1,6}：', s):
            continue
        body = s
        # strip quoted spans
        body = re.sub(r'[“「][^”」]*[”」]', '', body)
        body = re.sub(r'「[^」]*」', '', body)
        for m in re.finditer(r'不是[^，。\n]{1,14}[，。]\s*(而是|只是|是)|不在于[^，。\n]{1,14}而在', body):
            hits.append((i, m.group(0)))
    tot += len(hits)
    out.append('%s  n=%d' % (f.split('_')[0], len(hits)))
    for i, h in hits:
        out.append('   %d|%s' % (i, h))

sw = []
for f in files:
    t = io.open(f, 'rb').read().decode('utf-8').replace('\r\n', '\n').split('\n')
    for i, l in enumerate(t, 1):
        if '所谓' in l or '——' in l:
            sw.append('%s %d|%s' % (f.split('_')[0], i, l.strip()[:60]))
out.append('==== TOTAL narration-family %d' % tot)
out.append('==== 46 所谓/破折号')
out += [x for x in sw if x.startswith('46')]
io.open('_fei3.txt', 'wb').write('\n'.join(out).encode('utf-8'))
print('ok', tot)
