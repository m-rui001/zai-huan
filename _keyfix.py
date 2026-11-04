import json, os, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '_keys.json')
CFG = json.load(open(P, encoding='utf-8'))
rows = []
for name, c in CFG.items():
    if name == 'cssm-grok':
        rows.append('%s skip (key dead)' % name)
        continue
    req = urllib.request.Request(c['baseUrl'].rstrip('/') + '/models', headers={
        "Authorization": "Bearer " + c['apiKey'], "User-Agent": "opencode/1.1.4",
        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.loads(r.read().decode('utf-8', 'replace'))
        ids = [m.get('id') for m in (j.get('data') or []) if m.get('id')]
        old = len(c.get('models') or [])
        c['models'] = ids
        rows.append('%s updated %d -> %d' % (name, old, len(ids)))
    except Exception as e:
        rows.append('%s ERR %r (models left as-is)' % (name, repr(e)[:70]))
        continue

tmp = P + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(CFG, f, ensure_ascii=False, indent=2)
# 校验回读，确认 key 字段没丢
chk = json.load(open(tmp, encoding='utf-8'))
missing = [n for n in CFG if n not in chk or 'apiKey' not in chk[n] or not chk[n]['apiKey']]
rows.append('providers=%d missing_keys=%d' % (len(chk), len(missing)))
if not missing:
    os.replace(tmp, P)
    rows.append('WRITTEN')
open(os.path.join(HERE, '_tmp_keyfix.txt'), 'w', encoding='utf-8').write('\n'.join(rows))
