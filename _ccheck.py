# -*- coding: utf-8 -*-
# 账本引文核对：抽 「…」 跨度，剥标记后在全部正文里找子串；找不到 = 待查
import io,re,sys,glob
BODY=sorted([f for f in (glob.glob('40_*.md')+glob.glob('41_*.md')+glob.glob('42*.md')
            +glob.glob('43_*.md')+glob.glob('44_*.md')+glob.glob('45_*.md')+glob.glob('46_*.md')
            +glob.glob('48_*.md')+glob.glob('50_*.md')+glob.glob('67_*.md'))
            if 'backup' not in f and '_分章表' not in f])
strip=lambda s: re.sub(u'[“”「」『』＂‘’*’\u3010\u3011]','',s)
C=''.join(strip(io.open(f,encoding='utf-8',newline='').read()).replace('\n','') for f in BODY)
f=sys.argv[1]; start=sys.argv[2] if len(sys.argv)>2 else ''
t=io.open(f,encoding='utf-8',newline='').read()
if start: t=t[t.index(start):]
qs=re.findall(u'\u300c([^\u300d]{4,})\u300d',t)
seen=set(); miss=[]
for q in qs:
    s=strip(q).replace('\n','').replace(' ','').replace(u'\u3000','')
    if s in seen: continue
    seen.add(s)
    if s not in C.replace(' ',''): miss.append(q)
print('files=%d spans=%d unique=%d notfound=%d'%(len(BODY),len(qs),len(seen),len(miss)))
for m in miss: print(' MISS>',m[:70].replace('\n','|'))
