import io,re,glob
BAN=[('A',r'不是[^。”\n]{1,14}。[^。”\n]{1,18}是'),('B',r'，不是'),('C',r'并非[^。”\n]{0,18}而是'),('D',r'而非')]
out=io.open(r'E:\Novel2\_tmp_allban.txt','w',encoding='utf-8')
tot={}
for f in sorted(glob.glob('E:/Novel2/4*.md')+glob.glob('E:/Novel2/5*.md')+glob.glob('E:/Novel2/6*.md')):
    if '_snap' in f or '\\_' in f: continue
    lines=open(f,encoding='utf-8').read().replace('\r\n','\n').split('\n')
    n=0
    for i,L in enumerate(lines):
        for k,p in BAN:
            for m in re.finditer(p,L):
                n+=1
                if ('「' in L) or ('”' in L) or ('"' in L) or ('**' in L): continue
                out.write('CAND %s|%s|%d|%s\n' % (f.split('\\')[-1],k,i+1,L[max(0,m.start()-16):m.end()+12]))
    tot[f.split('\\')[-1]]=n
out.write('---- counts\n')
for k,v in sorted(tot.items()): out.write('%s %d\n' % (k,v))
out.close(); print('ok')
