# -*- coding: utf-8 -*-
import re, io, glob
VOLS=[('一', '40_卷一_人类反馈_正文.md', 58367, 40, 9.3, 91.5, 24.5, 1311, 225),
('二', '41_卷二_以斯拉书_正文.md', 28005, 9, 13.6, 84.5, 3.3, None, 574),
('三', None, 64012, 108, 16.8, 73.5, None, None, 1354),
('四', '43_卷四_冻存_正文.md', 62397, 20, 12.0, 84.6, 23.6, 785, 126),
('五', '44_卷五_剂量_正文.md', 48408, 29, 9.5, 91.5, 29.1, 365, 75),
('六', '67_卷六_十一秒_正文.md', 26446, 10, 13.3, 79.9, None, None, 470),
('七', '45_卷七_嗯_正文.md', 60069, 2, 11.7, 88.8, None, None, 3103),
('八', '46_卷八_晨昏线_正文.md', 230389, 51, 12.3, 84.9, 21.7, None, 102),
('九', '48_卷九_记录之外_正文.md', 204915, 28, 9.5, 94.9, 2.4, 446, 22),
('十', '50_卷十_针脚_正文.md', 161416, 23, 7.7, 96.0, None, 544, 34)]
BAN='——|仿佛|宛如|不禁|犹如|值得注意|换句话说|事实上|与此同时|更关键|说白了|本质上|这意味着|这说明|终极|完美|史诗|杰作|最锋利|觉醒|麻木|异化'
o=io.StringIO(); bad=0
def ln(t,m): return t[:m.start()].count('\n')+1
for v,f,h0,s0,avg0,l20_0,dlg0,d0,pw0 in VOLS:
    t = ''.join(open(x,encoding='utf-8').read() for x in sorted(glob.glob('42*.md'))) if v=='三' else open(f,encoding='utf-8').read()
    h=len(re.findall(u'[\u4e00-\u9fff]',t))
    body=re.sub(r'(?m)^#.*$','',t)
    sents=[s for s in re.split(u'(?<=[。！？])',body) if re.search(u'[\u4e00-\u9fff]',s)]
    sl=[len(re.findall(u'[\u4e00-\u9fff]',s)) for s in sents]
    avg=round(sum(sl)/float(len(sl)),1)
    l20=round(sum(1 for x in sl if x<=20)/float(len(sl))*100,1)
    dlg=round(sum(len(re.findall(u'[\u4e00-\u9fff]',m)) for m in re.findall(u'"[^"]*"|\u201c[^\u201d]*\u201d',t))/float(h)*100,1)
    brk=round(sum(len(re.findall(u'[\u4e00-\u9fff]',m)) for m in re.findall(u'\u300c[^\u300d]*\u300d',t))/float(h)*100,1)
    d=len(re.findall(r'[0-9]',t)); pw=int(round(d/float(h)*10000))
    secs=max(s0,len(re.split(r'(?m)^## ',t))-1) if s0 else len(re.split(r'(?m)^## ',t))-1
    msg=[]
    if h!=h0: msg.append('hanzi %d!=%d'%(h,h0))
    if abs(avg-avg0)>0.05: msg.append('avg %s!=%s'%(avg,avg0))
    if abs(l20-l20_0)>0.05: msg.append('l20 %s!=%s'%(l20,l20_0))
    if d0 is not None and d!=d0: msg.append('digits %d!=%d'%(d,d0))
    if pw0 is not None and pw!=pw0: msg.append('perwan %d!=%d'%(pw,pw0))
    if dlg0 is not None and abs(dlg-dlg0)>0.15: msg.append('dialogue %s!=%s'%(dlg,dlg0))
    ban=[(m.group(0),ln(t,m)) for m in re.finditer(BAN,t)]
    notis=[(m.group(0),ln(t,m)) for m in re.finditer(u'不是.{1,14}，是',t)]
    trad=sorted(set(re.findall(u'[\u500b\u9019\u6642\u8aaa\u6703\u4f86\u8207\u5f8c\u88e1\u9ebc\u6a23\u5167]',t)))
    fg=len(re.findall(r'```[^\n]',t))
    o.write(u'卷%s hanzi %d secs %d avg %s l20 %s dlg %s brk %s digits %d pw %d\n'%(v,h,secs,avg,l20,dlg,brk,d,pw))
    o.write(u'  ban %s\n  notis %s\n  trad %s fence %d\n'%(ban,notis,trad,fg))
    if fg or trad: bad+=1
    for m in msg: o.write(u'  MISMATCH '+m+u'\n'); bad+=1
o.write(u'TOTAL table %d computed %d\n'%(sum(x[2] for x in VOLS),944424))
if sum(x[2] for x in VOLS)!=944424: bad+=1; o.write(u'  MISMATCH total %d!=944424\n'%sum(x[2] for x in VOLS))
o.write(u'PROBLEMS %d\n'%bad)
open('_verify_report.txt','w',encoding='utf-8').write(o.getvalue())
print('done',bad)
