# -*- coding: utf-8 -*-
"""规矩一尺（权威版）：十卷 60-120 / >120 长句数，逐卷打印 files= 供核。
   用法：python _bands.py            ->  写 _bands.txt（UTF-8），stdout 只报 ASCII
   口径：句子级切分（。？！…）；剔代码围栏、# | > - 开头行、四空格缩进行；台词行照收。
   教训：卷三必须用 ^42[a-z]?_.*\\.md$ ——不加 .md 过滤会把过期底稿算进来（曾把 16 句算成 31 句）。"""
import io, re, os

HAN = re.compile(r'[一-鿿]')
VOLS = [
    ('卷一', ['40_卷一_人类反馈_正文.md']),
    ('卷二', ['41_卷二_以斯拉书_正文.md']),
    ('卷三', sorted(f for f in os.listdir('.') if re.match(r'^42[a-z]?_.*\.md$', f))),
    ('卷四', ['43_卷四_冻存_正文.md']),
    ('卷五', ['44_卷五_剂量_正文.md']),
    ('卷六', ['67_卷六_十一秒_正文.md']),
    ('卷七', ['45_卷七_嗯_正文.md']),
    ('卷八', ['46_卷八_晨昏线_正文.md']),
    ('卷九', ['48_卷九_记录之外_正文.md']),
    ('卷十', ['50_卷十_针脚_正文.md']),
]
out = io.open('_bands.txt', 'w', encoding='utf-8')
tb = to = 0
for name, files in VOLS:
    b60 = b120 = 0
    rows = []
    for f in files:
        L = io.open(f, encoding='utf-8').read().split('\n')
        fence = False
        for i, l in enumerate(L):
            s = l.strip()
            if s.startswith('```'):
                fence = not fence; continue
            if fence or not s or s[0] in '#|>-' or l.startswith('    '):
                continue
            for sent in re.split(r'(?<=[。？！…])', s):
                n = len(HAN.findall(sent))
                if 60 <= n <= 120:
                    b60 += 1
                    rows.append('60-120 L%d (%d) %s' % (i + 1, n, sent[:120]))
                elif n > 120:
                    b120 += 1
                    rows.append('>120  %s L%d (%d) %s' % (f[:10], i + 1, n, sent[:120]))
    out.write('##### %s files=%d 60-120:%d >120:%d\n' % (name, len(files), b60, b120))
    for r in rows:
        out.write('  ' + r + '\n')
    tb += b60; to += b120
out.write('=== 全书 60-120:%d >120:%d\n' % (tb, to))
out.close()
print('volumes', len(VOLS), 'band60_120', tb, 'over120', to)
