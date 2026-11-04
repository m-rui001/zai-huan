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
# 同线：引文收束 + ≤14 字（不含换行/引号）+ 标点 + 紧接着另起引文
RESUME = re.compile(u'\u201d[^\u201d\u201c\n]{1,14}，\u201c')
RESTART = re.compile(u'\u201d[^\u201d\u201c\n]{1,14}。\u201c')
# 跨段：本段以 。” 收束，标签自成一句在段末（或段中），下一段以 “ 开头
PARA_TAG = re.compile(u'[^\u201d\u201c\n]{1,14}。\u201d[^\n]{0,14}(说|问|道|答)[^\n]{0,10}。\n\u201c')
SPEECH = re.compile(u'说|问|答|念|报|道|笑|嘟囔|重复')
TAG_ANY = re.compile(u'\u201d[^\u201d\u201c\n]{1,14}[。，]\u201c')
o = io.StringIO()
o.write(u'vol  resume_same  restart_same  restart_with_speech  para_tag  brk  hz\n')
rows = []
for v in sorted(FILES, key=lambda x: u'一二三四五六七八九十'.index(x)):
    t = ''.join(io.open(f, encoding='utf-8').read() for f in FILES[v])
    hz = len(re.findall(HZ, t))
    r = len(RESUME.findall(t))
    s_all = len(RESTART.findall(t))
    s_tag = 0
    s_tag = len([m for m in RESTART.finditer(t) if SPEECH.search(m.group(0)[1:-2])])
    p = len(PARA_TAG.findall(t))
    brk = len(re.findall(u'\u300c[^\u300d]*\u300d', t))
    rows.append((v, r, s_all, s_tag, p, brk, hz))
    o.write(u'%s  %6d  %6d  %6d  %6d  brk %5d  hz %d\n' % (v, r, s_all, s_tag, p, brk, hz))
for v, r, s_all, s_tag, p, brk, hz in rows:
    tot = r + s_all
    if tot:
        o.write(u'%s share_resume %.1f%%   share_resume(仅含说话动词标签) ' % (v, r / float(tot) * 100))
        d = r + s_tag
        o.write(u'%s%%\n' % (r / float(d) * 100 if d else 0))
io.open(u'_tmp_tag2.txt', 'w', encoding='utf-8').write(o.getvalue())
print('ok')
