"""Gera as imagens de assets/ (rode uma vez: python make_assets.py).
Todas as imagens são criadas por código (sem fontes externas), em formato PNG.
Troque por qualquer PNG seu mantendo o mesmo nome; se usar arte de terceiros, cite a fonte no README.
"""
import os
import numpy as np
from PIL import Image
import texture as T

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)
for name, fn in [("space", T.make_space), ("stars", T.make_stars), ("grid", T.make_grid),
                 ("drone", T.make_drone), ("packet", T.make_packet), ("obstacle", T.make_obstacle)]:
    # as funções geram linha 0 = embaixo; o PNG tem linha 0 = topo, então inverte ao salvar
    Image.fromarray(np.flipud(fn())).save(os.path.join(OUT, name + ".png"))
    print("gerado assets/%s.png" % name)
