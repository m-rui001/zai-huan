import io, glob
def esc(s): return s.encode('unicode_escape').decode('ascii')
p = glob.glob('44_*.md')[0]
t = io.open(p, 'rb').read().decode('utf-8').replace('\r\n', '\n')
L = t.split('\n')
qs = [
 '她把这三个数写在纸上，画三个勾，一个比一个小。第二天她看那张纸，字是昨天的字。她照原样再画三个勾，一样大。',
 '锅里的味道跟上一回不一样。上一回，雷坐在对面。这一回，公共间没有人。',
 '她用手指擦了一下，灰挪了个位置。',
 '你修的那个柜子，里面装的就是这个。你们叫客户资产。',
 '柜子旁边的墙上贴着一排温度打印纸，一天一张，贴了两米长。',
 '那个柜子旁边她跪了一年多，换阀门，换垫片，听米拉背单词。她从来没问过里面是什么。',
 '第二天他照常出舱，三个小时，回来交了工单。',
 '安妮站起来。她打了她一巴掌。',
 '安妮把纸拿起来，看了一会儿，放回原处，压在米拉的物理课本下面。',
 '差出来的七十，在苏妮塔名下是零，在她腰上是真的。',
 '她看着它，觉得这半片指甲比她的工牌更像她。',
 '她坐上去，数比上个月少六公斤。',
 '有人跟着念，念得一模一样，念完自己笑。旁边的人也笑。',
 '有人带了毯子，有人带了牌，有人带了一箱水。',
 '这话在谁那里起的头，没有人说得清。',
 '后面她想再写一句，写了两个字，删掉。发出去的那一行只剩下那个数。',
 '她盛饭，坐下吃，吃完洗碗。两个人都没提。',
 '她洗得很慢，冲，擦，冲，擦。四分钟。水停了，她把杯子倒扣在架子上。',
]
for q in qs:
    idx = [i + 1 for i, l in enumerate(L) if q in l]
    print(len(idx), idx[:3], esc(q[:16]))
print('nWe', sum(1 for l in L if '我们' in l), 'lines', len(L))
# count narrative-plural chorus candidates: lines starting a paragraph with 我们 and no quote marks
c = 0
for i, l in enumerate(L, 1):
    if '我们' in l and '“' not in l and '「' not in l and '**' not in l:
        c += 1
        if c <= 8:
            print('unquoted-we L%d' % i, esc(l[:70]))
print('unquoted_we_total', c)
