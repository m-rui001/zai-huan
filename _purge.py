import os, re, glob, time, shutil, collections

GO = '--go' in os.sys.argv
BAK_CUTOFF = time.mktime(time.strptime('2026-10-31', '%Y-%m-%d'))   # older than this: drop the whole copy
BAK_KEEP_PER_BASE = 1
PROTECT = {'_keys.json', '_purge.py', '_tidy.py'}
DROP_DIRS = ['_snap', '__pycache__', '_gr', '_gr2', '_blind', '_blind2', '_work']
BAK_DIR = '_bak'

victims, reasons = [], {}


def mark(f, why):
    b = os.path.basename(f)
    if b in PROTECT or f.endswith('.json'):
        return
    if os.path.dirname(f) == '' and f.endswith('.md') and not f.startswith('_snap'):
        return                     # drafts, ledgers and settings never go
    victims.append(f)
    reasons[f] = why


def base_of(name):
    k = re.split(r'\.bak', name)[0]
    return re.sub(r'_[0-9a-f]{6,}$', '', k)


groups = collections.defaultdict(list)
for f in os.listdir('.'):
    if os.path.isdir(f) or '.bak' not in f:
        continue
    groups[base_of(f)].append(f)

kept_bak = []
for k, fs in groups.items():
    fs.sort(key=lambda x: -os.path.getmtime(x))
    fresh = [f for f in fs[:BAK_KEEP_PER_BASE] if os.path.getmtime(f) >= BAK_CUTOFF]
    kept_bak += fresh
    for f in fs:
        if f not in fresh:
            mark(f, 'BAK')

for f in glob.glob('_snap*'):
    if os.path.isfile(f):
        mark(f, 'SNAP')

for f in os.listdir('.'):
    if os.path.isdir(f) or not f.startswith('_') or f.endswith('.py'):
        continue
    if '.bak' in f or f in victims:
        continue
    mark(f, 'SCRATCH')

for f in glob.glob(os.path.join('_work', '**', '*'), recursive=True):
    if os.path.isfile(f):
        mark(f, 'ONEOFF')

for d in DROP_DIRS:
    if os.path.isdir(d):
        for r, _, fs in os.walk(d):
            for fn in fs:
                p = os.path.join(r, fn)
                if p not in victims:
                    mark(p, 'DIRTREE')

victims = sorted(set(victims))
mb = sum(os.path.getsize(f) for f in victims if os.path.isfile(f)) / 1048576.0
print('delete %d files, %.1f MB ; keep %d fresh backups -> %s/' % (len(victims), mb, len(kept_bak), BAK_DIR))
for k, v in sorted(collections.Counter(reasons.get(f, 'DIRTREE') for f in victims).items(), key=lambda x: -x[1]):
    print('  %-8s %d' % (k, v))

if GO:
    os.makedirs(BAK_DIR, exist_ok=True)
    for f in victims:
        if os.path.isfile(f):
            try:
                os.remove(f)
            except OSError as e:
                print('ERR', f, e)
    for d in DROP_DIRS:
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
    for f in kept_bak:
        if not os.path.isfile(f):
            continue
        stamp = time.strftime('%Y%m%d', time.localtime(os.path.getmtime(f)))
        shutil.move(f, os.path.join(BAK_DIR, '%s.%s.bak' % (base_of(f), stamp)))
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    dirs = [f for f in os.listdir('.') if os.path.isdir(f)]
    print('top-level now: %d files, %d dirs' % (len(files), len(dirs)))
    print('dirs: ' + ', '.join(sorted(dirs)))
    ext = collections.Counter(os.path.splitext(f)[1] or '(none)' for f in files)
    print('files by ext: ' + ', '.join('%s=%d' % (k, v) for k, v in ext.most_common()))
