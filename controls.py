"""Entrada do usuário (R09), separada da lógica do jogo (R15)."""
import glfw

START, RESTART, QUIT = "start", "restart", "quit"


class Controls:
    def __init__(self, window):
        self.window = window

    def vertical_axis(self):
        """+1 = cima (W / seta ↑), -1 = baixo (S / seta ↓), 0 = parado."""
        up = self._pressed(glfw.KEY_W, glfw.KEY_UP)
        down = self._pressed(glfw.KEY_S, glfw.KEY_DOWN)
        return int(up) - int(down)

    def action_for(self, key, action):
        """Traduz um evento de tecla em uma ação do jogo (ou None)."""
        if action != glfw.PRESS:
            return None
        return {glfw.KEY_SPACE: START, glfw.KEY_R: RESTART, glfw.KEY_ESCAPE: QUIT}.get(key)

    def _pressed(self, *keys):
        return any(glfw.get_key(self.window, k) == glfw.PRESS for k in keys)
