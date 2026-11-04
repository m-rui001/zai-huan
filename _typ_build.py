# -*- coding: utf-8 -*-
"""正文 Markdown → Typst（打印轨）。每卷一个 .typ，附 main.typ 汇总与样式。"""
import io, os, re, glob, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TYP = os.path.join(ROOT, 'typst')

VOL3 = ['42_卷三_退役访谈_档案卷一.md'] + [
    '42%s_卷三_退役访谈_档案卷%s.md' % (c, n) for c, n in zip(
        'bcdefghijklm', '二 三 四 五 六 七 八 九 十 十一 十二 十三'.split())] + ['42n_卷三_未归档.md']
VOLS = [
    ('卷一 人类反馈', 'v01', ['40_卷一_人类反馈_正文.md']),
    ('卷二 以斯拉书', 'v02', ['41_卷二_以斯拉书_正文.md']),
    ('卷三 退役访谈', 'v03', VOL3),
    ('卷四 冻存', 'v04', ['43_卷四_冻存_正文.md']),
    ('卷五 剂量', 'v05', ['44_卷五_剂量_正文.md']),
    ('卷六 十一秒', 'v06', ['67_卷六_十一秒_正文.md']),
    ('卷七 《嗯》', 'v07', ['45_卷七_嗯_正文.md']),
    ('卷八 晨昏线', 'v08', ['46_卷八_晨昏线_正文.md']),
    ('卷九 记录之外', 'v09', ['48_卷九_记录之外_正文.md']),
    ('卷十 针脚', 'v10', ['50_卷十_针脚_正文.md']),
]

ESC_CH = '\\*_<>`[]{}#$@~^'
HEAD_CH = '-+='


def esc(s):
    out = []
    for ch in s:
        if ch in ESC_CH:
            out.append('\\' + ch)
        else:
            out.append(ch)
    return ''.join(out)


def lit(s):
    """escape for a typst single-line string literal"""
    return (s.replace('\\', '\\\\').replace('"', '\\"')
             .replace('\t', '\\t'))


TOK = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*)')


def inline_md(s):
    """markdown inline → typst markup（非强调部分全部转义）"""
    res, pos = [], 0
    for m in TOK.finditer(s):
        res.append(esc(s[pos:m.start()]))
        t = m.group(0)
        if t[0] == '`':
            res.append('#raw("' + lit(t[1:-1]) + '")')
        elif t.startswith('**'):
            res.append('*' + esc(t[2:-2]) + '*')
        else:
            res.append('_' + esc(t[1:-1]) + '_')
        pos = m.end()
    res.append(esc(s[pos:]))
    return ''.join(res)


def line_out(s):
    """段落行首若是 typst 标记字符，补反斜杠"""
    if s and s[0] in HEAD_CH:
        return '\\' + s
    return s


def is_sep(l):
    return bool(re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', l)) and '--' in l


def cells(l):
    l = l.strip()
    if l.startswith('|'):
        l = l[1:]
    if l.endswith('|'):
        l = l[:-1]
    return [c.strip() for c in l.split('|')]


def md_to_typ(path, voltitle, base):
    """base=1：H1→=，H2→==；base=2：文件头→==，章→=== """
    txt = io.open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    lines = txt.split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            while buf and not buf[-1].strip():
                buf.pop()
            while buf and not buf[0].strip():
                buf.pop(0)
            if buf:
                body = '\\n'.join(lit(b) for b in buf)
                out.append('#raw(block: true, "%s")' % body)
            continue
        if ln.lstrip().startswith('|') and i + 1 < n and is_sep(lines[i + 1]):
            block = []
            while i < n and lines[i].lstrip().startswith('|'):
                block.append(lines[i])
                i += 1
            rows = [cells(b) for b in block]
            ncol = max(len(r) for r in rows)
            aligns = []
            for k in range(ncol):
                a = rows[1][k] if k < len(rows[1]) else ''
                aligns.append('center' if a.startswith(':') and a.endswith(':')
                              else ('right' if a.endswith(':') else 'left'))
            pad = lambda r, k: (r[k] if k < len(r) else '')

            def row(r, cls=''):
                return ', '.join(cls + '[' + inline_md(pad(r, k)) + ']'
                                 for k in range(ncol))
            args = ['columns: %d' % ncol,
                    'align: (%s)' % ', '.join(a for a in aligns),
                    'inset: (x: 4pt, y: 2.4pt)',
                    'stroke: 0.4pt']
            parts = ['#table(\n  ' + ',\n  '.join(args) + ',']
            if len(rows) > 2:
                parts.append('  table.header(%s),' % row(rows[0]))
                parts.append(',\n  '.join(row(r) for r in rows[2:]))
            else:
                parts.append(',\n  '.join(row(r) for r in rows[1:2]))
            parts.append(')')
            out.append('\n'.join(parts))
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                t = title.replace(voltitle, '').strip(' ·　-—')
                if not t:
                    i += 1
                    continue
                out.append('=' * base + ' ' + inline_md(t))
            else:
                out.append('=' * min(base + lvl - 1, 4) + ' ' + inline_md(title))
            i += 1
            continue
        if re.match(r'^\s*-{3,}\s*$', ln):
            out.append('#v(0.7em) #align(center)[#box(height: 0.4pt, width: 2.2em, '
                       'fill: rgb(154, 154, 154))] #v(0.7em)')
            i += 1
            continue
        if ln.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            body = '\n\n'.join(line_out(inline_md(b)) for b in buf if b.strip())
            if body:
                out.append('#quote(block: true)[\n%s\n]' % body)
            continue
        if re.match(r'^\s*(?:[-*]|\d+[.)])\s+\S', ln):
            buf = []
            while i < n and re.match(r'^\s*(?:[-*]|\d+[.)])\s+\S', lines[i]):
                buf.append(re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', lines[i]))
                i += 1
            ordered = bool(re.match(r'^\s*\d', ln))
            mark = '1.' if ordered else '-'
            out.append('\n'.join('%s %s' % (mark, inline_md(b)) for b in buf))
            continue
        if re.match(r'^#\S', ln):
            out.append('#raw("%s")' % lit(ln.strip()))
            i += 1
            continue
        out.append(line_out(inline_md(ln.strip())))
        i += 1
    return out


HEADER = '''#let cjk = ("Noto Serif SC", "SimSun")
#set document(title: "在环", author: "佚名")
#set page(paper: "a5", margin: (top: 2.3cm, bottom: 2.1cm, left: 2.05cm, right: 1.85cm))
#set text(font: cjk, size: 10.5pt, lang: "zh", region: "cn", overhang: true,
          kerning: true)
#set par(justify: true, first-line-indent: 2em, leading: 0.92em, spacing: 0.3em)
#set heading(numbering: none)
#set list(indent: 1.8em, marker: "•")
#set quote(block: true)

#show heading.where(level: 1): it => {
  pagebreak(weak: false)
  set par(first-line-indent: 0em)
  v(3.2em)
  set align(center)
  text(19pt, weight: "bold", it.body)
  v(2.6em)
}
#show heading.where(level: 2): it => {
  pagebreak(weak: true)
  set par(first-line-indent: 0em)
  v(1.5em)
  set align(center)
  text(12.5pt, weight: "bold", it.body)
  v(1.3em)
}
#show heading.where(level: 3): it => {
  set par(first-line-indent: 0em)
  v(1.1em)
  text(10.8pt, weight: "bold", it.body)
  v(0.5em)
}
#show heading.where(level: 4): it => {
  set par(first-line-indent: 0em)
  v(0.9em)
  text(size: 10.5pt, style: "italic", fill: rgb(125, 125, 125), it.body)
  v(0.4em)
}
#show raw.where(block: true): set text(size: 8.4pt, font: ("Consolas", "Courier New"))
#show raw.where(block: true): set block(fill: rgb(244, 243, 239), inset: (x: 6pt, y: 5pt), above: 0.7em, below: 0.7em)
#show raw.where(block: true): set par(first-line-indent: 0em, justify: false)
#show quote: set text(size: 9.6pt, font: cjk)
#show quote: set par(first-line-indent: 0em)
#show quote: it => block(inset: (left: 1.4em, right: 1.2em), it)
#show table: set text(size: 8.6pt)
'''


def build_volume(voltitle, tag, files):
    chunks = [HEADER]
    multi = len(files) > 1
    if multi:
        chunks.append('= ' + inline_md(voltitle))
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            raise SystemExit('missing ' + f)
        chunks.append('// ==== %s' % f)
        chunks.extend(md_to_typ(p, voltitle, 2 if multi else 1))
    src = '\n\n'.join(chunks) + '\n'
    out = os.path.join(TYP, tag + '.typ')
    io.open(out, 'w', encoding='utf-8').write(src)
    return out, len(src)


MAIN = '''#let cjk = ("Noto Serif SC", "SimSun")
#set document(title: "在环", author: "佚名")
#set page(paper: "a5", margin: (top: 2.3cm, bottom: 2.1cm, left: 2.05cm, right: 1.85cm),
          header: context {
            if page_number() > 2 {
              set text(size: 8pt, fill: rgb(154, 154, 154), font: cjk)
              align(center, counter(page).display())
            }
          })
#set text(font: cjk, size: 10.5pt, lang: "zh", region: "cn", overhang: true,
          kerning: true)
#set par(justify: true, first-line-indent: 2em, leading: 0.92em, spacing: 0.3em)
#set heading(numbering: none)

#show outline.entry: it => {
  set par(leading: 1.15em, spacing: 0.25em, justify: false)
  set text(size: 9.4pt)
  link(it.element, it.body)
}

#pagebreak(weak: false)
#{
  set align(center)
  set par(first-line-indent: 0em)
  v(6em)
  text(30pt, weight: "bold", "在环")
  v(1.2em)
  text(11pt, fill: rgb(154, 154, 154), "十卷")
  v(0.6em)
  text(9.5pt, fill: rgb(176, 176, 176), "2031–2101")
}
#pagebreak(weak: false)
#outline(title: [目录], depth: 2)
'''


def build_main():
    src = MAIN
    for _, tag, _ in VOLS:
        src += '\n#include "%s.typ"\n' % (tag + '.typ')
    p = os.path.join(TYP, 'main.typ')
    io.open(p, 'w', encoding='utf-8').write(src)
    return p


if __name__ == '__main__':
    os.makedirs(TYP, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    log = []
    for voltitle, tag, files in VOLS:
        if only and only != tag:
            continue
        path, size = build_volume(voltitle, tag, files)
        log.append('%s %.1f KB' % (tag, size / 1024.0))
    if not only:
        build_main()
    print('\n'.join(log).encode('ascii', 'replace').decode())
