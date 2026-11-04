import json, os, re, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, '_keys.json'), encoding='utf-8'))[os.environ.get('GRPROV', 'cssm-grok')]
BASE, KEY = CFG['baseUrl'], CFG['apiKey']
H = {"Authorization": "Bearer " + KEY, "User-Agent": "opencode/1.1.4",
     "Content-Type": "application/json", "Accept": "application/json"}
OUT = os.path.join(HERE, '_gr')
os.makedirs(OUT, exist_ok=True)

vol = sys.argv[1] if len(sys.argv) > 1 else '48'
slug = sys.argv[2] if len(sys.argv) > 2 else 'nine'
gsize = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
maxtok = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
models = (sys.argv[5] if len(sys.argv) > 5 else 'grok-4.7').split(',')

_cands = sorted(f for f in os.listdir(HERE) if f.startswith(vol + '_') and f.endswith('.md')
               and 'backup' not in f)
_body = [f for f in _cands if '_正文' in f]
src = (_body or _cands)[0]
text = open(os.path.join(HERE, src), encoding='utf-8').read()
lines = text.split('\n')

# 行号对齐：按行累加，切到 ~gsize 汉字，段落边界断开
chunks, cur, start, n = [], [], 1, 0
for i, l in enumerate(lines):
    cur.append('%d| %s' % (i + 1, l) if l.strip() else '%d|' % (i + 1))
    n += len(re.findall(r'[\u4e00-\u9fff]', l))
    if n >= gsize and (not l.strip()):
        chunks.append((start, '\n'.join(cur)))
        cur, start, n = [], i + 2, 0
if cur:
    chunks.append((start, '\n'.join(cur)))

PROMPT = """你是逐句读手。编辑的活你不做。下面是一部中文长篇小说的第 {k}/{tot} 段，每行行首是原文件的行号。

只做三件事，逐条报坐标，格式严格为：行号 || 原文照录 || 一句理由

一、同一场内的逐字回声：同一个短语或同一个句式在两三百字内出现第二次，且两次没有换关系。
二、叙述层替读者结算：叙述人把人物本该自己得出的判断直接写出来（结论句、意义句、"这说明"类）。
三、无根据的器物：某件物品/数字被用来承重，但在这个场景里此前没有任何来路。

规矩：
- 原文必须一字不改照录，包括标点；找不到确切原文就不要报。
- 不开处方，不改写，不解释你的方法，不总结，不寒暄，不复述本提示。
- 判不准就不报。宁少勿错。
- 没有命中就只输出这一行：NONE

正文：
{body}
"""

log = open(os.path.join(HERE, '_gr_%s.log' % slug), 'w', encoding='utf-8', buffering=1)
log.write('src %s chunks %d models %s gsize %d maxtok %d\n' % (src, len(chunks), models, gsize, maxtok))

LO = int(os.environ.get('GRFROM', '1'))
HI = int(os.environ.get('GRTO', '9999'))
log.write('range %d-%d of %d\n' % (LO, HI, len(chunks)))
for idx, (startline, body) in enumerate(chunks, 1):
    op = os.path.join(OUT, '%s_%02d.md' % (slug, idx))
    if idx < LO or idx > HI:
        continue
    if os.path.exists(op) and os.path.getsize(op) > 5:
        log.write('skip %d cached\n' % idx)
        continue
    msg = PROMPT.format(k=idx, tot=len(chunks), body=body)
    got = None
    for try_i in range(3):
        for model in models:
            req = urllib.request.Request(BASE.rstrip('/') + '/chat/completions',
                                         data=json.dumps({"model": model, "messages": [
                                             {"role": "user", "content": msg}],
                                             "temperature": 0.15, "max_tokens": maxtok,
                                             "stream": False}).encode('utf-8'), headers=H)
            try:
                with urllib.request.urlopen(req, timeout=420) as r:
                    j = json.loads(r.read().decode('utf-8', 'replace'))
                got = ((j.get('choices') or [{}])[0].get('message') or {}).get('content') or ''
                if got.strip():
                    log.write('chunk %d ok via %s\n' % (idx, model))
                    break
                got = None
            except urllib.error.HTTPError as e:
                log.write('chunk %d try %d %s HTTP %s %s\n' % (idx, try_i, model, e.code,
                                                            e.read().decode('utf-8', 'replace')[:80]))
            except Exception as e:
                log.write('chunk %d try %d %s ERR %r\n' % (idx, try_i, model, repr(e)[:120]))
        if got:
            break
        time.sleep(25 + 20 * try_i)
    if not got:
        log.write('chunk %d FAILED\n' % idx)
        continue
    open(op, 'w', encoding='utf-8').write(got)
    log.write('chunk %d saved %d chars (from line %d)\n' % (idx, len(got), startline))
    time.sleep(6)
log.write('done\n')
