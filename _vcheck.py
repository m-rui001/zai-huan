import re, os, sys
MAP = {'40':'40_卷一_人类反馈_正文.md','41':'41_卷二_以斯拉书_正文.md','42':'42_卷三_退役访谈_档案卷一.md',
       '43':'43_卷四_冻存_正文.md','44':'44_卷五_剂量_正文.md','45':'45_卷七_嗯_正文.md',
       '46':'46_卷八_晨昏线_正文.md','48':'48_卷九_记录之外_正文.md','50':'50_卷十_针脚_正文.md',
       '67':'67_卷六_十一秒_正文.md'}
for f in os.listdir('.'):
    if f.endswith('.md') and re.match(r'^42[a-z]?_卷三', f):
        MAP['42'+f[2]] = f
Q = re.compile(r'[「」“”﹁﹂＂]')
def strip(s):
    return Q.sub('', s)
texts = {}
for k, v in MAP.items():
    if os.path.exists(v):
        texts[k] = [strip(l) for l in open(v, encoding='utf-8').read().split('\n')]
rep = open(sys.argv[1], encoding='utf-8').read()
pat = re.compile(r'\b(4[0-8]|67|50)([a-n])?:(\d+)\s*[「“]([^」”\n]{5,120})[」”]')
seen = {}
for m in pat.finditer(rep):
    key, suf, ln, q = m.group(1), m.group(2), int(m.group(3)), strip(m.group(4)).strip()
    fk = key + (suf or '')
    k = fk if fk in texts else key
    seen[(k, ln, q)] = None
miss = drift = 0
for (k, ln, q) in seen:
    src = texts.get(k, [])
    hits = [i for i, l in enumerate(src, 1) if q in l]
    if not hits:
        frag = [x.strip() for x in re.split(r'…+|＋', q) if len(x.strip()) >= 6]
        ok = bool(frag) and all(any(f in l for t in texts.values() for l in t) for f in frag)
        miss += 1
        print('MISSING(%s) %s:%d  %s' % ('frag-ok' if ok else 'ABSENT', k, ln, q[:60]))
    elif ln not in hits:
        drift += 1
        print('DRIFT  %s:%d -> %s  %s' % (k, ln, hits[:4], q[:55]))
print('checked=%d missing=%d drift=%d' % (len(seen), miss, drift))
