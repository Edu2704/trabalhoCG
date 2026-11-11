#version 330 core
// R03 - Fragment Shader: amostra a textura, aplica cor base (tint) e brilho dinâmico
in vec2 vUV;

uniform sampler2D uTex;
uniform vec4 uTint;    // cor base (ex.: vermelho ao sofrer dano)
uniform float uGlow;   // brilho extra

out vec4 FragColor;

void main() {
    vec4 c = texture(uTex, vUV);
    vec3 rgb = c.rgb * uTint.rgb + c.rgb * uGlow;
    FragColor = vec4(rgb, c.a * uTint.a);
}
