# -*- coding: utf-8 -*-
"""向日志／账目类活文件末尾追加条目，按该文件自己的 EOL 写。用法：python _app30.py <utf8文本文件> [文件名glob，默认 30_*.md]"""
import io, sys, glob

F = glob.glob(sys.argv[2] if len(sys.argv) > 2 else '30_*.md')[0]
t = io.open(F, encoding='utf-8', newline='').read()
E = '\r\n' if '\r\n' in t else '\n'
entry = io.open(sys.argv[1], encoding='utf-8').read().rstrip('\n').replace('\r\n', '\n').split('\n')
L = t.split(E)
while L and not L[-1].strip():
    L.pop()
L.append('')
L.extend(entry)
L.append('')
io.open(F, 'w', encoding='utf-8', newline='').write(E.join(L))
raw = io.open(F, 'rb').read()
print('appended', len(entry), 'lines; EOL', E.encode('unicode_escape').decode(),
      'bare-LF', raw.count(b'\n') - raw.count(b'\r\n'))
