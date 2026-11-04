#let cjk = ("Noto Serif SC", "SimSun")
#let kai = ("KaiTi", "STKaiti", "Noto Serif SC")
#let fang = ("FangSong", "STFangsong", "Noto Serif SC")
#let hei = ("Noto Sans SC", "SimHei", "Microsoft YaHei")
#let mfont = ("DejaVu Sans Mono", "Consolas", "Noto Sans SC")
#let ink = rgb(28, 28, 28)
#let soft = rgb(124, 124, 124)
#let rule = rgb(188, 186, 180)
#let paper = rgb(246, 245, 241)
#let accent = rgb(88, 104, 118)
#set page(paper: "a5",
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

#include "v01.typ"

#include "v02.typ"

#include "v03.typ"

#include "v04.typ"

#include "v05.typ"

#include "v06.typ"

#include "v07.typ"

#include "v08.typ"

#include "v09.typ"

#include "v10.typ"

#pagebreak(weak: false)
#v(1fr)
#align(center)[#circle(radius: 0.5em, stroke: 0.8pt + accent)]
#v(0.9em)
#align(center)[#text(9pt, fill: soft, "全书完")]
#v(1.6em)
