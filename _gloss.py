# -*- coding: utf-8 -*-
"""宣布句普查：叙述声里先说破心理／主题，后面往往已有兑现动作。
判据（人工定，脚本只出坐标）：叙述行含【说破词】且该句抽象（无实物名词）。
输出：file:line + 该行 + 后两非空行（供我判"兑现是否已在场"）。
"""
import io, re, sys, glob

HAN = re.compile(u'[一-鿿]')
FILES = {
    u'一': ['40_卷一_人类反馈_正文.md'], u'二': ['41_卷二_以斯拉书_正文.md'],
    u'三': sorted(glob.glob('42*.md')), u'四': ['43_卷四_冻存_正文.md'],
    u'五': ['44_卷五_剂量_正文.md'], u'六': ['67_卷六_十一秒_正文.md'],
    u'七': ['45_卷七_嗯_正文.md'], u'八': ['46_卷八_晨昏线_正文.md'],
    u'九': ['48_卷九_记录之外_正文.md'], u'十': ['50_卷十_针脚_正文.md'],
}
DOC = re.compile(u'^[ \t]*(#|\||`|>|\*\*|\u3010|-{3,})')
SPK = re.compile(u'^[^：」]{1,8}：')
# 说破词：心理状态的直陈
TELL = [u'说不清', u'说不出', u'不明白', u'知道自己在', u'其实', u'她想', u'他想', u'她知道',
        u'他知道', u'她明白', u'他明白', u'她需要', u'他需要', u'她开始', u'他开始',
        u'她学会', u'他学会', u'她第一次', u'他第一次', u'有点怕', u'她怕', u'他怕',
        u'不好意思', u'心虚', u'不甘', u'她难受', u'他难受', u'不习惯', u'她懂了', u'他懂了']
CONCRETE = re.compile(u'碗|桌|门|窗|纸|笔|杯|水|雨|雪|灯|车|椅|床|布|布|柜|盒|箱|绳|刀|锅|勺|'
                      u'鞋|衣|伞|药|钱|表|机|屏|键|墙|地|路|桥|河|田|树|果|鱼|肉|盐|油|火|烟|灰|'
                      u'土|石|井|灶|盆|桶|篮|袋|扣|链|钉|环|孔|缝|线|针|布|枕|被|毯|扇|钟|球|杯')


def scan(v):
    out = []
    for f in FILES[v]:
        t = io.open(f, encoding='utf-8', newline='').read().replace('\r\n', '\n')
        L = t.split('\n')
        for i, raw in enumerate(L):
            s = raw.strip()
            if not s or DOC.match(s) or SPK.match(s):
                continue
            if u'”' in s or u'「' in s or u'“' in s:
                continue   # 含台词的行交给台词声部
            for w in TELL:
                if w in s:
                    nxt = [x.strip() for x in L[i + 1:i + 6] if x.strip()][:2]
                    has_conc = bool(CONCRETE.search(s))
                    out.append((f[:2] + ':' + str(i + 1), w, has_conc, s[:56],
                                u' / '.join(x[:40] for x in nxt)))
                    break
    return out


targets = sys.argv[1:] or list(u'一二三四五六七八九十')
rows = []
for v in targets:
    r = scan(v)
    rows.append(u'=== 卷%s 候选 %d' % (v, len(r)))
    for x in r:
        rows.append(u'%s|%s|实:%s|%s||后:%s' % x)
io.open('_gloss_out.txt', 'w', encoding='utf-8', newline='\n').write(u'\n'.join(rows) + u'\n')
print('candidates', sum(1 for x in rows if x.startswith(u'4')) or len(rows))
