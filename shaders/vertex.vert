#version 330 core
// R03 - Vertex Shader: aplica Model/View/Projection e repassa as coordenadas de textura
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUV;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;
uniform vec2 uUVScale;    // repete a textura (camadas de fundo)
uniform vec2 uUVOffset;   // rola a textura (R07 / parallax)

out vec2 vUV;

void main() {
    gl_Position = uProjection * uView * uModel * vec4(aPos, 0.0, 1.0);
    vUV = aUV * uUVScale + uUVOffset;
}
