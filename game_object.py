"""GameObject.py equivalente (R01, R02, R04, R11): entidade com VAO/VBO próprio."""
import ctypes
import numpy as np
from OpenGL.GL import *


def ortho(l, r, b, t, n=-1.0, f=1.0):
    """R05: projeção ortográfica (equivalente a glm::ortho)."""
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (t - b), 0, -(t + b) / (t - b)],
        [0, 0, -2 / (f - n), -(f + n) / (f - n)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


def model_matrix(x, y, w, h, angle_deg):
    """R04: Model = Translação * Rotação(Z) * Escala."""
    a = np.radians(angle_deg)
    c, s = np.cos(a), np.sin(a)
    T = np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    R = np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    S = np.array([[w, 0, 0, 0], [0, h, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    return T @ R @ S


# R01: quad centrado na origem = 2 triângulos (GL_TRIANGLES), cada vértice = (x, y, u, v)
QUAD = np.array([
    -0.5, -0.5, 0.0, 0.0,
     0.5, -0.5, 1.0, 0.0,
     0.5,  0.5, 1.0, 1.0,
    -0.5, -0.5, 0.0, 0.0,
     0.5,  0.5, 1.0, 1.0,
    -0.5,  0.5, 0.0, 1.0,
], dtype=np.float32)


class GameObject:
    def __init__(self, x, y, w, h, texture=None, hitbox=1.0):
        self.x, self.y = x, y          # centro do objeto (coordenadas do mundo 800x600)
        self.w, self.h = w, h
        self.angle = 0.0               # graus
        self.scale = 1.0
        self.texture = texture
        self.hitbox = hitbox           # fração do tamanho usada na colisão
        self.tint = (1.0, 1.0, 1.0, 1.0)
        self.glow = 0.0
        self.uv_scale = (1.0, 1.0)
        self.uv_offset = (0.0, 0.0)
        self.vx = 0.0                  # velocidade (px/s)
        self.vy = 0.0
        self._init_gl()

    # ---------- R02: VAO + VBO próprios ----------
    def _init_gl(self):
        self.vao = glGenVertexArrays(1)                      # [OpenGL] glGenVertexArrays
        self.vbo = glGenBuffers(1)                           # [OpenGL] glGenBuffers
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, QUAD.nbytes, QUAD, GL_STATIC_DRAW)
        stride = 4 * 4
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))   # posição
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))   # textura
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])

    # ---------- desenho ----------
    def draw(self, shader):
        shader.set_mat4("uModel", model_matrix(self.x, self.y, self.w * self.scale,
                                               self.h * self.scale, self.angle))
        shader.set_vec2("uUVScale", *self.uv_scale)
        shader.set_vec2("uUVOffset", *self.uv_offset)
        shader.set_vec4("uTint", *self.tint)
        shader.set_float("uGlow", self.glow)
        if self.texture:
            self.texture.bind(0)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)                     # [OpenGL] glDrawArrays
        glBindVertexArray(0)

    # ---------- R11: colisão AABB ----------
    def aabb(self):
        hw = self.w * self.scale * self.hitbox / 2
        hh = self.h * self.scale * self.hitbox / 2
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def collides(self, other):
        a, b = self.aabb(), other.aabb()
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
