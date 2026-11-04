# -*- coding: utf-8 -*-
import io, re, subprocess, sys

FILES = ['40_卷一_人类反馈_正文.md', '41_卷二_以斯拉书_正文.md', '43_卷四_冻存_正文.md',
         '44_卷五_剂量_正文.md', '45_卷七_嗯_正文.md', '46_卷八_晨昏线_正文.md',
         '48_卷九_记录之外_正文.md', '50_卷十_针脚_正文.md', '67_卷六_十一秒_正文.md']
for f in FILES:
    out = subprocess.run([sys.executable, '_sent.py', f], capture_output=True).stdout.decode('utf-8', 'replace')
    def g(k):
        m = re.search(k + r'=([0-9.]+)', out)
        return m.group(1) if m else '?'
    print(f.split('_')[0], g('all>=60'), g('prose>=60'), g('adj<=3'), g('narr>=60'), sep='\t')
