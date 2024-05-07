#version 330

in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_model;
uniform mat4 m_cam;

void main() {
    gl_Position = m_proj * m_cam * m_model * vec4(in_position, 1.0);
}