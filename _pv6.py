import glob, io, re, sys, hashlib

GO = '--go' in sys.argv
f = [x for x in glob.glob('67_*.md') if '_正文' in x][0]
raw = io.open(f, encoding='utf-8', newline='').read()
t = raw.replace('\r\n', '\n')

NEW = (u'包里掏钥匙的时候，他把那只杯子摸出来，拧开，打算把剩下的茶倒掉再洗。倒出来的是速溶咖啡，凉的，'
       u'杯底一层粉渣没有化开。他的杯子不装这个。他低头看杯盖，里圈是干净的，他自己那一圈茶垢去年就刮不掉。'
       u'他把杯子放进水池冲了一遍，第二遍打了洗洁精，冲完搁在灶台左边，自己那只还在厂里那个大厅的桌角，明天还在。'
       u'第二天他把两只并排放在桌角，一只是他的，一只他不认得。谁也没有问。第三天那只不在了，他也不晓得它去了哪里。'
       u'厂里这种杯子是一箱一箱买的，谁拿走哪一只都看不出来。')

old = u'六点一十，奥克萨娜把亨里克扶到沙发上'
new = NEW + u'\n\n' + old
c = t.count(old)
print('file', f, 'sha8', hashlib.sha1(raw.encode('utf-8')).hexdigest()[:8], 'crlf', '\r\n' in raw, 'anchor', c, 'new_hanzi', len(re.findall(u'[一-鿿]', NEW)))
if c == 1 and GO:
    w = t.replace(old, new)
    if '\r\n' in raw:
        w = w.replace('\n', '\r\n')
    io.open(f, 'w', encoding='utf-8', newline='').write(w)
    a = io.open(f, encoding='utf-8', newline='').read()
    print('WRITTEN sha8', hashlib.sha1(a.encode('utf-8')).hexdigest()[:8], 'hanzi', len(re.findall(u'[一-鿿]', a)))
