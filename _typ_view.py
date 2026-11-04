# -*- coding: utf-8 -*-
"""从打印本 PDF 里出指定页的 PNG，供逐页看版。"""
import io, os, re, sys
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(ROOT, '在环_十卷_打印本.pdf')
OUT = os.path.join(ROOT, 'scratch', 'view')


def pages():
    doc = pymupdf.open(PDF)
    return doc


if __name__ == '__main__':
    doc = pages()
    print('pages', doc.page_count)
    os.makedirs(OUT, exist_ok=True)
    want = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 6, 7]
    for p in want:
        if p < 1 or p > doc.page_count:
            continue
        pg = doc[p - 1]
        pix = pg.get_pixmap(dpi=125)
        f = os.path.join(OUT, 'p%04d.png' % p)
        pix.save(f)
        print('wrote', f, os.path.getsize(f))
