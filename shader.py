"""Shader.py equivalente (R03): compilação e uso dos shaders GLSL (arquivos em shaders/)."""
import os
import numpy as np
from OpenGL.GL import *

SHADER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shaders")


def _read(name):
    with open(os.path.join(SHADER_DIR, name), encoding="utf-8") as f:
        return f.read()


class Shader:
    def __init__(self, vertex_file="vertex.vert", fragment_file="fragment.frag"):
        vertex_src, fragment_src = _read(vertex_file), _read(fragment_file)
        vs = self._compile(vertex_src, GL_VERTEX_SHADER)
        fs = self._compile(fragment_src, GL_FRAGMENT_SHADER)
        self.program = glCreateProgram()           # [OpenGL] criação do programa
        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(self.program).decode())
        glDeleteShader(vs)
        glDeleteShader(fs)
        self._locs = {}

    @staticmethod
    def _compile(src, kind):
        sh = glCreateShader(kind)
        glShaderSource(sh, src)
        glCompileShader(sh)
        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(sh).decode())
        return sh

    def use(self):
        glUseProgram(self.program)                 # [OpenGL] glUseProgram

    def _loc(self, name):
        if name not in self._locs:
            self._locs[name] = glGetUniformLocation(self.program, name)
        return self._locs[name]

    def set_mat4(self, name, m):
        # matrizes em numpy são row-major -> transpose=GL_TRUE
        glUniformMatrix4fv(self._loc(name), 1, GL_TRUE, np.ascontiguousarray(m, dtype=np.float32))

    def set_vec2(self, name, x, y):
        glUniform2f(self._loc(name), x, y)

    def set_vec4(self, name, r, g, b, a):
        glUniform4f(self._loc(name), r, g, b, a)

    def set_float(self, name, v):
        glUniform1f(self._loc(name), v)

    def set_int(self, name, v):
        glUniform1i(self._loc(name), v)
