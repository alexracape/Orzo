#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texture;

uniform mat4 m_proj;
uniform mat4 m_model;
uniform mat4 m_cam;

out vec3 frag_normal;
out vec3 frag_position;
out vec2 frag_texcoord;

void main() {
    gl_Position = m_proj * m_cam * m_model * vec4(in_position, 1.0);
    frag_normal = mat3(m_model) * in_normal;  // Transform normal by model matrix
    frag_position = vec3(m_model * vec4(in_position, 1.0));  // Transform position
    frag_texcoord = in_texture;  // Pass texture coordinates through
}
