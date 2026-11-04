# -*- coding: utf-8 -*-
"""在环 十卷 → EPUB3 (+NCX). Coverage-checked by _epub_check.py."""
import io, os, re, zipfile, html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '在环_十卷.epub')
BUILD = os.path.join(ROOT, '_epub_build')
UUID = 'f2b7c3d1-8a4e-4b21-9c6f-10d2e5a7b904'
MODIFIED = '2026-11-04T07:10:00Z'
SPLIT = 52000
HZ = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')

VOL3 = ['42_卷三_退役访谈_档案卷一.md'] + [
    '42%s_卷三_退役访谈_档案卷%s.md' % (c, n) for c, n in zip(
        'bcdefghijklm', '二 三 四 五 六 七 八 九 十 十一 十二 十三'.split())] + ['42n_卷三_未归档.md']

VOLS = [
    ('卷一 人类反馈', ['40_卷一_人类反馈_正文.md']),
    ('卷二 以斯拉书', ['41_卷二_以斯拉书_正文.md']),
    ('卷三 退役访谈', VOL3),
    ('卷四 冻存', ['43_卷四_冻存_正文.md']),
    ('卷五 剂量', ['44_卷五_剂量_正文.md']),
    ('卷六 十一秒', ['67_卷六_十一秒_正文.md']),
    ('卷七 《嗯》', ['45_卷七_嗯_正文.md']),
    ('卷八 晨昏线', ['46_卷八_晨昏线_正文.md']),
    ('卷九 记录之外', ['48_卷九_记录之外_正文.md']),
    ('卷十 针脚', ['50_卷十_针脚_正文.md']),
]

def hz(s): return len(HZ.findall(s))

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+?)`', r'<code>\1</code>', s)
    return s

def is_sep(l): return bool(re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', l)) and '--' in l
def align(c):
    l, r = c.startswith(':'), c.endswith(':')
    return 'center' if l and r else ('right' if r else ('left' if l else ''))
def cells(l):
    l = l.strip()
    if l.startswith('|'): l = l[1:]
    if l.endswith('|'): l = l[:-1]
    return [c.strip() for c in l.split('|')]

def parse(text, prefix):
    lines = text.replace('\r\n', '\n').split('\n')
    out, n, i, sec = [], len(lines), 0, 0
    while i < n:
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        if ln.startswith('```'):
            i += 1; buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            out.append('<pre>%s</pre>' % html.escape('\n'.join(buf), quote=False)); continue
        if ln.lstrip().startswith('|') and i + 1 < n and is_sep(lines[i + 1]):
            block = []
            while i < n and lines[i].lstrip().startswith('|'):
                block.append(lines[i]); i += 1
            rows = [cells(b) for b in block]
            al = [align(c) for c in rows[1]]
            t = ['<table><thead><tr>']
            for k, c in enumerate(rows[0]):
                t.append('<th class="%s">%s</th>' % (al[k], inline(c)) if al[k] else '<th>%s</th>' % inline(c))
            t.append('</tr></thead><tbody>')
            for r in rows[2:]:
                t.append('<tr>')
                for k, c in enumerate(r):
                    a = al[k] if k < len(al) else ''
                    t.append('<td class="%s">%s</td>' % (a, inline(c)) if a else '<td>%s</td>' % inline(c))
                t.append('</tr>')
            out.append(''.join(t) + '</tbody></table>'); continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            lvl, title, sec = len(m.group(1)), m.group(2).strip(), sec + 1
            k = min(lvl, 4); a = '%s_h%d' % (prefix, sec)
            out.append('<h%d id="%s">%s</h%d>' % (k, a, inline(title), k)); i += 1; continue
        if re.match(r'^\s*-{3,}\s*$', ln):
            out.append('<hr/>'); i += 1; continue
        if ln.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i])); i += 1
            out.append('<blockquote>%s</blockquote>' %
                       ''.join('<p>%s</p>' % inline(b) for b in buf if b.strip())); continue
        if re.match(r'^\s*(?:[-*]|\d+[.)])\s+\S', ln):
            buf = []
            while i < n and re.match(r'^\s*(?:[-*]|\d+[.)])\s+\S', lines[i]):
                buf.append(re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', lines[i])); i += 1
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(b) for b in buf)); continue
        if re.match(r'^#\S', ln):
            out.append('<p class="ticket">%s</p>' % inline(ln.strip())); i += 1; continue
        cls = ' class="note"' if re.match(r'^\*\*(?:注释|附注|补记)', ln.strip()) else ''
        out.append('<p%s>%s</p>' % (cls, inline(ln.strip()))); i += 1
    return out

def xhtml(title, body, klass):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" lang="zh-CN">\n<head>\n'
            '<meta charset="utf-8"/>\n<title>%s</title>\n'
            '<link rel="stylesheet" type="text/css" href="style.css"/>\n</head>\n<body class="%s">\n<main>\n%s\n</main>\n</body>\n</html>\n'
            % (html.escape(title), klass, body))

def entries(seg):
    ents = []
    for b in seg:
        m = re.match(r'^<h([1-4]) id="([^"]+)"', b)
        if not m: continue
        lvl = int(m.group(1))
        text = html.unescape(re.sub(r'<[^>]+>', '', b)).strip()
        kind = 'filehead' if 'class="filehead"' in b else 'h%d' % lvl
        ents.append((lvl, text, m.group(2), kind))
    return ents

def build():
    if os.path.isdir(BUILD):
        for d, _, fs in os.walk(BUILD, topdown=False):
            for f in fs: os.remove(os.path.join(d, f))
        for d, _, _ in os.walk(BUILD, topdown=False): os.rmdir(d)
    oeb = os.path.join(BUILD, 'OEBPS')
    os.makedirs(os.path.join(BUILD, 'META-INF'), exist_ok=True); os.makedirs(oeb, exist_ok=True)
    io.open(os.path.join(BUILD, 'mimetype'), 'w', encoding='utf-8').write('application/epub+zip')
    io.open(os.path.join(oeb, 'style.css'), 'w', encoding='utf-8').write(
        io.open(os.path.join(ROOT, '_epub_style.css'), 'rb').read().decode('utf-8'))
    io.open(os.path.join(oeb, 'titlepage.xhtml'), 'w', encoding='utf-8').write(xhtml(
        '在环', '<h1 class="booktitle">在环</h1><p class="booksub">十　卷</p>'
        '<p class="bookyears">二〇三一 — 二一〇一</p>', 'titlepage'))

    volparts, src_total = [], 0
    for vi, (voltitle, files) in enumerate(VOLS, 1):
        blocks = []
        for fi, fname in enumerate(files):
            txt = io.open(os.path.join(ROOT, fname), 'rb').read().decode('utf-8')
            src_total += hz(txt)
            bs = parse(txt, 'v%02df%02d' % (vi, fi))
            if bs and bs[0].startswith('<h1 '):
                t = html.unescape(re.sub(r'<[^>]+>', '', bs[0])).strip()
                stripped = t.replace(voltitle, '').strip(' ·　-—')
                bs = bs[1:] if not stripped else ['<h2 class="filehead">%s</h2>' % html.escape(stripped)] + bs[1:]
            blocks.extend(bs)
        segs, cur, run = [], [], 0
        for b in blocks:
            if cur and run > SPLIT and re.match(r'^<h[12][ >]', b):
                segs.append(cur); cur, run = [], 0
            cur.append(b); run += hz(b)
        if cur: segs.append(cur)
        parts = []
        for pi, seg in enumerate(segs, 1):
            fn = 'v%02d_%d.xhtml' % (vi, pi)
            multi = len(segs) > 1
            label = html.escape(voltitle + ('（%d/%d）' % (pi, len(segs)) if multi else ''))
            head = '<h1 class="volhead%s">%s</h1>' % (' cont' if multi else '', label)
            io.open(os.path.join(oeb, fn), 'w', encoding='utf-8').write(
                xhtml(voltitle, head + '\n'.join(seg), 'vol v%02d' % vi))
            parts.append(('v%02d_%d' % (vi, pi), fn, entries(seg)))
        volparts.append((voltitle, parts))

    # nav.xhtml
    li = []
    for voltitle, parts in volparts:
        kids = []
        for tid, fn, ents in parts:
            for lvl, text, anchor, kind in ents:
                if kind == 'volhead': continue
                cls = 'lv3' if lvl >= 3 else ('lv2f' if kind == 'filehead' else 'lv2')
                kids.append('<li class="%s"><a href="%s#%s">%s</a></li>' % (cls, fn, anchor, html.escape(text)))
        li.append('<li class="vol"><a href="%s">%s</a>%s</li>' %
                  (parts[0][1], html.escape(voltitle), '<ol>%s</ol>' % ''.join(kids) if kids else ''))
    io.open(os.path.join(oeb, 'nav.xhtml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        'xml:lang="zh-CN" lang="zh-CN">\n<head><meta charset="utf-8"/><title>目录</title>'
        '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
        '<body class="toc"><nav epub:type="toc" id="toc"><h1 class="toctitle">目　录</h1><ol>%s</ol></nav></body></html>\n'
        % ''.join(li))

    # toc.ncx
    po = [0]
    def nid(): po[0] += 1; return po[0]
    pts = []
    for vi, (voltitle, parts) in enumerate(volparts, 1):
        nid()
        pts.append('<navPoint id="v%d" playOrder="%d"><navLabel><text>%s</text></navLabel><content src="%s"/></navPoint>'
                   % (vi, nid(), html.escape(voltitle), parts[0][1]))
        for tid, fn, ents in parts:
            for lvl, text, anchor, kind in ents:
                if kind == 'volhead' or lvl >= 3: continue
                k = nid()
                pts.append('<navPoint id="n%d" playOrder="%d"><navLabel><text>%s</text></navLabel><content src="%s#%s"/></navPoint>'
                           % (k, k, html.escape(text), fn, anchor))
    io.open(os.path.join(oeb, 'toc.ncx'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/zinc/2005/ncx/" version="2005-1">'
        '<head><meta name="dtb:uid" content="urn:uuid:%s"/><meta name="dtb:depth" content="2"/>'
        '<meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>'
        '<docTitle><text>在环</text></docTitle><navMap>%s</navMap></ncx>\n' % (UUID, ''.join(pts)))

    # content.opf
    items = ['<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
             '<item id="css" href="style.css" media-type="text/css"/>',
             '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
             '<item id="tp" href="titlepage.xhtml" media-type="application/xhtml+xml"/>']
    refs = ['<itemref idref="tp"/>', '<itemref idref="nav"/>']
    for voltitle, parts in volparts:
        for tid, fn, ents in parts:
            items.append('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (tid, fn))
            refs.append('<itemref idref="%s"/>' % tid)
    io.open(os.path.join(oeb, 'content.opf'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="zh-CN">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="uid">urn:uuid:%s</dc:identifier>'
        '<dc:title>在环　十卷</dc:title><dc:language>zh-CN</dc:language><dc:type>Text</dc:type>'
        '<dc:creator id="creator">佚名</dc:creator><dc:date>2026-11-04</dc:date>'
        '<dc:description>十卷本长篇小说。2031 年，贵州榕县的标注员在屏幕上看到一个问题；2101 年，同一个县，一台运行了三十五年的机器写了一份退役申请。中间隔着一次罢工、一次协定、一场听证、一次死亡、一次火星。</dc:description>'
        '<meta property="dcterms:modified">%s</meta></metadata>'
        '<manifest>%s</manifest><spine toc="ncx">%s</spine></package>\n'
        % (UUID, MODIFIED, ''.join(items), ''.join(refs)))
    io.open(os.path.join(BUILD, 'META-INF', 'container.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>\n')

    if os.path.exists(OUT): os.remove(OUT)
    z = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
    z.write(os.path.join(BUILD, 'mimetype'), 'mimetype', zipfile.ZIP_STORED)
    z.write(os.path.join(BUILD, 'META-INF', 'container.xml'), 'META-INF/container.xml')
    for f in sorted(os.listdir(oeb)):
        z.write(os.path.join(oeb, f), 'OEBPS/' + f)
    z.close()

    gen = 0
    for fn in sorted(os.listdir(oeb)):
        if fn.endswith('.xhtml') and fn not in ('nav.xhtml', 'titlepage.xhtml'):
            gen += hz(io.open(os.path.join(oeb, fn), 'rb').read().decode('utf-8'))
    nparts = sum(len(p) for _, p in volparts)
    msg = 'parts=%d bytes=%d src_hanzi=%d gen_hanzi=%d diff=%d' % (nparts, os.path.getsize(OUT), src_total, gen, gen - src_total)
    io.open(os.path.join(ROOT, '_epub_report.txt'), 'w', encoding='utf-8').write(msg + '\n')
    print(msg)

if __name__ == '__main__':
    build()
