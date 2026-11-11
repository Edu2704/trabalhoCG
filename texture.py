"""Texture.py equivalente (R06): criação de texturas OpenGL.

Para o esboço rodar sem assets, as texturas são geradas proceduralmente com numpy.
Para usar imagens reais, troque por Texture.from_file("assets/drone.png").
"""
import numpy as np
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont


class Texture:
    def __init__(self, rgba, wrap=GL_CLAMP_TO_EDGE, smooth=True):
        rgba = np.ascontiguousarray(rgba, dtype=np.uint8)
        self.height, self.width, _ = rgba.shape
        self.id = glGenTextures(1)                          # [OpenGL] glGenTextures
        glBindTexture(GL_TEXTURE_2D, self.id)               # [OpenGL] glBindTexture
        filt = GL_LINEAR if smooth else GL_NEAREST
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filt)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filt)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, rgba)       # [OpenGL] glTexImage2D

    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def delete(self):
        glDeleteTextures([self.id])

    # ---------- fábricas ----------
    @classmethod
    def from_file(cls, path, **kw):
        img = Image.open(path).convert("RGBA")
        return cls(np.flipud(np.array(img)), **kw)          # flip: origem da textura é embaixo

    @classmethod
    def from_text(cls, text, size=32, color=(255, 255, 255)):
        font = _load_font(size)
        l, t, r, b = font.getbbox(text)
        img = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((4 - l, 4 - t), text, font=font, fill=color + (255,))
        return cls(np.flipud(np.array(img)))


def _load_font(size):
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


# ---------- texturas procedurais (linha 0 = parte de baixo da imagem) ----------
def make_space(size=256):
    """Parallax camada 0 (fundo distante): gradiente de nebulosa, periódico (tileable)."""
    ys, xs = np.mgrid[0:size, 0:size]
    u, v = xs / size * 2 * np.pi, ys / size * 2 * np.pi
    n = 0.5 + 0.25 * np.sin(u + 2 * np.sin(v)) + 0.25 * np.sin(2 * v - u)
    img = np.zeros((size, size, 4), np.uint8)
    img[..., 0] = 6 + 22 * n
    img[..., 1] = 6 + 8 * n
    img[..., 2] = 24 + 46 * n
    img[..., 3] = 255
    return img


def make_stars(size=256, count=40, seed=3):
    """Parallax camada 1: estrelas sobre fundo transparente."""
    img = np.zeros((size, size, 4), np.uint8)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        x, y = rng.integers(1, size - 1, 2)
        b = int(rng.integers(150, 256))
        img[y, x] = (b, b, 255, 255)
        if rng.random() < 0.3:                       # estrelas maiores (cruz)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                img[y + dy, x + dx] = (b // 2, b // 2, 200, 255)
    return img


def make_grid(size=128):
    """Parallax camada 2 (mais próxima): grade cibernética com fundo transparente."""
    img = np.zeros((size, size, 4), np.uint8)
    ys, xs = np.mgrid[0:size, 0:size]
    lines = (xs % 32 == 0) | (ys % 32 == 0)
    img[lines] = (20, 140, 200, 110)
    return img


def make_drone(w=96, h=48):
    """Nave/drone apontando para a direita."""
    ys, xs = np.mgrid[0:h, 0:w]
    nx = xs / (w - 1) * 2 - 1
    ny = ys / (h - 1) * 2 - 1
    img = np.zeros((h, w, 4), np.uint8)
    body = np.abs(ny) <= (0.1 + 0.45 * (1 - nx))
    img[body] = (0, 200, 255, 255)
    edge = body & (np.abs(ny) > (0.1 + 0.45 * (1 - nx)) - 0.12)
    img[edge] = (0, 90, 160, 255)
    cockpit = ((nx - 0.05) / 0.3) ** 2 + (ny / 0.25) ** 2 < 1
    img[cockpit & body] = (230, 255, 255, 255)
    thruster = (nx < -0.85) & (np.abs(ny) < 0.35)
    img[thruster] = (255, 140, 0, 255)
    return img


def make_packet(s=32):
    """Pacote de dados: caixa dourada com miolo verde."""
    img = np.zeros((s, s, 4), np.uint8)
    img[:] = (255, 200, 0, 255)
    img[4:-4, 4:-4] = (30, 230, 130, 255)
    ys, xs = np.mgrid[0:s, 0:s]
    img[(np.abs(xs - ys) < 2) & (xs > 4) & (xs < s - 4)] = (255, 255, 255, 255)
    return img


def make_obstacle(s=64):
    """Drone corrompido / meteoro cibernético com espinhos."""
    ys, xs = np.mgrid[0:s, 0:s]
    nx = xs / (s - 1) * 2 - 1
    ny = ys / (s - 1) * 2 - 1
    r = np.hypot(nx, ny)
    th = np.arctan2(ny, nx)
    limit = 0.7 + 0.3 * (np.cos(8 * th) > 0)
    img = np.zeros((s, s, 4), np.uint8)
    body = r < limit
    img[body] = (200, 30, 80, 255)
    img[body & (r < 0.45)] = (90, 0, 40, 255)
    img[body & (r < 0.15)] = (255, 60, 255, 255)
    glitch = body & (ys % 8 == 0)
    img[glitch] = (255, 120, 160, 255)
    return img
