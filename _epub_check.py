# -*- coding: utf-8 -*-
"""Validate 在环_十卷.epub: container / opf / spine / nav / ncx, XML 良构,
锚点, markdown 残留, 以及每卷逐段落稿核对。"""
import io, os, re, zipfile, html
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
EP = os.path.join(ROOT, '在环_十卷.epub')
HZ = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
problems, notes, lines = [], [], []

z = zipfile.ZipFile(EP)
names = z.namelist()

if names[0] != 'mimetype' or z.read('mimetype') != b'application/epub+zip':
    problems.append('mimetype 不在首位或内容不对')
if z.getinfo('mimetype').compress_type != zipfile.ZIP_STORED:
    problems.append('mimetype 被压缩')

XHTML = [n for n in names if n.endswith('.xhtml')]
for n in names:
    if n.endswith(('.xml', '.opf', '.ncx', '.xhtml')):
        try:
            ET.fromstring(z.read(n))
        except Exception as e:
            problems.append('XML 非良构: %s -> %s' % (n, e))

C = '{urn:oasis:names:tc:opendocument:xmlns:container}'
cont = ET.fromstring(z.read('META-INF/container.xml'))
opf_path = cont.find(C + 'rootfiles').find(C + 'rootfile').get('full-path')
if opf_path not in names:
    problems.append('rootfile 缺失: %s' % opf_path)

opf = ET.fromstring(z.read(opf_path))
P = '{http://www.idpf.org/2007/opf}'
D = '{http://purl.org/dc/elements/1.1/}'
meta = opf.find(P + 'metadata')
for req in ('identifier', 'title', 'language'):
    if meta.find(D + req) is None:
        problems.append('缺 dc:' + req)
if not [m for m in meta.findall(P + 'meta') if m.get('property') == 'dcterms:modified']:
    problems.append('缺 dcterms:modified')

items = {}
for i in opf.find(P + 'manifest').findall(P + 'item'):
    if i.get('id') in items:
        problems.append('manifest id 重复: %s' % i.get('id'))
    items[i.get('id')] = (i.get('href'), i.get('media-type'))
base = os.path.dirname(opf_path)
for k, (href, mt) in items.items():
    full = (base + '/' + href).replace('\\', '/')
    if full not in names:
        problems.append('manifest 指向的文件不在包里: %s' % href)
    elif href.endswith('.xhtml') and mt != 'application/xhtml+xml':
        problems.append('media-type 不对: %s' % href)

refs = [r.get('idref') for r in opf.find(P + 'spine').findall(P + 'itemref')]
for r in refs:
    if r not in items:
        problems.append('spine 引用了不存在的 id: %s' % r)
in_spine = set((base + '/' + items[r][0]).replace('\\', '/') for r in refs if r in items)
for i, (href, mt) in items.items():
    full = (base + '/' + href).replace('\\', '/')
    if href.endswith('.xhtml') and full not in in_spine:
        problems.append('xhtml 未进 spine: %s' % href)
notes.append('spine %d 项，xhtml %d 个' % (len(refs), len(XHTML)))

for n in XHTML:
    raw = z.read(n).decode('utf-8')
    for a, b in (('<em>', '</em>'), ('<strong>', '</strong>'), ('<table>', '</table>'),
                 ('<tr>', '</tr>'), ('<td[ >]', '</td>'), ('<th[ >]', '</th>'), ('<blockquote>', '</blockquote>')):
        if len(re.findall(a, raw)) != len(re.findall(b, raw)):
            problems.append('%s/%s 不配对: %s' % (a, b, n))
    if len(re.findall(r'<p[ >]', raw)) != raw.count('</p>'):
        problems.append('<p> 不配对: %s' % n)
    ids = re.findall(r'id="([^"]+)"', raw)
    dup = [k for k, c in Counter(ids).items() if c > 1]
    if dup:
        problems.append('id 重复 %s in %s' % (dup[:3], n))
    stripped = re.sub(r'(?s)<[^>]+>', '', raw)
    for tok in ('**', '```', '##'):
        if tok in stripped:
            problems.append('残留 markdown 符号 %s in %s' % (tok, n))
    if re.search(r'(?m)^\s*\|', stripped):
        problems.append('残留表格竖线 in %s' % n)

def resolve(href):
    f, _, a = href.partition('#')
    f = f.replace('\\', '/')
    full = f if f.startswith('OEBPS') else 'OEBPS/' + f
    if full not in names:
        return '文件断链 ' + href
    if a and ('id="%s"' % a) not in z.read(full).decode('utf-8'):
        return '锚点断链 ' + href
    return None

nav_raw = z.read('OEBPS/nav.xhtml').decode('utf-8')
for href in re.findall(r'href="([^"]+)"', nav_raw):
    r = resolve(href)
    if r:
        problems.append('nav: ' + r)
ncx_name = [n for n in names if n.endswith('toc.ncx')][0]
ncx_raw = z.read(ncx_name).decode('utf-8')
for href in re.findall(r'src="([^"]+)"', ncx_raw):
    r = resolve(href)
    if r:
        problems.append('ncx: ' + r)
notes.append('nav 链接 %d，ncx 链接 %d' % (
    len(re.findall(r'href="', nav_raw)), len(re.findall(r'src="', ncx_raw))))

VOL3 = ['42_卷三_退役访谈_档案卷一.md'] + [
    '42%s_卷三_退役访谈_档案卷%s.md' % (c, n) for c, n in zip(
        'bcdefghijklm', '二 三 四 五 六 七 八 九 十 十一 十二 十三'.split())] + ['42n_卷三_未归档.md']
VOLS = [('卷一', ['40_卷一_人类反馈_正文.md']), ('卷二', ['41_卷二_以斯拉书_正文.md']),
        ('卷三', VOL3), ('卷四', ['43_卷四_冻存_正文.md']), ('卷五', ['44_卷五_剂量_正文.md']),
        ('卷六', ['67_卷六_十一秒_正文.md']), ('卷七', ['45_卷七_嗯_正文.md']),
        ('卷八', ['46_卷八_晨昏线_正文.md']), ('卷九', ['48_卷九_记录之外_正文.md']),
        ('卷十', ['50_卷十_针脚_正文.md'])]

for vi, (vt, files) in enumerate(VOLS, 1):
    hay, numparts = '', 0
    for pi in range(1, 60):
        fn = 'OEBPS/v%02d_%d.xhtml' % (vi, pi)
        if fn not in names:
            continue
        numparts += 1
        b = re.sub(r'(?s)^.*?<main>', '', z.read(fn).decode('utf-8'))
        hay += re.sub(r'(?s)<[^>]+>', '', b)
    hayc = re.sub(r'\s+', '', html.unescape(hay))
    miss = srcp = 0
    for f in files:
        tt = io.open(os.path.join(ROOT, f), 'rb').read().decode('utf-8').replace('\r\n', '\n')
        for ln in tt.split('\n'):
            s = ln.strip()
            if not s:
                continue
            core = re.sub(r'(?m)^#{1,6}\s+|^>+\s?|^[-*]\s+|^\d+[.)]\s+|`', '', s)
            core = re.sub(r'\*\*(.+?)\*\*', r'\1', core)
            core = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'\1', core)
            if re.match(r'^\|?[\s:|-]+\|?$', core):
                continue
            if s.startswith('|'):
                core = core.replace('|', '')
            core = re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', core)))
            if not HZ.search(core):
                continue
            if s.startswith('# ') and s[2:].strip().startswith(vt):
                continue          # 卷首行被有意收短为档案卷号，见 build
            srcp += 1
            if core not in hayc:
                miss += 1
                if miss <= 3:
                    lines.append('  MISS %s: %s' % (f[:18], core[:44]))
    sh = sum(len(HZ.findall(io.open(os.path.join(ROOT, f), 'rb').read().decode('utf-8'))) for f in files)
    gh = len(HZ.findall(hay))
    lines.append('%-4s 分片=%d 源=%6d epub=%6d 差=%+5d 段落=%5d 未命中=%d' % (
        vt, numparts, sh, gh, gh - sh, srcp, miss))
    if miss:
        problems.append('%s 有 %d 段未落入 epub' % (vt, miss))

io.open(os.path.join(ROOT, '_epub_report.txt'), 'w', encoding='utf-8').write(
    '；'.join(notes) + '\n\n' + '\n'.join(lines) + '\n\n问题（%d）：\n%s\n' % (
        len(problems), '\n'.join(problems) if problems else '无'))
print('problems=%d' % len(problems))
