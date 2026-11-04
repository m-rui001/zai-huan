# -*- coding: utf-8 -*-
import io, re, glob

HZ = u'[\u4e00-\u9fff]'
FILES = {
 u'一': ['40_卷一_人类反馈_正文.md'], u'二': ['41_卷二_以斯拉书_正文.md'],
 u'三': sorted(glob.glob('42*.md')), u'四': ['43_卷四_冻存_正文.md'],
 u'五': ['44_卷五_剂量_正文.md'], u'六': ['67_卷六_十一秒_正文.md'],
 u'七': ['45_卷七_嗯_正文.md'], u'八': ['46_卷八_晨昏线_正文.md'],
 u'九': ['48_卷九_记录之外_正文.md'], u'十': ['50_卷十_针脚_正文.md'],
}
SENT = re.compile(u'(?<=[。！？])')
o = io.StringIO()
o.write(u'vol  sentences  chain>=3逗号&>=40字  chains/万字  汉字占chain份额%  平均链长  链内平均逗号数\n')
rows = []
for v in sorted(FILES, key=lambda x: u'一二三四五六七八九十'.index(x)):
    t = ''.join(io.open(f, encoding='utf-8').read() for f in FILES[v])
    hz = len(re.findall(HZ, t))
    body = re.sub(r'(?m)^#.*$', '', t)
    ss = [s.strip() for s in SENT.split(body) if re.findall(HZ, s)]
    ch = []
    for s in ss:
        n = len(re.findall(HZ, s))
        c = s.count(u'，')
        if c >= 3 and n >= 40:
            ch.append((n, c))
    share = sum(n for n, _ in ch) / float(hz) * 100 if hz else 0.0
    avglen = (sum(n for n, _ in ch) / float(len(ch))) if ch else 0.0
    avgc = (sum(c for _, c in ch) / float(len(ch))) if ch else 0.0
    rows.append((v, len(ss), len(ch), 10000.0 * len(ch) / hz, share, avglen, avgc))
    o.write(u'%s  %6d  %5d  %8.1f  %8.1f%%  %6.1f  %5.2f\n' % (
        v, len(ss), len(ch), 10000.0 * len(ch) / hz, share, avglen, avgc))
o.write(u'\n按 链/万字 排序：' + u' > '.join(u'%s %.1f' % (r[0], r[3]) for r in sorted(rows, key=lambda r: -r[3])) + u'\n')
io.open(u'_tmp_chain.txt', 'w', encoding='utf-8').write(o.getvalue())
print('ok')
