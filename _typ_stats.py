# -*- coding: utf-8 -*-
"""量页：每页行数、字数、文字块上下缘，用来判断版心是否吃满。"""
import io, os, sys
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(ROOT, '在环_十卷_打印本.pdf')


def stats(doc, p):
    pg = doc[p - 1]
    d = pg.get_text('dict')
    lines, chars = 0, 0
    ys = []
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            txt = ''.join(s['text'] for s in l['spans'])
            if not txt.strip():
                continue
            lines += 1
            chars += len(txt.strip())
            ys.append(l['bbox'][1])
    h = pg.rect.height
    top = min(ys) if ys else 0
    bot = max(ys) if ys else 0
    return dict(page=p, h=round(h, 1), lines=lines, chars=chars,
                top=round(top, 1), bot=round(bot, 1))


if __name__ == '__main__':
    doc = pymupdf.open(PDF)
    print('pages', doc.page_count)
    ps = [int(x) for x in sys.argv[1:]]
    rows = [stats(doc, p) for p in ps if 1 <= p <= doc.page_count]
    body = [r for r in rows if r['lines'] > 6]
    if body:
        r = max(body, key=lambda x: x['lines'])
        pitch = (r['bot'] - r['top']) / max(1, r['lines'] - 1)
        print('pitch_pt', round(pitch, 2), 'text_height_pt',
              round(r['h'] - 2 * 70, 1))
    for x in rows:
        print(x)
