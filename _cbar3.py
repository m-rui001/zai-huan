# -*- coding: utf-8 -*-
# _cbar3.py —— C 栏样张尺 v3：样张按自然段边界成块（不从段落中间切开），
# 最佳窗按「过线条数 k，再看三特征相对偏差之和」排名，避免单靠句均/短句两维挑窗、
# 把标题块之类的偶然段长方差当成装置强度。
import io, re, glob, statistics, math

HAN = re.compile(u'[\u4e00-\u9fff]')
SENT = re.compile(u'[^\u3002\uff01\uff1f\r\n]+[\u3002\uff01\uff1f]?')
VOLS = [('一', ['40_卷一_人类反馈_正文.md']), ('二', ['41_卷二_以斯拉书_正文.md']),
        ('三', sorted(glob.glob('42*.md'))), ('四', ['43_卷四_冻存_正文.md']),
        ('五', ['44_卷五_剂量_正文.md']), ('六', ['67_卷六_十一秒_正文.md']),
        ('七', ['45_卷七_嗯_正文.md']), ('八', ['46_卷八_晨昏线_正文.md']),
        ('九', ['48_卷九_记录之外_正文.md']), ('十', ['50_卷十_针脚_正文.md'])]
CR = chr(13)
SIZE = 2000


def load(fs):
    return ''.join(io.open(f, encoding='utf-8', newline='').read().replace(CR, '') for f in fs)


def feat(t):
    ss = [s.strip() for s in SENT.findall(t) if HAN.search(s)]
    ls = [len(HAN.findall(s)) for s in ss]
    ls = [x for x in ls if x > 0]
    if not ls:
        return None
    pars = [q for q in t.split('\n\n') if HAN.search(q)]
    pl = [len(HAN.findall(q)) for q in pars]
    pv = statistics.pvariance(pl) if len(pl) > 1 else 0.0
    return [sum(ls) / float(len(ls)), 100.0 * sum(1 for x in ls if x <= 20) / len(ls), pv]


def chunks(t):
    """按自然段累积成约 SIZE 汉字的块；块边界只落在段落之间。"""
    pars = t.split('\n\n')
    out, cur, curn = [], [], 0
    for q in pars:
        h = len(HAN.findall(q))
        if curn + h > SIZE and cur:
            out.append('\n\n'.join(cur))
            cur, curn = [q], h
        else:
            cur.append(q)
            curn += h
    if cur and curn >= SIZE // 2:
        out.append('\n\n'.join(cur))
    return out


texts, full = {}, {}
for n, fs in VOLS:
    t = load(fs)
    texts[n] = t
    full[n] = feat(t)
names = [n for n, _ in VOLS]
mean = [sum(full[n][i] for n in names) / len(names) for i in range(3)]
sd = [math.sqrt(sum((full[n][i] - mean[i]) ** 2 for n in names) / len(names)) or 1 for i in range(3)]


def z(v):
    return [(v[i] - mean[i]) / sd[i] for i in range(3)]


lines = [u'vol  full(avg le20 pvar)  blocks  pass2/3  passrate  bestblock k(avg le20 pvar)  delta%  nearest(full-z)']
for n in names:
    f = full[n]
    ws = chunks(texts[n])
    hits, best = 0, None
    for w in ws:
        v = feat(w)
        if not v:
            continue
        d = [(v[i] - f[i]) / f[i] * 100 if f[i] else 0 for i in range(3)]
        k = sum(1 for i in range(3) if abs(d[i]) >= 15)
        if k >= 2:
            hits += 1
        score = (k, sum(abs(x) / 15.0 for x in d))
        if best is None or score > best[0]:
            best = (score, v, d, k)
    zd = sorted(((math.sqrt(sum((z(best[1])[i] - z(full[m])[i]) ** 2 for i in range(3))), m)
                 for m in names if m != n))
    lines.append(u'%s  %.2f  %.1f  %.0f   %d  %.0f%%  k=%d  %.2f %.1f %.0f   %s   %s %.2f' % (
        n, f[0], f[1], f[2], len(ws), 100.0 * hits / max(1, len(ws)), best[3],
        best[1][0], best[1][1], best[1][2],
        u' '.join(u'%+.0f' % x for x in best[2]), zd[0][1], zd[0][0]))
io.open('_cbar3_out.txt', 'w', encoding='utf-8', newline='').write(u'\n'.join(lines) + u'\n')
print('ok')
