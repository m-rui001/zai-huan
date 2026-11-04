# -*- coding: utf-8 -*-
import io
BLOCK = '''
## §三百二十九（排版轨：行距复核与 EPUB 轨说明，2026-11-04）

一，行距实测（打印本，pymupdf 量基线到基线）：正文 10.5pt／17.5pt＝1.67 倍；文书卷 9.9pt／15.5pt＝1.57 倍；注释 9.5pt 原 12.2pt＝1.28 倍；机器行 8.9pt 原 10.8pt＝1.21 倍。「奇怪」不在正文，在副级：注与机器行被压到 1.2 倍上下，与正文 1.67 倍并排时，一页里的节奏一跳一跳。

二，改法（只动副级，正文字距行距一字未动）：注 9.35→9.5pt、leading 0.96→1.22em（约 1.5 倍）；机器行 leading 0.62→0.85em；代码块 0.5→0.72em；引文 0.8→0.9em；段距 正文 0.3→0.42em、文书 0.5→0.55em。全书 2,148→2,276 页，`_typchk.py` misses 0。

三，EPUB 轨的由来（答案）：EPUB 不是从 Typst 转的。Typst 没有 EPUB 后端，两轨同出一份 Markdown——`_epub_build.py` 直出 22 个部件（本版 1,417,182 字节），`_typ3.py` 出打印本。用户若嫌 EPUB 质量不够，改的是 `_epub_style.css` 与那个生成器，不必碰 Typst。

四，本轮把五种字面搬进 EPUB：`p.note` 楷体（0.92em、1.7 倍、首行不缩进、墨色 #3a3a3a），注内 strong 走黑体；`body.v03`／`body.v07` 整卷仿宋、齐左、0.45em 段距；`pre` 等宽、1.55 倍、浅底、左缘一道专色 2px。与打印轨同口径。`_epub_check.py` problems=0。

五，留一条口径：屏幕轨的行距用倍数（1.92／1.7／1.86／1.55），打印轨用 em 的 leading；两边不互抄数值，只抄比例。
'''
for p in (r'E:\Novel2\16_细节毛病账.md', r'E:\Novel2\30_进度.md'):
    io.open(p, 'a', encoding='utf-8').write(BLOCK)
print('ok')
