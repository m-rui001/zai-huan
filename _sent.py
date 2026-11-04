import re, io, sys, glob

def hz(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))

def measure(p):
    files = sorted(glob.glob(p)) if '*' in p else [p]
    t = '\n'.join(io.open(f, encoding='utf-8').read() for f in files)
    parts = re.split(r'(```.*?```)', t, flags=re.S)
    prose = []
    for part in parts:
        if not part.startswith('```'):
            prose.append(part)
    prose = ''.join(prose)
    prose = re.sub(r'(?m)^#.*$', '', prose)
    body = re.sub(r'(?m)^#.*$', '', t)
    def sents(x):
        return [s for s in re.split(r'(?<=[。！？])', x) if hz(s)]
    ps = sents(prose)
    alls = sents(body)
    pl = [hz(s) for s in ps]
    al = [hz(s) for s in alls]
    def share(l, n):
        return round(sum(1 for x in l if x >= n) / len(l) * 100, 1)
    ad = [abs(pl[i] - pl[i-1]) for i in range(1, len(pl))]
    low = round(sum(1 for x in ad if x <= 3) / len(ad) * 100, 1)
    narr = [s for s in ps if not re.match(r'^\s*[“「"]', s.strip())]
    nl = [hz(s) for s in narr]
    nad = [abs(nl[i] - nl[i-1]) for i in range(1, len(nl))]
    nlow = round(sum(1 for x in nad if x <= 3) / len(nad) * 100, 1)
    name = files[0].split('_')[1] if '_' in files[0] else files[0]
    print(f"{name}\tall_n={len(al)}\tall>=60={share(al,60)}\tprose_n={len(pl)}\tprose>=60={share(pl,60)}\tprose>=80={share(pl,80)}\tadj<=3={low}\tnarr>=60={share(nl,60)}\tnarr_adj<=3={nlow}")

for p in sys.argv[1:]:
    measure(p)
