import io, glob
f=[x for x in glob.glob('40_*.md') if '_正文' in x and 'backup' not in x][0]
L=io.open(f,'rb').read().decode('utf-8').replace('\r\n','\n').split('\n')
o=['file %s lines %d' % (f,len(L))]
for pat in ['分到哪类','哪类','重复','去重','罗永红','其他']:
    hs=[(i,l) for i,l in enumerate(L,1) if pat in l]
    o.append('== %s :: %d' % (pat,len(hs)))
    for i,l in hs[:16]:
        o.append('  %d| %s' % (i,l[:120]))
io.open('_tmp_zg1.txt','w',encoding='utf-8').write('\n'.join(o)); print('ok')
