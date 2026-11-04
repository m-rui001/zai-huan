import io, glob, re, hashlib, sys
GO = '--go' in sys.argv

CHORUS = '''那道乘法我们都在心里算过：四十七，三十，一千四百一十。算完谁也没念出来。女声每小时来一次，同样的音量，同样的一行字；第三次上有人跟着念，念完自己笑，旁边的人也笑，笑声很短，通风机把它盖过去了。八十多个人靠着一米厚的水箱坐着，水在墙里循环，摸上去是温的，每个人的手都在墙上停过一下。我们知道外面在下什么，看不见它。墙上的数跳到四十七就停住了，它停住，把往下要过的三十个小时切成三十段，每一段开头都是那一句。有人把毯子蒙到头上。有人把一箱水推到两个人中间，推过去以后没有人喝。通风机一直响，响到我们听不见了。'''

p = glob.glob('44_*.md')[0]
raw = io.open(p, 'rb').read().decode('utf-8')
eol = '\r\n' in raw
t = raw.replace('\r\n', '\n')
anchor = '年终奖就没了。”\n\n没人接话。'
print('anchorcount', t.count(anchor))
assert t.count(anchor) == 1
out = t.replace(anchor, '年终奖就没了。”\n\n' + CHORUS + '\n\n没人接话。')
before_we = sum(1 for l in out.split('\n') if '我们' in l and '“' not in l and '「' not in l)
for bad in ['不是', '而是', '而非', '并非', '——', '不等于']:
    if bad in CHORUS:
        print('BAN HIT', bad.encode('unicode_escape').decode('ascii'))
print('chorus_hanzi', len(re.findall(r'[\u4e00-\u9fff]', CHORUS)))
print('before', hashlib.sha1(t.encode('utf-8')).hexdigest()[:12], len(re.findall(r'[\u4e00-\u9fff]', t)),
      '-> after', hashlib.sha1(out.encode('utf-8')).hexdigest()[:12], len(re.findall(r'[\u4e00-\u9fff]', out)),
      'unquoted_we_lines', before_we, 'eol', 'crlf' if eol else 'lf')
if GO:
    io.open(p, 'wb').write((out.replace('\n', '\r\n') if eol else out).encode('utf-8'))
    print('WRITTEN')
else:
    print('DRY')
