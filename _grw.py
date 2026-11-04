# -*- coding: utf-8 -*-
# grok 变体生成器：取一段正文，让远端只改说话方式，事件/数字/物件/人物一律不动
import json, os, re, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
prov = os.environ.get('GRPROV', 'cssm-fun')
CFG = json.load(open(os.path.join(HERE, '_keys.json'), encoding='utf-8'))[prov]
BASE, KEY = CFG['baseUrl'], CFG['apiKey']
H = {"Authorization": "Bearer " + KEY, "User-Agent": "opencode/1.1.4",
     "Content-Type": "application/json", "Accept": "application/json"}

vol = sys.argv[1]
slug = sys.argv[2]
lo = int(sys.argv[3])
hi = int(sys.argv[4])
models = (sys.argv[5] if len(sys.argv) > 5 else 'grok-4.3').split(',')
maxtok = int(sys.argv[6]) if len(sys.argv) > 6 else 1500

cands = sorted(f for f in os.listdir(HERE) if f.startswith(vol + '_') and f.endswith('.md') and 'backup' not in f)
body = [f for f in cands if '_正文' in f]
src = (body or cands)[0]
lines = open(os.path.join(HERE, src), encoding='utf-8').read().split('\n')
seg = '\n'.join('%d| %s' % (i + 1, lines[i]) for i in range(lo - 1, min(hi, len(lines))))

PROMPT = u"""下面是一部中文长篇小说里的一段，每行行首是原文件的行号。

你的活：把这段里的对白重写一遍，让每个人物的说话方式更像他自己的身份、年龄、地方和当下的心情。

硬规矩：
- 只改说话的方式和说话前后的动作描写。人物、事件、时间、日期、数字、金额、器物名、地名、条款号，一个都不许改。
- 不许新增情节，不许删掉原有的信息，不许让人物说出他还不知道的事。
- 保持原来的行结构：输出每一行都以原行号加竖线开头，行号后跟这一行重写后的正文，一行对应一行，不合并、不拆分、不增行、不减行。
- 不用「不是……而是……」「……，不是……」这一类先否定再肯定的句式。
- 不要比喻堆砌，不要形容词连用，不要总结，不要解释你做了什么，不要寒暄，不复述本提示。
- 除重写稿以外不输出任何文字。

原文：
""" + seg

out_dir = os.path.join(HERE, '_gw')
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
log = open(os.path.join(HERE, '_gw_%s.log' % slug), 'w', encoding='utf-8', buffering=1)
log.write('src %s lines %d-%d models %s\n' % (src, lo, hi, models))
for model in models:
    op = os.path.join(out_dir, '%s_%s.txt' % (slug, model.replace('/', '_')))
    req = urllib.request.Request(BASE.rstrip('/') + '/chat/completions',
                                 data=json.dumps({"model": model.strip(), "messages": [
                                     {"role": "user", "content": PROMPT}],
                                     "temperature": 0.75, "max_tokens": maxtok,
                                     "stream": False}).encode('utf-8'), headers=H)
    got = None
    for try_i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=420) as r:
                j = json.loads(r.read().decode('utf-8', 'replace'))
            got = ((j.get('choices') or [{}])[0].get('message') or {}).get('content') or ''
            if got.strip():
                break
            got = None
        except urllib.error.HTTPError as e:
            log.write('%s try %d HTTP %s %s\n' % (model, try_i, e.code,
                                                  e.read().decode('utf-8', 'replace')[:120]))
        except Exception as e:
            log.write('%s try %d ERR %r\n' % (model, try_i, repr(e)[:150]))
    if not got:
        log.write('%s FAILED\n' % model)
        continue
    open(op, 'w', encoding='utf-8').write(got)
    log.write('%s saved %d chars -> %s\n' % (model, len(got), os.path.basename(op)))
log.write('done\n')
print('ok')
