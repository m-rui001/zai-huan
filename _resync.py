# -*- coding: utf-8 -*-
"""通用四址复算：正文改完后跑它。
   1) 用 _verify.py 自己的实测值为唯一真值；
   2) 若任何 MISMATCH，按整行替换该卷元组（不逐格）、改 00 行、_auditall 元组与总数、30 表头与该卷行；
   3) 循环到 done 0。报告写 _tmp_resync.txt（UTF-8）。
   用法：cd E:/Novel2 && python _resync.py [卷号...]   不带参数=全卷扫描"""
import io, re, os, sys, glob, subprocess

HAN = re.compile(u'[\u4e00-\u9fff]')
FILE_OF = {u'\u4e00': '40', u'\u4e8c': '41', u'\u4e09': '42', u'\u56db': '43', u'\u4e94': '44',
           u'\u516d': '67', u'\u5168': '45', u'\u4e03': '45', u'\u516b': '46', u'\u4e5d': '48', u'\u5341': '50'}
F00 = glob.glob('00_*.md')[0]
F30 = glob.glob('30_*.md')[0]


def rd(f):
    return io.open(f, encoding='utf-8', newline='').read()


def wr(f, t):
    io.open(f, 'w', encoding='utf-8', newline='').write(t)


def com(x):
    return u'{:,}'.format(int(x))


def fmt(x):
    return com(x) if float(x) == int(float(x)) else u'%s.5' % com(int(float(x)))


def secstats(f):
    t = rd(f)
    pl = sorted(len(HAN.findall(q)) for q in re.split(u'(?m)^## ', t)[1:] if q.strip())
    n = len(pl)
    med = pl[n // 2] if n % 2 else (pl[n // 2 - 1] + pl[n // 2]) / 2.0
    return n, med, pl[-1]


GLOB = sorted(glob.glob('42*.md'))
# 文件名与 _auditall.py 的 VOLS 一致；不用前缀 glob（曾误取别的 40_* 文件，把全书总数算成 885,718）
BODY = {'40': glob.glob('40_卷一_人类反馈_正文.md')[0], '41': glob.glob('41_卷二_以斯拉书_正文.md')[0],
        '42': GLOB,
        '43': glob.glob('43_卷四_冻存_正文.md')[0], '44': glob.glob('44_卷五_剂量_正文.md')[0],
        '67': glob.glob('67_卷六_十一秒_正文.md')[0],
        '45': glob.glob('45_卷七_嗯_正文.md')[0], '46': glob.glob('46_卷八_晨昏线_正文.md')[0],
        '48': glob.glob('48_卷九_记录之外_正文.md')[0],
        '50': glob.glob('50_卷十_针脚_正文.md')[0]}


def path_of(tag):
    p = BODY[FILE_OF[tag]]
    return p[0] if isinstance(p, list) else p


def total_hanzi():
    n = 0
    for k, p in BODY.items():
        for f in (p if isinstance(p, list) else [p]):
            n += len(HAN.findall(rd(f)))
    return n


ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
LOG = []
targets = sys.argv[1:] or []
prev_total = None
for it in range(6):
    subprocess.run([sys.executable, '_verify.py'], capture_output=True, env=ENV)
    rep = rd('_verify_report.txt').replace('\r', '')
    bad = [l.strip() for l in rep.split('\n') if 'MISMATCH' in l]
    # current measured values per volume
    meas = {}
    for m in re.finditer(u'\u5377(' + u'|'.join(FILE_OF) + u') hanzi (\\d+) secs (\\d+) avg ([\\d.]+) l20 ([\\d.]+) dlg ([\\d.]+) brk ([\\d.]+) digits (\\d+) pw (\\d+)', rep):
        g = m.groups()
        meas[g[0]] = dict(zip('h secs avg l20 dlg brk digits pw'.split(), g[1:]))
    LOG.append('iter %d flagged %d: %s' % (it, len(bad), u' / '.join(bad)))
    if not bad:
        break
    want = {}
    for b in bad:
        mm = re.match(r'MISMATCH (\w+) ([\d.]+)!=([\d.]+)', b)
        if mm:
            want[mm.group(2)] = None  # not volume-specific; use file scan below
    # figure out which volumes are flagged by comparing tuple vs measurement
    tv = rd('_verify.py')
    vols = re.findall(u"\\('(.*?)', '[^']*', ([^)]*)\\)", tv)
    flagged = set()
    for m in bad:
        mm = re.match(r'MISMATCH (hanzi|avg|l20|digits|perwan|dialogue) ([\d.]+)!=', m)
        if mm:
            val = mm.group(2)
            keymap = {'hanzi': 'h', 'avg': 'avg', 'l20': 'l20', 'digits': 'digits', 'perwan': 'pw', 'dialogue': 'dlg'}
            for tag, d in meas.items():
                if val == d['h'] or val == d[keymap[mm.group(1)]]:
                    flagged.add(tag)
    if not flagged:
        flagged = set(meas)
    for tag in flagged:
        if tag not in meas:
            continue
        d = meas[tag]
        old = re.findall(u"\\('%s',[^)]*\\)" % tag, tv)
        if len(old) != 1:
            LOG.append('WARN tuple not unique for %s' % tag)
            continue
        parts = [x.strip() for x in old[0].strip('()').split(',')]
        newl = u"('%s', %s, %s, %s, %s, %s, %s, %s, %s)" % (
            tag, parts[1], d['h'], d['secs'], d['avg'], d['l20'],
            'None' if parts[6] == 'None' else d['dlg'],
            'None' if parts[7] == 'None' else d['digits'], d['pw'])
        if old[0] != newl:
            LOG.append('verify tuple %s: %s  ->  %s' % (tag, old[0], newl))
        tv = tv.replace(old[0], newl)
    tot = total_hanzi()
    for lit in set(re.findall(r'\b9\d{5}\b', tv)):
        if int(lit) != tot:
            LOG.append('verify total %s -> %s' % (lit, tot))
            tv = tv.replace(lit, str(tot))
    wr('_verify.py', tv)
    # 00 rows
    t0 = rd(F00)
    for i, l in enumerate(t0.split('\n')):
        pass
    L = t0.split('\n')
    for i, l in enumerate(L):
        mm = re.match(r'^\| (\S) \|', l)
        if not mm or l.count('|') < 10:
            continue
        tag = mm.group(1)
        if tag not in meas or tag not in flagged:
            continue
        d = meas[tag]
        c = l.split('|')
        f = path_of(tag)
        try:
            n, med, mx = secstats(f)
        except Exception as e:
            LOG.append('secstats failed %s: %s' % (tag, e))
            continue
        old_cells = [x.strip() for x in c]
        c[2] = u' %s ' % com(int(d['h']))
        if old_cells[4] not in (u'\u2014',):
            c[4] = u' %s ' % fmt(med)
        if old_cells[5] not in (u'\u2014',):
            c[5] = u' %s ' % com(mx)
        # 第 3 栏（节数）与第 8 栏（对话）永不自动改写：三 记「档案」，六／七／九／十 的对话栏各有自己的尺与脚注（‡ † * ※）
        for key, idx in (('avg', 6), ('l20', 7), ('pw', 9)):
            if u'\u2014' in c[idx] or u',' in c[idx]:
                continue
            val = d[key]
            sm = re.match(u'^\\s*([\\d.]+)\\s*(.*)$', c[idx])
            if sm is None:
                continue
            if float(val) != float(sm.group(1)):
                c[idx] = u' %s%s ' % (val, sm.group(2))   # 保留 % 与脚注标记（***、※）
                LOG.append('00 cell %s[%d] -> %s (suffix %r)' % (tag, idx, val, sm.group(2)))
        L[i] = u'|'.join(c)
    t0 = u'\n'.join(L)
    for lit in set(re.findall(r'9[\d,]{5,7}', t0)):
        if lit.replace(',', '') != str(tot) and len(lit.replace(',', '')) == 6:
            t0 = t0.replace(lit, com(tot))
            LOG.append('00 total %s -> %s' % (lit, com(tot)))
    wr(F00, t0)
    # _auditall 的每卷字数行由文件末尾的无条件同步块改写；这里只处理总数面值
    ta = rd('_auditall.py')
    for lit in set(re.findall(r'9[,\d]{5,7}', ta)):
        if lit.replace(',', '') != str(tot) and len(lit.replace(',', '')) == 6:
            ta = ta.replace(lit, com(tot) if ',' in lit else str(tot))
            LOG.append('auditall total literal replaced: %s' % lit)
    wr('_auditall.py', ta)
    # 30: header line 3 and current-state rows
    t3 = rd(F30)
    E3 = '\r\n' if '\r\n' in t3 else '\n'
    L3 = t3.split(E3)
    for i, l in enumerate(L3):
        s = l.rstrip('\r')
        if i == 2:
            ns = re.sub(r'9[\d,]{5,7}', com(tot), s)
            if ns != s:
                LOG.append('30 header -> %s' % com(tot))
            L3[i] = ns
        else:
            mm = re.match(r'^\| \u5377(\S) \|', s)
            if mm and mm.group(1) in meas and s.count('|') >= 3:
                c = s.split('|')
                cur = c[3].strip().replace(',', '') if len(c) > 3 else ''
                if cur.isdigit() and int(cur) != int(meas[mm.group(1)]['h']):
                    LOG.append('30 row %s %s -> %s' % (mm.group(1), c[3].strip(), com(int(meas[mm.group(1)]['h']))))
                    c[3] = u' %s ' % com(int(meas[mm.group(1)]['h']))
                    L3[i] = u'|'.join(c)
    wr(F30, E3.join(L3))
    prev_total = tot


# --- unconditional _auditall row sync (fixes stale per-volume literals even when _verify is clean) ---
ta = rd('_auditall.py')
for tag, pre in FILE_OF.items():
    if pre not in BODY:
        continue
    _p = BODY[pre]
    h = sum(len(HAN.findall(rd(f))) for f in (_p if isinstance(_p, list) else [_p]))
    for _ln in [x for x in ta.splitlines() if x.strip().startswith("('" + tag + "',") and x.rstrip().endswith('),')]:
        n = re.sub(r',\s*\d+\)\s*,\s*$', u', %s),' % h, _ln)
        if n != _ln:
            ta = ta.replace(_ln, n)
            LOG.append('auditall row %s -> %d' % (tag, h))
wr('_auditall.py', ta)

p = subprocess.run([sys.executable, '_auditall.py'], capture_output=True, env=ENV)
rep = rd('_verify_report.txt').replace('\r', '')
ok = 'MISMATCH' not in rep
audit = p.stdout.decode('utf-8', 'replace').replace('\r', u' ')
LOG.append('FINAL verify %s total %s || audit %s' % ('CLEAN' if ok else 'DIRTY', total_hanzi(), audit[-260:]))
LOG.append(u'\u5168\u4e66 hanzi = %s' % com(total_hanzi()))
io.open('_tmp_resync.txt', 'w', encoding='utf-8', newline='\n').write(u'\n'.join(LOG) + u'\n')
print('verify', 'CLEAN' if ok else 'DIRTY', 'total', total_hanzi())
