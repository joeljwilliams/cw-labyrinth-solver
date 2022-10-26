#!/usr/bin/env python3

import numpy as np
from PIL import Image, ImagePalette

pl = Image.open('palette-3.png')
im = Image.open('maze.jpg').quantize(8, method=Image.Quantize.LIBIMAGEQUANT, palette=pl, dither=Image.Dither.NONE).convert(mode="RGB")
smol = im.reduce(5).quantize(8, palette=pl).convert(mode="RGB")
#smol.show()
smol.save('out.png')
nim = np.array(smol)
w,h = smol.size
pixmap = {
    (255, 255, 255): [9, '⬜️'], # white : passage
    (  0,   0,   0): [0, '⬛️'], # black : wall
    (255,   0,   0): [1, '🟥'], # red   : boss
    ( 55,  59, 255): [2, '🟦'], # blue  : landmark
    ( 57, 156,  42): [3, '🟩'], # green : fountain
    (137, 121, 216): [4, '🟪'], # lilac : monster
    (255, 162,   0): [5, '🟧'], # orange: bonfire
    (  7, 237, 130): [6, '🟨'], # cyan  : treasure
}
for r in range(h):
    for c in range(w):
        print(pixmap[tuple(nim[r,c])][1], end='')
    print()
