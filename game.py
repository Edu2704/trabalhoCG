"""Game.py equivalente: máquina de estados + laço de atualização/renderização."""
import math
import os
import random
import glfw
from OpenGL.GL import *

from shader import Shader
from texture import Texture
from game_object import GameObject, ortho
from controls import Controls, START, RESTART, QUIT

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

WIDTH, HEIGHT = 800, 600
MAX_LIVES = 3
WIN_SCORE = 1000                     # R13: pontuação-alvo
TEAM = "Equipe: Eduardo, Mayk, Thomas" 

# Desafio adicional: EFEITO PARALLAX -> (textura, tamanho do tile em px, velocidade em px/s)
# camadas mais distantes rolam mais devagar que as mais próximas.
PARALLAX = [("space", 256, 25), ("stars", 256, 80), ("grid", 128, 220)]

MENU, PLAYING, GAME_OVER, WIN = range(4)


class Game:
    def __init__(self, window):
        self.window = window
        self.controls = Controls(window)
        self.state = MENU
        self.time = 0.0

        glEnable(GL_BLEND)                                   # [OpenGL] transparência
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.02, 0.02, 0.08, 1.0)

        self.shader = Shader()
        self.projection = ortho(0, WIDTH, 0, HEIGHT)         # R05
        self.view = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

        # R06: texturas carregadas de assets/*.png (Pillow -> glTexImage2D)
        tex = lambda name, **kw: Texture.from_file(os.path.join(ASSETS, name + ".png"), **kw)
        self.tex_drone = tex("drone")
        self.tex_packet = tex("packet", smooth=False)
        self.tex_obstacle = tex("obstacle")

        # Desafio adicional - EFEITO PARALLAX: uma camada de fundo (quad de tela cheia) por entrada
        self.layers = []
        for name, tile, speed in PARALLAX:
            layer = GameObject(WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT,
                               tex(name, wrap=GL_REPEAT, smooth=False))
            layer.uv_scale = (WIDTH / tile, HEIGHT / tile)
            layer.tile, layer.speed = tile, speed
            self.layers.append(layer)
        self.player = GameObject(100, HEIGHT / 2, 64, 32, self.tex_drone, hitbox=0.8)
        self.text_quad = GameObject(0, 0, 1, 1)              # quad reutilizado p/ texto
        self.text_cache = {}

        self.obstacles, self.packets = [], []
        self.reset()

    # ---------- R14: reinício completo ----------
    def reset(self):
        for o in self.obstacles + self.packets:
            o.destroy()
        self.obstacles, self.packets = [], []
        self.lives = MAX_LIVES
        self.survival = 0.0
        self.collected = 0
        self.invuln = 0.0
        self.spawn_obs_t = 1.0
        self.spawn_pkt_t = 2.0
        self.player.x, self.player.y = 100, HEIGHT / 2
        self.player.angle = 0.0

    @property
    def score(self):
        return int(self.survival * 10) + self.collected * 50

    # ---------- entrada ----------
    def on_key(self, key, action):
        act = self.controls.action_for(key, action)
        if act == QUIT:
            glfw.set_window_should_close(self.window, True)
        elif act == START and self.state == MENU:            # R08
            self.reset()
            self.state = PLAYING
        elif act == RESTART and self.state in (GAME_OVER, WIN):   # R14
            self.reset()
            self.state = PLAYING

    # ---------- atualização ----------
    def update(self, dt):
        self.time += dt
        # R07 + parallax: cada camada rola numa velocidade (translação contínua das coords. de textura)
        boost = 1.0 if self.state == PLAYING else 0.4
        for layer in self.layers:
            u, v = layer.uv_offset
            layer.uv_offset = ((u + layer.speed * boost * dt / layer.tile) % 1.0, v)

        if self.state == MENU:
            self.player.y = HEIGHT / 2 - 40 + math.sin(self.time * 2) * 10
            self.player.x = WIDTH / 2
            return
        if self.state != PLAYING:
            return

        self.survival += dt
        self._update_player(dt)
        self._spawn(dt)
        self._update_entities(dt)
        self._collisions()

        if self.lives <= 0:
            self.state = GAME_OVER                            # R13 derrota
        elif self.score >= WIN_SCORE:
            self.state = WIN                                  # R13 vitória

    def _update_player(self, dt):
        p = self.player
        dy = self.controls.vertical_axis()                    # R09
        p.y += dy * 350 * dt
        p.y = max(p.h / 2, min(HEIGHT - p.h / 2, p.y))        # R10: limites da tela
        p.angle += (dy * 15 - p.angle) * min(1.0, 10 * dt)    # R04: inclinação suave

        if self.invuln > 0:
            self.invuln -= dt
            blink = 0.5 + 0.5 * math.sin(self.time * 30)
            p.tint = (1.0, 0.3 + 0.7 * blink, 0.3 + 0.7 * blink, 1.0)   # R03: cor ao sofrer dano
            p.glow = 0.3 * blink
        else:
            p.tint, p.glow = (1, 1, 1, 1), 0.0

    def _spawn(self, dt):
        difficulty = min(1.0, self.survival / 60)
        self.spawn_obs_t -= dt
        if self.spawn_obs_t <= 0:
            o = GameObject(WIDTH + 40, random.uniform(40, HEIGHT - 40), 48, 48,
                           self.tex_obstacle, hitbox=0.7)
            o.vx = -random.uniform(250, 350) * (1 + difficulty)   # R10: velocidades variadas
            self.obstacles.append(o)
            self.spawn_obs_t = random.uniform(0.5, 1.1) * (1.0 - 0.4 * difficulty)
        self.spawn_pkt_t -= dt
        if self.spawn_pkt_t <= 0:
            k = GameObject(WIDTH + 40, random.uniform(40, HEIGHT - 40), 28, 28, self.tex_packet)
            k.vx = -220
            self.packets.append(k)
            self.spawn_pkt_t = random.uniform(1.5, 2.5)

    def _update_entities(self, dt):
        for o in self.obstacles:
            o.x += o.vx * dt
            o.angle += 60 * dt
        for k in self.packets:
            k.x += k.vx * dt
            k.angle += 120 * dt                               # R04: rotação em Z
            k.scale = 1.0 + 0.2 * math.sin(self.time * 6)     # R04: escala pulsante
            k.glow = 0.2 + 0.2 * math.sin(self.time * 6)
        for lst in (self.obstacles, self.packets):
            for e in [e for e in lst if e.x < -60]:
                e.destroy()
                lst.remove(e)

    def _collisions(self):                                    # R11
        for k in list(self.packets):
            if self.player.collides(k):
                self.collected += 1
                k.destroy()
                self.packets.remove(k)
        if self.invuln > 0:
            return
        for o in list(self.obstacles):
            if self.player.collides(o):
                self.lives -= 1
                self.invuln = 1.5
                o.destroy()
                self.obstacles.remove(o)
                break

    # ---------- renderização ----------
    def render(self, fb_w, fb_h):
        glViewport(0, 0, fb_w, fb_h)
        glClear(GL_COLOR_BUFFER_BIT)
        self.shader.use()
        self.shader.set_mat4("uProjection", self.projection)
        self.shader.set_mat4("uView", self.view)
        self.shader.set_int("uTex", 0)

        for layer in self.layers:                             # parallax: do fundo para a frente
            layer.draw(self.shader)
        if self.state in (PLAYING, GAME_OVER, WIN):
            for k in self.packets:
                k.draw(self.shader)
            for o in self.obstacles:
                o.draw(self.shader)
        self.player.draw(self.shader)

        if self.state == MENU:
            self._text("CYBER DELIVERY", 56, WIDTH / 2, 480, (0, 220, 255))
            self._text("Entrega no Setor 404", 28, WIDTH / 2, 425, (255, 255, 255))
            self._text(TEAM, 20, WIDTH / 2, 160, (200, 200, 200))
            self._text("Pressione ESPAÇO para Iniciar", 28, WIDTH / 2, 100, (255, 220, 0))
        else:
            self._text(f"Pontos: {self.score}", 24, 90, HEIGHT - 25, (255, 255, 255))
            self._text(f"Vidas: {max(self.lives, 0)}", 24, WIDTH - 70, HEIGHT - 25, (255, 100, 100))
            if self.state == GAME_OVER:
                self._text("GAME OVER", 64, WIDTH / 2, 330, (255, 60, 80))
                self._text("Pressione R para reiniciar", 28, WIDTH / 2, 270, (255, 255, 255))
            elif self.state == WIN:
                self._text("VITÓRIA! Entrega concluída", 48, WIDTH / 2, 330, (60, 255, 140))
                self._text("Pressione R para reiniciar", 28, WIDTH / 2, 270, (255, 255, 255))

    def _text(self, text, size, x, y, color):
        key = (text, size, color)
        if key not in self.text_cache:
            if len(self.text_cache) > 150:                    # evita crescer sem limite
                for t in self.text_cache.values():
                    t.delete()
                self.text_cache.clear()
            self.text_cache[key] = Texture.from_text(text, size, color)
        tex = self.text_cache[key]
        q = self.text_quad
        q.texture, q.x, q.y, q.w, q.h = tex, x, y, tex.width, tex.height
        q.draw(self.shader)
