"""main.py: janela (GLFW) + contexto OpenGL 3.3 core + laço principal."""
import sys
import glfw
from game import Game, WIDTH, HEIGHT


def main():
    if not glfw.init():
        sys.exit("Falha ao inicializar o GLFW")
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)        # necessário no macOS
    glfw.window_hint(glfw.RESIZABLE, False)

    window = glfw.create_window(WIDTH, HEIGHT, "Cyber Delivery: Entrega no Setor 404", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar a janela")
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    game = Game(window)
    glfw.set_key_callback(window, lambda w, key, sc, action, mods: game.on_key(key, action))

    last = glfw.get_time()
    while not glfw.window_should_close(window):
        now = glfw.get_time()
        dt = min(now - last, 0.05)       # Delta Time (limitado para evitar saltos)
        last = now

        glfw.poll_events()
        game.update(dt)
        fb_w, fb_h = glfw.get_framebuffer_size(window)
        game.render(fb_w, fb_h)
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
