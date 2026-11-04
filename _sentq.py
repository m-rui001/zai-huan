# -*- coding: utf-8 -*-
"""句子级缺陷普查：输出坐标＋原文，不自动判定。
缺陷类：
 A 碎句串（连续 >=4 句，每句 <=6 汉字，叙述声，非表格非台词）
 B 说明腔开头（解释性连接词进入叙述）
 C 抽象名词入叙述（替身体替实物说话）
 D 方程式警句（「X 是 Y」且两侧都抽象）
 E 比喻标记密度（像/如同/仿佛/犹如/般，只报数供人工读）
用法：python _sentq.py [卷号...]   不带参数＝全卷
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
DOC = re.compile(u'^[ \\t]*(#|\\||`|>|\\*\\*|\\u3010|\\*|-{3,})')
SPK = re.compile(u'^[^：」]{1,8}：')
B_WORDS = [u'这说明', u'这意味着', u'值得注意', u'事实上', u'换句话说', u'可以说', u'显然',
           u'无疑', u'不难看出', u'某种意义上', u'其实', u'毕竟', u'归根结底', u'本质上',
           u'也就是说', u'要知道']
C_WORDS = [u'尊严', u'孤独', u'命运', u'意义', u'价值', u'温暖', u'冰冷', u'残忍', u'温柔',
           u'绝望', u'希望', u'自由', u'幸福感', u'存在感', u'成就感', u'失落', u'悲哀',
           u'悲凉', u'苍凉', u'荒诞', u'异化', u'麻木', u'觉醒', u'沉重', u'酸楚']
E_WORDS = [u'像', u'如同', u'仿佛', u'犹如', u'般', u'似的']
ABSTRACT = set(u'制度系统权力结构规则秩序意义价值时间记忆历史情感关系身份自我他者身体语言声音')


def sentences(line):
    body = re.sub(u'[“”「」]', '', line)
    return [s for s in re.split(u'(?<=[。！？])', body) if HAN.search(s)]


def is_abstract_word(w):
    return all(c in ABSTRACT or not HAN.search(c) for c in w) and len(w) >= 2


def clause_pairs(sent):
    """X 是 Y 方程句：两侧均为 >=2 字且至少一侧全抽象"""
    for m in re.finditer(u'([^，。]{2,10})是([^，。]{2,10})[。！？]', sent):
        a, b = m.group(1), m.group(2)
        if not re.search(u'[一二三四五六七八九十百千万][一二三四五六七八九十百千万]?$', a):
            pass
        return a, b
    return None


def scan(vol):
    fs = FILES[vol]
    hits = {'A': [], 'B': [], 'C': [], 'D': []}
    ecount = 0
    for f in fs:
        lines = io.open(f, encoding='utf-8', newline='').read().replace('\r\n', '\n').split('\n')
        run = []
        for i, raw in enumerate(lines, 1):
            s = raw.strip()
            in_f = False
            if s.startswith('```'):
                pass
            if not s or DOC.match(s) or SPK.match(s):
                if s and not DOC.match(s):
                    pass
                run = []
                continue
            if u'：' in s and re.match(u'^[\u4e00-\u9fff]{1,3}：', s):
                run = []
                continue
            hs = sentences(s)
            # A: run of tiny sentences inside one line
            tiny = [h for h in hs if len(HAN.findall(h)) <= 6]
            if len(hs) >= 4 and len(tiny) == len(hs):
                hits['A'].append((f[:2], i, s[:70]))
                run = []
            else:
                run.append((i, s))
            for w in B_WORDS:
                if w in s:
                    hits['B'].append((f[:2], i, w, s[:70]))
            for w in C_WORDS:
                if w in s:
                    hits['C'].append((f[:2], i, w, s[:66]))
            for w in E_WORDS:
                ecount += s.count(w)
            for h in hs:
                cp = clause_pairs(h)
                if cp and is_abstract_word(cp[0]) and is_abstract_word(cp[1]):
                    hits['D'].append((f[:2], i, h[:56]))
    return hits, ecount


targets = sys.argv[1:] or list(u'一二三四五六七八九十')
out = []
for v in targets:
    hits, e = scan(v)
    out.append(u'=== 卷%s  A碎串 %d｜B说明腔 %d｜C抽象词 %d｜D方程句 %d｜E比喻词 %d' %
               (v, len(hits['A']), len(hits['B']), len(hits['C']), len(hits['D']), e))
    for k in 'ABCD':
        for rec in hits[k][:6]:
            out.append(u'  %s %s' % (k, rec))
    if len(hits['C']) > 6:
        out.append(u'  C 另有 %d 条' % (len(hits['C']) - 6))
io.open('_sentq_out.txt', 'w', encoding='utf-8', newline='\n').write(u'\n'.join(out) + u'\n')
print(u'\n'.join(out)[:120].encode('utf-8').decode('utf-8'))
print('written _sentq_out.txt lines', len(out))
