# -*- coding: utf-8 -*-
"""同章/同卷整句重复扫描（己类毛病）。叙述卷：卷一/四/五/六/十。文档卷（二/三/七/九）与只读卷八只报不判。
   口径：切句后取汉字数 >= MIN 的句子，在同章内与跨章分别找逐字重复；围栏内与抬头行不计。"""
import io, re, sys, glob

HAN = re.compile(u'[一-鿿]')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 10
NARR = {u'一': '40_卷一_人类反馈_正文.md', u'四': '43_卷四_冻存_正文.md', u'五': '44_卷五_剂量_正文.md',
        u'六': '67_卷六_十一秒_正文.md', u'十': '50_卷十_针脚_正文.md'}
DOC = {u'二': '41_卷二_以斯拉书_正文.md', u'三': '42_卷三_退役访谈_档案卷一.md',
       u'七': '45_卷七_嗯_正文.md', u'九': '48_卷九_记录之外_正文.md'}
OUT = []

def sents(text):
    """yield (line_no, clean_sentence, hanzi_count) outside code fences and headings"""
    fence = False
    for i, ln in enumerate(text.split(u'\n'), 1):
        if ln.strip().startswith(u'```'):
            fence = not fence
            continue
        if fence or ln.startswith(u'#'):
            continue
        for s in re.split(u'[。！？；]', ln):
            s = s.strip(u'“”" 、，:：「」')
            n = len(HAN.findall(s))
            if n >= MIN:
                yield i, s, n

def scan(tag, f, label):
    text = io.open(f, encoding='utf-8').read()
    # chapter index by '## ' offsets
    heads = [(m.start(), m.group(1).strip()) for m in re.finditer(u'(?m)^## (.*)$', text)]
    def chap_of(pos):
        cur = u'(序)'
        for off, h in heads:
            if off <= pos:
                cur = h
            else:
                break
        return cur
    seen = {}
    for i, s, n in sents(text):
        pos = text.index(s, max(0, i * 2 - 200)) if False else None
        seen.setdefault(s, []).append((i, n))
    dup_in = []
    dup_ac = []
    for s, occ in seen.items():
        if len(occ) < 2:
            continue
        chs = []
        for ln, n in occ:
            pos = 0
            for k, l2 in enumerate(text.split(u'\n')[:ln], 0):
                pass
            chs.append(None)
        # locate chapters by line: rebuild line->chapter map once
        dup_in.append((s, occ))
    return seen

# build line->chapter maps once, then report
def line2chap(text):
    lines = text.split(u'\n')
    mp = {}
    cur = u'(序)'
    fence = False
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith(u'```'):
            fence = not fence
        if ln.startswith(u'## ') and not fence:
            cur = ln[3:].strip()
        mp[i] = cur
    return mp

def report(tag, f, label):
    text = io.open(f, encoding='utf-8').read()
    l2c = line2chap(text)
    seen = {}
    for i, s, n in sents(text):
        seen.setdefault(s, []).append(i)
    rep = []
    for s, occ in seen.items():
        if len(occ) < 2:
            continue
        cs = set(l2c[i] for i in occ)
        kind = u'同章' if len(cs) == 1 else u'跨章'
        rep.append((kind, len(occ), s[:46], occ[:4], [l2c[i][:14] for i in occ[:2]]))
    rep.sort(key=lambda r: (r[0], -r[1]))
    OUT.append(u'==== 卷%s (%s) %s  句长>=%d  重复条数=%d' % (tag, label, f, MIN, len(rep)))
    for r in rep:
        OUT.append(u'%s x%d | %s | 行%s | 章%s' % r)

for t, f in NARR.items():
    report(t, f, u'叙述卷')
for t, f in DOC.items():
    report(t, f, u'文档卷·只报')
io.open(u'_tmp_dup.txt', 'w', encoding='utf-8').write(u'\n'.join(OUT))
print(u'wrote _tmp_dup.txt, lines', len(OUT))
