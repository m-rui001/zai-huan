# -*- coding: utf-8 -*-
# 两把尺并存：段级（整行 60-120 汉字）与句级（单句 >=80 汉字，剔除文书行/注/对白前缀）
import io,re,glob
HAN=re.compile(u'[\u4e00-\u9fff]')
F={u'一':['40_卷一_人类反馈_正文.md'],u'二':['41_卷二_以斯拉书_正文.md'],
 u'三':sorted(glob.glob('42*.md')),u'四':['43_卷四_冻存_正文.md'],u'五':['44_卷五_剂量_正文.md'],
 u'六':['67_卷六_十一秒_正文.md'],u'七':['45_卷七_嗯_正文.md'],u'八':['46_卷八_晨昏线_正文.md'],
 u'九':['48_卷九_记录之外_正文.md'],u'十':['50_卷十_针脚_正文.md']}
DOC=re.compile(u'^[ \t]*(#|\||`|>|\*\*|\u3010|\*)')
SPK=re.compile(u'^[^：」]{1,8}：')
print(u'volume | files | duan60-120 | ju>=80 | longest narrative sentence (line:hanzi)')
for k in u'一二三四五六七八九十':
    fs=F[k]; p60=s80=0; best=('',0,'')
    for f in fs:
        for i,L in enumerate(io.open(f,encoding='utf-8',newline='').read().split('\n')):
            s=L.strip()
            if not s or DOC.match(s): continue
            h=len(HAN.findall(s))
            if 60<=h<=120: p60+=1
            if SPK.match(s): continue
            body=re.sub(u'[“”「」]','',s)
            for seg in re.split(u'(?<=[。！？])',body):
                hh=len(HAN.findall(seg))
                if hh>=80: s80+=1
                if hh>best[1]: best=(f[:2]+':'+str(i+1),hh,seg[:20])
    print(u'%s | files=%d | %4d | %3d | %s %s %s'%(k,len(fs),p60,s80,best[0],best[1],best[2]))
