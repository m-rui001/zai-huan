# -*- coding: utf-8 -*-
import io
BLOCK = '''
## §三百三十一（排版轨：行距定版——两条尺相等，2026-11-04）

一，量出来的真相：spacing 归零时，段间实测 7.6 磅，段内 18.4 磅。段间吃不到 leading，所以段与段被压得比行还紧；加 spacing 又直接叠在 leading 上（spacing 1.02em 时整本 2,960 页）。两条尺原来各走各的。

二，定版：`leading` 与 `spacing` 取同一个值——正文 0.8em／文书 0.8em，段内段间同为 16.1 磅（文书 14.5），差为零。p1100（卷八 合唱二 一名）逐行量过：16.1／16.0 全页一致，32.1 只是小节间隔。

三，页数 2,601（原 2,148）：差出来的不是空白，是原先被压掉的段间距离。`_typchk.py` misses 0。

四，口径：打印轨凡改行距，`leading` 与 `spacing` 必须同值；单动一条即回到两档间距。EPUB 轨不受影响（段距用 margin，行距单一倍数）。
'''
for p in (r'E:\Novel2\16_细节毛病账.md', r'E:\Novel2\30_进度.md'):
    io.open(p, 'a', encoding='utf-8').write(BLOCK)
print('ok')
