# -*- coding: utf-8 -*-
"""正文 Markdown → Typst（打印轨·设计版）。

五种字面五种职能：
  叙事（宋体）—— 首行缩进两字，10.5pt，宽行距；
  注释（楷体）—— 小半号，齐左，凯特琳的手；
  文书（仿宋）—— 卷三／卷七整卷与各卷附录，齐左分块，9.9pt，像档案本身；
  机器（等宽）—— 工单行、【任务批次…】、step 记录，浅底，像屏幕；
  标题（黑体）—— 章题、强调，黑体是官署的字面。
章题三层：章号（小字灰色）／章名（大字）／地点日号（小字灰色）。
合唱章整段收窄，不缩进，读作另一个声音。
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TYP = os.path.join(ROOT, 'typst')

VOL3 = ['42_卷三_退役访谈_档案卷一.md'] + [
    '42%s_卷三_退役访谈_档案卷%s.md' % (c, n) for c, n in zip(
        'bcdefghijklm', '二 三 四 五 六 七 八 九 十 十一 十二 十三'.split())] + ['42n_卷三_未归档.md']
VOLS = [
    ('卷一 人类反馈', 'v01', ['40_卷一_人类反馈_正文.md']),
    ('卷二 以斯拉书（注释本）', 'v02', ['41_卷二_以斯拉书_正文.md']),
    ('卷三 退役访谈', 'v03', VOL3),
    ('卷四 冻存', 'v04', ['43_卷四_冻存_正文.md']),
    ('卷五 剂量', 'v05', ['44_卷五_剂量_正文.md']),
    ('卷六 十一秒', 'v06', ['67_卷六_十一秒_正文.md']),
    ('卷七 《嗯》', 'v07', ['45_卷七_嗯_正文.md']),
    ('卷八 晨昏线', 'v08', ['46_卷八_晨昏线_正文.md']),
    ('卷九 记录之外', 'v09', ['48_卷九_记录之外_正文.md']),
    ('卷十 针脚', 'v10', ['50_卷十_针脚_正文.md']),
]
DOC_VOLS = ('v03', 'v07')          # 整卷按文书排

ESC_CH = '\\*_<>`[]{}#$@~^'
HEAD_CH = '-+='
SCREEN = re.compile(r'^(?:【[^】]*】|step\s+\d+\s|#[A-Z]{1,6}-)')

CHAP = re.compile(r'^(?:第[一二三四五六七八九十百千0-9]+[章节卷]|'
                  r'[一二三四五六七八九十]{1,3}(?:\s|$|　)|档案卷|卷[一二三四五六七八九十]|'
                  r'合唱[一二三四五六七八九十])')
SUB = re.compile(r'^[一二三四五六七八九十]+之[一二三四五六七八九十]')
NAMES = ('尾声', '终章', '附录', '补遗', '无编号页', '证据卷宗', '编者说明',
         '未归档', '整理者说明', '火星线')


def is_chapter(t):
    t = t.strip()
    if any(t.startswith(n) for n in NAMES):
        return True
    if SUB.match(t):
        return False
    return bool(CHAP.match(t))


def esc(s):
    return ''.join('\\' + c if c in ESC_CH else c for c in s)


def lit(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\t', '\\t')


TOK = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*\n]+\*)')


def inline_md(s):
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


def table_typ(rows, flip_at=6):
    ncol = max(len(r) for r in rows)
    aligns = []
    for k in range(ncol):
        a = rows[1][k] if k < len(rows[1]) else ''
        aligns.append('center' if a.startswith(':') and a.endswith(':')
                      else ('right' if a.endswith(':') else 'left'))
    pad = lambda r, k: (r[k] if k < len(r) else '')

    def row(r, head=False):
        cs = []
        for k in range(ncol):
            v = inline_md(pad(r, k))
            cs.append('[*' + v + '*]' if head and v else '[' + v + ']')
        return ', '.join(cs)
    args = ['columns: %d' % ncol,
            'align: (%s)' % ', '.join(aligns),
            'stroke: 0.4pt + rule']
    body = []
    if len(rows) > 2:
        body.append('table.header(%s),' % row(rows[0], True))
        body.append(',\n  '.join(row(r) for r in rows[2:]))
    else:
        body.append(row(rows[1], True))
    tbl = ('#table(\n  ' + ',\n  '.join(args) + ',\n  ' + '\n  '.join(body) + '\n)')
    if ncol >= flip_at:
        tbl = ('#page(flipped: true, columns: 1)[\n#set par(first-line-indent: 0em)\n'
               '#set align(left)\n' + tbl + '\n]')
    return tbl


def md_to_typ(path, voltitle, base, flip_at=6, basefont='cjk'):
    txt = io.open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    lines = txt.split('\n')
    out, i, n = [], 0, len(lines)
    chorus = None                                  # 合唱段的缓冲
    in_appx = False                                # 附录：档案体
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
                out.append('#raw(block: true, "%s")' % '\\n'.join(lit(b) for b in buf))
            continue
        if ln.lstrip().startswith('|') and i + 1 < n and is_sep(lines[i + 1]):
            block = []
            while i < n and lines[i].lstrip().startswith('|'):
                block.append(lines[i])
                i += 1
            out.append(table_typ([cells(b) for b in block], flip_at))
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            if chorus is not None:
                out.append('#chorus[\n' + '\n\n'.join(chorus) + '\n]')
                chorus = None
            lvl, title = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                t = title.replace(voltitle, '').strip(' ·　-—')
                if not t:
                    i += 1
                    continue
                out.append('=' * base + ' ' + inline_md(t))
            else:
                d = min(base + lvl - 1, 4)
                if d == 2 and not is_chapter(title):
                    d = 3
                out.append('=' * d + ' ' + inline_md(title))
                if d == 2 and title.startswith('合唱'):
                    chorus = []
                if d == 2 and title.startswith('附录') and basefont != 'fang':
                    out.append('#set text(font: fang)')
                    out.append('#set par(first-line-indent: 0em, spacing: 0.55em, '
                               'leading: 1.0em)')
                    out.append('#show strong: it => text(font: hei, weight: "bold", it.body)')
                    in_appx = True
                elif d == 2 and in_appx:
                    out.append('#set text(font: %s)' % basefont)
                    out.append('#set par(first-line-indent: (amount: 2em, all: true), spacing: 0.8em, '
                               'leading: 0.94em)')
                    out.append('#show strong: it => text(weight: "bold", it.body)')
                    in_appx = False
            i += 1
            continue
        if re.match(r'^\s*-{3,}\s*$', ln):
            k = i + 1
            while k < n and not lines[k].strip():
                k += 1
            if k < n and not re.match(r'^(?:#{1,6}\s|-{3,}$|>)', lines[k]):
                (chorus if chorus is not None else out).append(
                    '#v(0.9em) #align(center)[#line(length: 2.4em, '
                    'stroke: 0.5pt + rule)] #v(0.9em)')
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
            mark = '1.' if re.match(r'^\s*\d', ln) else '-'
            out.append('\n'.join('%s %s' % (mark, inline_md(b)) for b in buf))
            continue
        if SCREEN.match(ln.strip()):                # 屏幕与工单：等宽浅底
            buf = [ln.strip()]
            while i + 1 < n and lines[i + 1].strip() and \
                    not re.match(r'^(?:#{1,6}\s|-{3,}$|>|\|)', lines[i + 1].strip()) and \
                    not SCREEN.match(lines[i + 1].strip()) and \
                    len(buf) < 14 and lines[i + 1].strip().startswith(
                        ('被保险人', '申请项目', '模型建议', '置信度', '理由摘要',
                         '并发', '状态', '备注', '工号', '时间', '排队')):
                i += 1
                buf.append(lines[i].strip())
            i += 1
            (chorus if chorus is not None else out).append(
                '#moline[' + ' #linebreak() '.join(
                    line_out(inline_md(b)) for b in buf) + ']')
            continue
        seg = line_out(inline_md(ln.strip()))
        if re.match(r'^\*\*(?:注释|附注|补记)', ln.strip()):
            seg = '#note[%s]' % seg
        elif not out and chorus is None and len(ln.strip()) <= 60:
            seg = '#align(center)[#text(10pt, fill: soft, [%s])]' % seg
        (chorus if chorus is not None else out).append(seg)
        i += 1
    if chorus is not None:
        out.append('#chorus[\n' + '\n\n'.join(chorus) + '\n]')
    return out


STYLE = '''#let cjk = ("Noto Serif SC", "SimSun")
#let kai = ("KaiTi", "STKaiti", "Noto Serif SC")
#let fang = ("FangSong", "STFangsong", "Noto Serif SC")
#let hei = ("Noto Sans SC", "SimHei", "Microsoft YaHei")
#let mfont = ("DejaVu Sans Mono", "Consolas", "Noto Sans SC")
#let ink = rgb(28, 28, 28)
#let soft = rgb(124, 124, 124)
#let rule = rgb(188, 186, 180)
#let paper = rgb(246, 245, 241)
#let accent = rgb(88, 104, 118)
'''

PAGE = '''#set page(paper: "a5",
          margin: (top: 2.45cm, bottom: 2.15cm, left: 2.05cm, right: 1.85cm),
          numbering: "1",
          header: context {
            if here().page() > 1 {
              set text(size: 7.6pt, fill: soft, font: cjk)
              if calc.even(counter(page).get().at(-1)) {
                align(left, [在　环])
              } else {
                align(right, [#run-title])
              }
            }
          },
          footer: context {
            if here().page() > 1 {
              set text(size: 8.2pt, fill: soft, font: cjk)
              align(center, counter(page).display())
            }
          })
'''

BODY = '''#set text(font: __FONT__, size: __SIZE__, lang: "zh", region: "cn", fill: ink,
          overhang: true, kerning: true, hyphenate: false)
#set par(justify: true, first-line-indent: (amount: __INDENT__, all: true),
         leading: __LEAD__, spacing: __PSPACE__)
#set heading(numbering: none)
#set list(indent: 1.9em, marker: "•", body-indent: 1.1em)
#set enum(indent: 1.9em, body-indent: 1.1em)
#set quote(block: true)
#set table(inset: (x: 4.5pt, y: 2.8pt))
#show link: set text(fill: ink)

#let moline(body) = {
  set text(size: 8.9pt, font: mfont)
  set par(first-line-indent: 0em, justify: false, leading: 0.85em, spacing: 0.15em)
  block(above: 0.7em, below: 0.7em, rect(width: 100%, fill: paper,
        inset: (x: 7pt, y: 5pt),
        stroke: (left: 1pt + accent, top: none, right: none,
                 bottom: none), body))
}

#let chorus(body) = {
  set text(size: 10pt)
  set par(first-line-indent: 0em, leading: 0.98em, spacing: 0.45em)
  block(inset: (left: 1.9em, right: 1.7em), above: 0.5em, below: 0.9em, body)
}

#let note(body) = {
  show strong: it => text(font: hei, weight: "bold", it.body)
  set text(font: kai, size: 9.5pt, fill: rgb(56, 56, 56))
  set par(first-line-indent: 0em, leading: 1.22em, spacing: 0.45em)
  block(above: 0.5em, below: 0.6em, body)
}

#show heading.where(depth: 1): it => {
  pagebreak(weak: true)
  set par(first-line-indent: 0em)
  set align(center)
  v(4.0em)
  circle(radius: 0.62em, stroke: 0.8pt + accent)
  v(1.5em)
  text(18pt, weight: "bold", it.body)
  v(1.0em)
  line(length: 3.2em, stroke: 0.5pt + rule)
  v(3.6em)
}

#show heading.where(depth: 2): it => {
  __BREAK__
  set par(first-line-indent: 0em)
  set align(center)
  let raw = if "text" in it.body.fields() { it.body.text } else { none }
  let m = if raw == none { none } else {
    raw.match(regex("^((?:第[一二三四五六七八九十百千0-9]+章|合唱[一二三四五六七八九十]+|档案卷[一二三四五六七八九十]+))[ 　]*(.*)$"))
  }
  v(2.8em)
  if m == none {
    text(12.5pt, weight: "bold", font: hei, it.body)
  } else {
    let c = m.captures
    let rest = c.at(1)
    let w = rest.match(regex("^(.*?)[（(](.*?)[）)]$"))
    let name = if w == none { rest } else { w.captures.at(0) }
    let place = if w == none { none } else { w.captures.at(1) }
    text(7.8pt, fill: soft, c.at(0))
    v(0.85em)
    text(15pt, weight: "bold", font: hei, name)
    if place != none {
      v(0.7em)
      text(8.6pt, fill: soft, place)
    }
  }
  v(2.9em)
}
__D3__
#show heading.where(depth: 4): it => {
  set par(first-line-indent: 0em)
  v(1.0em)
  text(10.3pt, weight: "bold", fill: rgb(70, 70, 70), it.body)
  v(0.45em)
}
#show raw.where(block: true): set text(size: 8.5pt, font: mfont)
#show raw.where(block: true): set block(fill: paper, inset: (x: 8pt, y: 6pt),
                                          above: 0.9em, below: 0.9em)
#show raw.where(block: true): set par(justify: false, leading: 0.72em, spacing: 0em)
#show raw.where(block: false): set text(size: 9.2pt, font: mfont)
#show quote: set text(size: 9.7pt)
#show quote: set par(first-line-indent: 0em, leading: 0.9em)
#show quote: it => block(inset: (left: 1.6em, right: 1.4em), above: 0.7em, below: 0.7em, it)
#show table: set text(size: 8.6pt)
#show table: set par(first-line-indent: 0em, justify: false)
'''


D3_PLAIN = '''#show heading.where(depth: 3): it => {
  set par(first-line-indent: 0em)
  v(1.7em)
  text(10.8pt, weight: "bold", it.body)
  v(0.55em)
}'''
D3_DOC = '''#show heading.where(depth: 3): it => {
  set par(first-line-indent: 0em)
  v(1.9em)
  let raw = if "text" in it.body.fields() { it.body.text } else { "" }
  let m = raw.match(regex("^([^ 　]{1,8}(?:[ 　][A-Z0-9]{1,3})?)[ 　]+(.+)$"))
  if m == none {
    text(10.8pt, weight: "bold", it.body)
  } else {
    text(7.2pt, fill: accent, m.captures.at(0))
    linebreak()
    text(10.8pt, weight: "bold", m.captures.at(1))
  }
  v(0.55em)
}'''


def header_for(run_title, doc):
    body = (BODY.replace('__D3__', D3_DOC if doc else D3_PLAIN).replace('__SIZE__', '9.9pt' if doc else '10.5pt')
                .replace('__FONT__', 'fang' if doc else 'cjk')
                .replace('__INDENT__', '0em' if doc else '2em')
                .replace('__LEAD__', '0.8em' if doc else '0.8em')
                .replace('__PSPACE__', '0.8em' if doc else '0.8em')
                .replace('__BREAK__', 'pagebreak(weak: true)'))
    extra = ''
    return (STYLE + '#let run-title = "%s"\n\n' % run_title + PAGE + extra + body)


def build_volume(voltitle, tag, files):
    doc = tag in DOC_VOLS
    chunks = [header_for(voltitle, doc)]
    multi = len(files) > 1
    opener = '= ' + inline_md(voltitle)
    # 文书卷：卷首单栏，正文双栏（查考体例）；叙事卷通篇单栏（通读体例）
    chunks.append(opener)
    if doc:
        chunks.append('#pagebreak(weak: false)')
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            raise SystemExit('missing ' + f)
        body = md_to_typ(p, voltitle, 2 if multi else 1, 4 if doc else 6,
                         basefont='fang' if doc else 'cjk')
        chunks.append('// ==== %s' % f)
        if doc and chunks and any(c.startswith('== ') for c in chunks[-60:]):
            chunks.append('#pagebreak(weak: true)')
        chunks.extend(body)
    src = '\n\n'.join(chunks) + '\n'
    out = os.path.join(TYP, tag + '.typ')
    io.open(out, 'w', encoding='utf-8').write(src)
    return out, len(src)


FRONT = '''#set page(paper: "a5",
          margin: (top: 2.45cm, bottom: 2.15cm, left: 2.05cm, right: 1.85cm),
          numbering: none, header: none, footer: none)
#set text(font: cjk, size: 10.5pt, lang: "zh", region: "cn", fill: ink,
          overhang: true, kerning: true, hyphenate: false)
#set par(justify: false, first-line-indent: 0em, leading: 0.9em)
#set heading(numbering: none)
#show link: set text(fill: ink)

#show outline.entry: it => {
  set text(size: 9.5pt, fill: ink)
  set par(leading: 0.8em, spacing: 0.12em)
  if it.element.depth == 1 {
    set text(size: 10.5pt, weight: "bold")
    v(0.6em)
  }
  it
}

#{
  set align(center)
  v(5.0em)
  circle(radius: 1.5em, stroke: 1.1pt + accent)
  v(0.9em)
  circle(radius: 0.42em, stroke: 0.8pt + accent)
  v(2.2em)
  text(30pt, weight: "bold", "在　环")
  v(1.4em)
  line(length: 3.4em, stroke: 0.6pt + rule)
  v(1.2em)
  text(10.5pt, fill: soft, "长篇小说　十卷")
  v(1fr)
  text(9pt, fill: soft, "2031 — 2101")
  v(1.6em)
}
#pagebreak(weak: false)

#v(1fr)
#text(8.6pt, fill: soft)[《在环》十卷，正文九十四万余字。]
#text(8.6pt, fill: soft)[卷一 人类反馈／卷二 以斯拉书／卷三 退役访谈／卷四 冻存／卷五 剂量／卷六 十一秒／卷七 嗯／卷八 晨昏线／卷九 记录之外／卷十 针脚。]
#text(8.6pt, fill: soft)[本版由 Markdown 正文生成 Typst 源码排出，A5 开本。五种字面各司其职：叙事宋体，首行缩进两字；注释楷体，字小半号，是同一本书里的第二只手；卷三、卷七与附录用仿宋，齐左分块，照档案排；工单、屏幕行与 step 记录用等宽体浅底；章题与强调用黑体。章题分章号、章名、地点日号三层，合唱段整段收窄。]
#v(1fr)
#pagebreak(weak: false)

#{
  set align(center)
  v(1.0em)
  text(15pt, weight: "bold", "目　录")
  v(1.6em)
}
#outline(title: none, depth: 3)
#pagebreak(weak: false)
#counter(page).update(1)
'''


def build_main():
    src = STYLE + FRONT
    for _, tag, _ in VOLS:
        src += '\n#include "%s.typ"\n' % tag
    src += ('\n#pagebreak(weak: false)\n#v(1fr)\n'
            '#align(center)[#circle(radius: 0.5em, stroke: 0.8pt + accent)]\n'
            '#v(0.9em)\n#align(center)[#text(9pt, fill: soft, "全书完")]\n#v(1.6em)\n')
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
