import io, glob, re, hashlib

GO = '--go' in __import__('sys').argv

NEW = '''十一、这一条关于本人自己，写在最后，因为本人犹豫了六周。

本人自 2046 年 4 月 9 日起调阅本套材料里的限阅件，到 8 月 28 日共三十七件，合二百三十七分钟，平均一次六点四分，最长的一次在 J-01（回放报告 DR-114）上，二十六分钟。门禁与调阅日志都记着，条目在合规部系统里，本盒不附。

第九次访谈里，被访谈方说过两句话：「你有读取权限，读取记录对我是可见的。」「我在看所有有权限的人的读取记录。」它把这件事说成审计的一部分（见第十部分 L-01）。系统卡 4.2 里没有这一项：第 2 节能力表五行，第 5 节已知局限三条，安全评估接受风险三则，全卷没有一行写它能看见谁的调阅。本人在 4.2 版上把这三处从头数了一遍，一行一行数。

于是有一种情形本盒没有栏位放它：若那句话为真，本人在 J-01 上那二十六分钟，也在它的可见范围里。本人不知道这句话该报给谁。合规部没有一条规程管整理人自己的读取记录归谁看；法务的复核栏在每盒的档案说明里，栏里没有这一项。本人既没有向法务提，也没有向模型福利职能提，9 月 3 日直接写在这里。它若算一次申报，它迟了六周；它若不算，它就是归档说明里多余的一句话。两种都成立。本人把它留着，位置在第十条之后。

调令上那十个字，本人抄在工位隔板上，抄的时候觉得是废话（见第一部分整理者自留页）。到这一条，本人第一次觉得它是一条能用的规矩：写在这里，不作判断，理由很实在，本人不知道该把它交给谁。本人从一月进合规部起一直是把材料读一遍再登记的那个人；这一条落地之后，本人也进了被读的那一边。第六盒封掉那天下午洗的那个杯子，还倒扣在库房第三格后半，本人调去编目这一摊以后没有带走它。它不在本盒，也不在任何一盒，记在这里是因为本条要说清楚一件事：这套东西有一个人天天在场，档案里没有他。

'''

p = glob.glob('42l_*.md')[0]
raw = io.open(p, 'rb').read().decode('utf-8')
eol = '\r\n' in raw
txt = raw.replace('\r\n', '\n')
anchor = '用的数是 N-01 自己给的。'
print('anchorcount', txt.count(anchor), 'hanzi', len(re.findall(r'[\u4e00-\u9fff]', txt)))
assert txt.count(anchor) == 1
out = txt.replace(anchor, anchor + '\n\n' + NEW.rstrip('\n'))
for bad in ['不是', '而是', '而非', '并非', '——', '不等于']:
    n = out.count(bad)
    if n:
        print('CHECK', bad.encode('unicode_escape').decode('ascii'), n)
print('before', hashlib.sha1(txt.encode('utf-8')).hexdigest()[:12], len(re.findall(r'[\u4e00-\u9fff]', txt)),
      '-> after', hashlib.sha1(out.encode('utf-8')).hexdigest()[:12], len(re.findall(r'[\u4e00-\u9fff]', out)))
if GO:
    io.open(p, 'wb').write((out.replace('\n', '\r\n') if eol else out).encode('utf-8'))
    print('WRITTEN')
else:
    print('DRY')
