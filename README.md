# Cyber Delivery: Entrega no Setor 404 (PyOpenGL)

Jogo 2D de rolagem lateral: um drone coleta pacotes de dados e desvia de obstáculos cibernéticos.

**Equipe:** Eduardo, Mayk, Thomas  

## Instalação e execução
```
pip install PyOpenGL glfw numpy pillow
python main.py
```
Requer OpenGL 3.3+. (Opcional: `python make_assets.py` regenera as imagens de `assets/`.)

## Controles
- **ESPAÇO**: iniciar · **W/S ou ↑/↓**: mover o drone · **R**: reiniciar (Game Over/Vitória) · **ESC**: sair

## Regras
Comece com 3 vidas. Pacotes dão +50 pontos; sobreviver dá 10 pontos por segundo. Bater num obstáculo tira 1 vida (com 1,5 s de invulnerabilidade). **Vitória:** 1000 pontos. **Derrota:** 0 vidas.

## Estrutura
| Arquivo | Conteúdo |
|---|---|
| `main.py` | Janela GLFW, contexto OpenGL 3.3 core, laço principal com Delta Time |
| `game.py` | Máquina de estados (Menu, Jogando, Game Over, Vitória), spawn, colisões, HUD |
| `controls.py` | Entrada do usuário (teclado) |
| `game_object.py` | Entidade com VAO/VBO próprios, matrizes Model/Ortho, colisão AABB |
| `shader.py` | Carrega/compila/liga os shaders e define uniforms |
| `shaders/vertex.vert`, `shaders/fragment.frag` | Código GLSL |
| `texture.py` | Criação de texturas OpenGL (+ geradores das imagens) |
| `assets/*.png` | Texturas usadas no jogo |

## Desafio gráfico adicional: efeito parallax
O fundo tem 3 camadas (`PARALLAX` em `game.py`): nebulosa (25 px/s), estrelas (80 px/s) e grade (220 px/s). Cada camada é um quad de tela cheia com textura `GL_REPEAT`; a cada frame `uv_offset` avança conforme a velocidade da camada (`Game.update`), e o vertex shader soma esse deslocamento às coordenadas de textura. Camadas mais próximas rolam mais rápido, criando sensação de profundidade.

## Onde está cada requisito
| Req. | Local |
|---|---|
| R01 Primitivas/vértices | `game_object.py` → `QUAD` (2 triângulos, `GL_TRIANGLES`) |
| R02 VAO/VBO | `game_object.py` → `_init_gl()` |
| R03 Shaders | `shaders/*.vert/.frag`, `shader.py`; tint/glow ao sofrer dano em `game.py::_update_player` |
| R04 Transformações | `game_object.py::model_matrix`; inclinação do drone, rotação e pulso dos pacotes em `game.py` |
| R05 Projeção ortográfica | `game_object.py::ortho` (0–800 × 0–600) |
| R06 Texturas | `texture.py::Texture`, carregadas de `assets/` em `game.py::__init__` |
| R07 Animação | Camadas do fundo via `uv_offset`; pacotes girando/pulsando por Delta Time |
| R08 Tela inicial | `game.py::render` (estado `MENU`) |
| R09 Controle | `controls.py` |
| R10 Comportamentos | `game.py::_update_player`, `_spawn`, `_update_entities` |
| R11 Colisão AABB | `game_object.py::collides` · `game.py::_collisions` |
| R12 Pontuação e vidas | `game.py::score`, HUD em `render` |
| R13 Fim de jogo | Vidas = 0 → Game Over; 1000 pontos → Vitória |
| R14 Reinício | `game.py::reset` |
| R15 Modularização | arquivos da tabela "Estrutura" |
| R17 Identificação | comentários `[OpenGL]` e `R0x` no código |

## Créditos e licenças
Todas as imagens em `assets/` foram geradas por código (`texture.py`/`make_assets.py`); nenhum recurso externo é usado. Fonte do texto: DejaVu Sans (se disponível no sistema) via Pillow.
