import io, os, re, sys, subprocess, time, glob, hashlib

CBC = r'C:\Users\hp\AppData\Roaming\npm\cbc.cmd'
TASK = ('你在校对一部中文长篇小说的一个切片。只做发现，不改写，不总结情节，不开处方。'
        '按四类报告，每条给「切片内行号｜照抄原句｜一句理由」：'
        'A 叙述声里替读者把意义说破的句子（心理宣告、价值判定、把比喻结算成道理）。'
        'B 同一人物在切片内第三次重复的同一小动作或同一句式。'
        'C 像是表格、字段、清单直接抄进叙述而没有被人用手碰过的段落。'
        'D 读起来像复制粘贴的整句重复（同卷他处可能也有，只管本切片）。'
        '某类没有就写 NONE。不要引用规则原文，不要给修改建议。')

def chunks(path, size):
    t = io.open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    lines = t.split('\n')
    out, cur, cnt, start = [], [], 0, 1
    for i, l in enumerate(lines, 1):
        cur.append(l)
        cnt += len(re.findall(r'[一-鿿]', l))
        if cnt >= size and (l.strip() == '' or l.startswith('##')):
            out.append((start, cur)); cur, cnt, start = [], 0, i + 1
    if cur:
        out.append((start, cur))
    return out

def main():
    vol, slug, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    model = sys.argv[4] if len(sys.argv) > 4 else 'fast-model'
    frm = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    to = int(sys.argv[6]) if len(sys.argv) > 6 else 999
    f = [x for x in glob.glob(vol + '_*.md') if '_正文' in x and 'backup' not in x][0]
    cs = chunks(f, size)
    os.makedirs('_cbd', exist_ok=True)
    log = io.open('_cbd_' + slug + '.log', 'w', encoding='utf-8')
    log.write('file %s hanzi %d chunks %d model %s\n' % (
        f, len(re.findall(r'[一-鿿]', io.open(f, 'rb').read().decode('utf-8'))), len(cs), model))
    log.flush()
    for n, (start, ls) in enumerate(cs, 1):
        if n < frm or n > to:
            continue
        body = '\n'.join('%d| %s' % (i, x) for i, x in enumerate(ls, start))
        prompt = TASK + '\n\n===== 切片 %d/%d（原文件行号已标在每行行首） =====\n' % (n, len(cs)) + body
        pf = '_cbd/_p_%s_%02d.txt' % (slug, n)
        io.open(pf, 'wb').write(prompt.encode('utf-8'))
        t0 = time.time()
        try:
            with io.open(pf, 'rb') as fin:
                r = subprocess.run([CBC, '-p', '--disallowedTools',
                                    'Write,Edit,MultiEdit,NotebookEdit,Bash,BashOutput,KillShell,Glob,Grep,Read,LS,Task,WebFetch,WebSearch',
                                    '--no-session-persistence', '--permission-mode', 'default',
                                    '--model', model], stdin=fin,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=420)
            out = r.stdout.decode('utf-8', errors='replace')
        except Exception as e:
            out = 'ERR ' + str(e)
        io.open('_cbd/%s_%02d.md' % (slug, n), 'w', encoding='utf-8').write(out)
        log.write('%02d lines=%d %.0fs sha=%s head=%s\n' % (
            n, len(ls), time.time() - t0, hashlib.sha256(out.encode('utf-8')).hexdigest()[:8],
            out.replace('\n', ' ')[:60]))
        log.flush()
        os.remove(pf)
    log.write('DONE\n'); log.flush(); log.close()

main()
