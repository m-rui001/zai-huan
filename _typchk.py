# -*- coding: utf-8 -*-
"""打印本逐卷回验：源正文每一段是否原样进了 PDF；顺带查 markdown 残渣。

用法：python _typchk.py → _typ_report.txt
"""
import io, os, re
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(ROOT, '在环_十卷_打印本.pdf')
REP = os.path.join(ROOT, '_typ_report.txt')

VOL3 = ['42_卷三_退役访谈_档案卷一.md'] + [
    '42%s_卷三_退役访谈_档案卷%s.md' % (c, n) for c, n in zip(
        'bcdefghijklm', '二 三 四 五 六 七 八 九 十 十一 十二 十三'.split())] + ['42n_卷三_未归档.md']
VOLS = [
    ('卷一', ['40_卷一_人类反馈_正文.md']),
    ('卷二', ['41_卷二_以斯拉书_正文.md']),
    ('卷三', VOL3),
    ('卷四', ['43_卷四_冻存_正文.md']),
    ('卷五', ['44_卷五_剂量_正文.md']),
    ('卷六', ['67_卷六_十一秒_正文.md']),
    ('卷七', ['45_卷七_嗯_正文.md']),
    ('卷八', ['46_卷八_晨昏线_正文.md']),
    ('卷九', ['48_卷九_记录之外_正文.md']),
    ('卷十', ['50_卷十_针脚_正文.md']),
]

TAG = re.compile(r'<[^>]+>')
TRANS = [('…', '...'), ('——', '-'), ('—', '-'), ('–', '-'), ('−', '-')]
DROP = '|｜"\'“”‘’'


def norm(s):
    """剥掉 markdown 记号、竖线分隔与引号形，只留可比对的正文"""
    s = s.replace('**', '').replace('`', '')
    if s.count('*') % 2 == 0:      # 成对的星号按emphasis 处理，单个（键名 internal.*）保留
        s = s.replace('*', '')
    s = s.replace('\\', '')
    s = TAG.sub('', s)
    s = re.sub(r'^#{1,6}\s*', '', s)
    s = re.sub(r'^>\s?', '', s)
    s = re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', s)
    for ch in DROP:
        s = s.replace(ch, '')
    for x, y in TRANS:
        s = s.replace(x, y)
    return re.sub(r'\s+', '', s)


def paras(path):
    txt = io.open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    res, fence = [], False
    for ln in txt.split('\n'):
        if ln.startswith('```'):
            fence = not fence
            continue
        t = ln.strip()
        if not t or fence:
            continue
        if re.match(r'^-{3,}$', t):
            continue
        if re.match(r'^#{1,6}\s', t):
            continue
        if re.match(r'^\|?[\s:|-]+\|[\s:|-]*$', t) and '--' in t:
            continue
        res.append(t)
    return res


def clean(t):
    for ch in DROP:
        t = t.replace(ch, '')
    for x, y in TRANS:
        t = t.replace(x, y)
    return re.sub(r'\s+', '', t)


doc = pymupdf.open(PDF)
N = doc.page_count
toc1 = [x for x in doc.get_toc() if x[0] == 1 and x[1].startswith('卷')]
starts = [x[2] for x in toc1]
assert len(starts) == len(VOLS), (len(starts), [x[1] for x in toc1])
out = ['pages %d' % N]
tot_miss = 0
for k, (name, files) in enumerate(VOLS):
    lo = starts[k]
    hi = starts[k + 1] - 1 if k + 1 < len(starts) else N
    blob = clean(''.join(
        doc[p].get_text('text', clip=pymupdf.Rect(
            0, 60, doc[p].rect.width, doc[p].rect.height - 58))
        for p in range(lo - 1, hi)))
    miss, tot = [], 0
    for f in files:
        for p in paras(os.path.join(ROOT, f)):
            q = norm(p)
            if not q:
                continue
            tot += 1
            if q not in blob:
                if p.lstrip().startswith('|') and all(
                        norm(x) and norm(x) in blob for x in p.split('|') if x.strip()):
                    continue
                miss.append((f, p))
    tot_miss += len(miss)
    out.append('%s 页 %d-%d 段 %d 未命中 %d' % (name, lo, hi, tot, len(miss)))
    for f, p in miss[:12]:
        out.append('   MISS %s %s' % (f, p[:80]))
pats = ('**', '```', '####', '\\#', '&amp;', '&lt;', '#raw(', 'align.center')
junk = dict((x, 0) for x in pats)
for i in range(N):
    t = doc[i].get_text('text')
    for x in pats:
        c = t.count(x)
        if c:
            junk[x] += c
out.append('junk %s' % junk)
out.append('未命中合计 %d / 段 %d' % (tot_miss, 0))
io.open(REP, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('report written, misses', tot_miss)
