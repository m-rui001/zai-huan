import re, io, statistics, sys

p = sys.argv[1]
t = io.open(p, encoding='utf-8').read()
ban = '——|仿佛|宛如|不禁|犹如|值得注意|换句话说|事实上|与此同时|更关键|说白了|本质上|这意味着|这说明|终极|完美|史诗|杰作|最锋利|觉醒|麻木|异化|所谓|与其说|关键在于|真正的是|这就叫|归根结底|某种意义上'
line = lambda m: t[:m.start()].count('\n') + 1
print('banned', [(m.group(0), line(m)) for m in re.finditer(ban, t)])
print('notis', [(m.group(0), line(m)) for m in re.finditer(r'不是.{1,14}，(是|而是|只是)', t)])
print('notis2', [(m.group(0), line(m)) for m in re.finditer(u'不是[^。”\\n]{1,16}。[^。”\\n]{1,20}是', t)])
print('locus', [(m.group(0), line(m)) for m in re.finditer(u'(问题|答案|原因|关键|分歧)[^。\\n]{0,6}(正|就|恰恰)在这里|[^。\\n]{0,10}(难处|麻烦|症结|要害|关键|吊诡)(之处|的地方)[，,]?(正|就|恰恰)', t)])
print('shell', [(m.group(0), line(m)) for m in re.finditer(u'并不(复杂|新鲜|意外|奇怪|难懂|高明|深奥|简单|轻松|容易)|多了去了|(省事|省力|省心|省去了|省掉)|(最)(残酷|要紧|要命|讽刺|为难)(的地方|之处)(在于|是)', t)])
print('objneg', [(m.group(0), line(m)) for m in re.finditer(u'(数据|血管|系统|模型|文件|机器|算法|制度|条款|屏幕|表格|秤|记录|规矩|条文|流程|清单|编号|指标|数字)[^。\\n]{0,3}(不认|不在乎|不懂|不看|不听|不问|不回答|不解释)', t)])
print('notis3', [(m.group(0), line(m)) for m in re.finditer(u'并非[^。]{0,12}而是|[^。]{0,10}而非[^。]{0,10}', t)])
_nq = re.sub(r'[“「][^”」]*[”」]', '', t)
_line2 = lambda m: _nq[:m.start()].count('\n') + 1
print('dashnarr', [(_line2(m), re.sub(r'[\r\n]', ' ', _nq[max(0, m.start()-16):m.start()+16])) for m in re.finditer('——', _nq)])
print('trad', sorted(set(re.findall(r'[個這時說會來與後裡麼樣內]', t))))
print('curly', len(re.findall(r'[「」“”]', t)))
print('xiangqi', [(m.group(0), line(m)) for m in re.finditer(r'想起', t)])
print('fenceglue', len(re.findall(r'```[^\n]', t)))
h = len(re.findall(r'[\u4e00-\u9fff]', t))
secs = re.split(r'(?m)^## ', t)[1:]
lens = [len(re.findall(r'[\u4e00-\u9fff]', x)) for x in secs] or [h]
body = re.sub(r'(?m)^#.*$', '', t)
sents = [s for s in re.split(r'(?<=[。！？])', body) if re.search(r'[\u4e00-\u9fff]', s)]
sl = [len(re.findall(r'[\u4e00-\u9fff]', s)) for s in sents]
dlg = sum(len(re.findall(r'[\u4e00-\u9fff]', m)) for m in re.findall(r'\"[^\"]*\"|“[^”]*”', t))
brk = sum(len(re.findall(r'[\u4e00-\u9fff]', m)) for m in re.findall(r'「[^」]*」', t))
d = len(re.findall(r'[0-9]', t))
print('hanzi', h, 'secs', len(secs), 'median', statistics.median(lens), 'max', max(lens))
print('sent avg', round(sum(sl) / len(sl), 1), '<=20', round(sum(1 for x in sl if x <= 20) / len(sl) * 100, 1), '>=80', sum(1 for x in sl if x >= 80))
print('dialogue', round(dlg / h * 100, 1), 'bracket', round(brk / h * 100, 1), 'digits', d, 'perwan', round(d / h * 10000))
